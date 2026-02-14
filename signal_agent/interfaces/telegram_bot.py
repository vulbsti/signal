"""Telegram bot interface — bridges Telegram messages to the ADK backend API."""

import asyncio
import json
import logging

import httpx
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from signal_agent.config import TELEGRAM_BOT_TOKEN, ADK_BASE_URL, ADK_APP_NAME
from signal_agent.tools.browser_tools import login_to_platform

logger = logging.getLogger(__name__)

# Shared async HTTP client — created once, reused across requests
_http: httpx.AsyncClient | None = None


def _client() -> httpx.AsyncClient:
    global _http
    if _http is None or _http.is_closed:
        _http = httpx.AsyncClient(base_url=ADK_BASE_URL, timeout=120.0)
    return _http


async def _ensure_session(user_id: int) -> str:
    """Ensure an ADK session exists for this Telegram user, creating one if needed."""
    session_id = f"telegram_{user_id}"
    user_id_str = str(user_id)
    client = _client()

    # Check if session exists
    resp = await client.get(
        f"/apps/{ADK_APP_NAME}/users/{user_id_str}/sessions/{session_id}"
    )
    if resp.status_code == 404:
        # Create session
        await client.post(
            f"/apps/{ADK_APP_NAME}/users/{user_id_str}/sessions",
            json={"session_id": session_id},
        )
    return session_id


async def _run_agent(user_id: int, message: str) -> str:
    """Send a message to the ADK agent via HTTP API and collect the response."""
    try:
        session_id = await _ensure_session(user_id)
    except httpx.ConnectError:
        return f"Cannot connect to ADK backend at {ADK_BASE_URL}. Is it running? Start with: adk web --port 3030 ."
    except Exception as e:
        return f"Session error: {e}"

    client = _client()

    try:
        resp = await client.post(
            "/run",
            json={
                "app_name": ADK_APP_NAME,
                "user_id": str(user_id),
                "session_id": session_id,
                "new_message": {
                    "role": "user",
                    "parts": [{"text": message}],
                },
            },
        )
        resp.raise_for_status()
    except httpx.ConnectError:
        return f"Cannot connect to ADK backend at {ADK_BASE_URL}. Is it running? Start with: adk web --port 3030 ."
    except httpx.HTTPStatusError as e:
        return f"ADK backend error: {e.response.status_code} — {e.response.text[:200]}"
    except Exception as e:
        return f"Request failed: {e}"

    events = resp.json()

    # Extract text from agent response events
    response_parts = []
    for event in events:
        content = event.get("content")
        if not content or not content.get("parts"):
            continue
        for part in content["parts"]:
            text = part.get("text")
            thought = part.get("thought")
            if text and not thought:
                response_parts.append(text)

    return "\n".join(response_parts) if response_parts else "No response from agent."


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "Hey! I'm Signal, your personal noise reducer.\n\n"
        "Commands:\n"
        "/digest — Get your filtered content digest\n"
        "/voice — Get your digest as a voice briefing\n"
        "/login [platform] — Log in to a platform (instagram/x)\n"
        "/curate [platform] — Curate your social feed (instagram/x)\n"
        "/preferences — View your preferences\n"
        "/history — View your history\n\n"
        "Or just type anything to chat with me."
    )


async def cmd_digest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /digest command."""
    await update.message.reply_text("Fetching your digest... this takes a moment.")
    response = await _run_agent(update.effective_user.id, "Give me my digest")
    for chunk in _split_message(response):
        await _send(update.message, chunk)


async def cmd_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /voice command — digest as audio briefing."""
    await update.message.reply_text("Generating your digest and voice briefing...")
    digest_text = await _run_agent(update.effective_user.id, "Give me my digest")

    try:
        from signal_agent.interfaces.live_voice import generate_voice_briefing

        wav_path = await generate_voice_briefing(digest_text)
        await update.message.reply_voice(voice=open(wav_path, "rb"))
    except Exception as e:
        logger.error("Voice briefing failed: %s", e)
        await update.message.reply_text("Voice generation failed. Here's the text digest:")
        for chunk in _split_message(digest_text):
            await _send(update.message, chunk)


async def cmd_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /login command — open browser directly for manual login."""
    args = context.args
    platform = args[0] if args else "instagram"
    try:
        await update.message.reply_text(
            f"Opening {platform} in a browser window.\n"
            f"Please log in manually — you have 5 minutes.\n"
            f"The window will close automatically after login is detected."
        )
    except Exception:
        pass  # Transient Telegram network error, continue anyway

    try:
        result_json = await login_to_platform(platform)
        result = json.loads(result_json)
        status = result.get("status", "unknown")

        if status == "already_logged_in":
            msg = f"You're already logged in to {platform}! Run /curate {platform} to start."
        elif status == "logged_in":
            msg = f"Login to {platform} detected! Run /curate {platform} to start."
        elif status == "timeout":
            msg = f"Login timed out after 5 minutes. Run /login {platform} to try again."
        else:
            msg = f"Login status: {status}"

        await _send(update.message, msg)
    except Exception as e:
        logger.exception("Login failed")
        await _send(update.message, f"Login failed: {e}")


async def cmd_curate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /curate command."""
    args = context.args
    platform = args[0] if args else "instagram"
    await update.message.reply_text(f"Starting {platform} feed curation...")
    response = await _run_agent(
        update.effective_user.id, f"Curate my {platform} feed"
    )
    for chunk in _split_message(response):
        await _send(update.message, chunk)


async def cmd_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /preferences command."""
    response = await _run_agent(update.effective_user.id, "Show my preferences")
    for chunk in _split_message(response):
        await _send(update.message, chunk)


async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command."""
    response = await _run_agent(update.effective_user.id, "Show my history")
    for chunk in _split_message(response):
        await _send(update.message, chunk)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free-form text messages."""
    response = await _run_agent(update.effective_user.id, update.message.text)
    for chunk in _split_message(response):
        await _send(update.message, chunk)


async def _send(message, text: str):
    """Send a message, trying Markdown first and falling back to plain text."""
    try:
        await message.reply_text(text, parse_mode="Markdown")
    except Exception:
        await message.reply_text(text)


def _split_message(text: str, limit: int = 4000) -> list[str]:
    """Split a message into chunks that fit Telegram's character limit."""
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


def main():
    """Start the Telegram bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set in .env")
        return

    print(f"Connecting to ADK backend at {ADK_BASE_URL}")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("digest", cmd_digest))
    app.add_handler(CommandHandler("voice", cmd_voice))
    app.add_handler(CommandHandler("login", cmd_login))
    app.add_handler(CommandHandler("curate", cmd_curate))
    app.add_handler(CommandHandler("preferences", cmd_preferences))
    app.add_handler(CommandHandler("history", cmd_history))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting Signal Telegram bot...")
    app.run_polling()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
