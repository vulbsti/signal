"""Telegram bot interface — bridges Telegram messages to the ADK root agent."""

import asyncio
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from google.adk.runners import InMemoryRunner
from google.genai import types

from signal_agent.agent import root_agent
from signal_agent.config import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)

# ADK runner — manages sessions and agent execution
runner = InMemoryRunner(agent=root_agent, app_name="signal_bot")

# Map Telegram user IDs to ADK session IDs
_user_sessions: dict[int, str] = {}


def _session_id(user_id: int) -> str:
    """Get or create an ADK session ID for a Telegram user."""
    if user_id not in _user_sessions:
        _user_sessions[user_id] = f"telegram_{user_id}"
    return _user_sessions[user_id]


async def _ensure_session(user_id: int) -> str:
    """Ensure an ADK session exists for this Telegram user, creating one if needed."""
    session_id = _session_id(user_id)
    user_id_str = str(user_id)

    # Check if session already exists
    session = await runner.session_service.get_session(
        app_name="signal_bot", user_id=user_id_str, session_id=session_id
    )
    if not session:
        session = await runner.session_service.create_session(
            app_name="signal_bot", user_id=user_id_str, session_id=session_id
        )
    return session_id


async def _run_agent(user_id: int, message: str) -> str:
    """Send a message to the ADK agent and collect the response."""
    session_id = await _ensure_session(user_id)

    content = types.Content(
        role="user",
        parts=[types.Part(text=message)],
    )

    response_parts = []
    async for event in runner.run_async(
        user_id=str(user_id),
        session_id=session_id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text and not getattr(part, "thought", False):
                    response_parts.append(part.text)

    return "\n".join(response_parts) if response_parts else "No response from agent."


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "Hey! I'm Signal, your personal noise reducer.\n\n"
        "Commands:\n"
        "/digest — Get your filtered content digest\n"
        "/curate [platform] — Curate your social feed (instagram/x)\n"
        "/preferences — View your preferences\n"
        "/history — View your history\n\n"
        "Or just type anything to chat with me."
    )


async def cmd_digest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /digest command."""
    await update.message.reply_text("Fetching your digest... this takes a moment.")
    response = await _run_agent(update.effective_user.id, "Give me my digest")
    # Split long messages (Telegram has a 4096 char limit)
    for chunk in _split_message(response):
        await _send(update.message, chunk)


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
        # Find a good break point
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

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("digest", cmd_digest))
    app.add_handler(CommandHandler("curate", cmd_curate))
    app.add_handler(CommandHandler("preferences", cmd_preferences))
    app.add_handler(CommandHandler("history", cmd_history))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting Signal Telegram bot...")
    app.run_polling()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
