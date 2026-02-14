"""ADK tool wrapper for browser-use feed curation sessions."""

import asyncio
import json
import logging
import os

from browser_use import Agent as BUAgent, Browser, BrowserProfile, ChatOpenAI

from signal_agent.browser.controller import BrowserController
from signal_agent.memory.manager import read_memory

logger = logging.getLogger(__name__)

# Persistent profile path — shared between login (Playwright) and curation (browser-use)
_EDGE_PROFILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "browser", ".edge_profile")

PLATFORM_URLS = {
    "instagram": "https://www.instagram.com/",
    "x": "https://x.com/home",
}


def _get_llm():
    """Create a ChatOpenAI instance pointing at the LiteLLM proxy."""
    return ChatOpenAI(
        model="gemini-3-flash-preview",
        api_key=os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY"),
        base_url=(os.getenv("OPENAI_BASE_URL") or os.getenv("GOOGLE_GEMINI_BASE_URL", "")) + "/v1",
        temperature=0.2,
    )


def _get_browser_profile():
    """Create a BrowserProfile using Edge with the persistent login profile."""
    return BrowserProfile(
        channel="msedge",
        user_data_dir=_EDGE_PROFILE,
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )


CURATION_TASK_TEMPLATE = """\
Go to {url} and curate my feed. Process approximately {post_count} posts.

For EACH post visible on screen:
1. Read and understand the post content (text, image topic, author)
2. Decide one action:
   - LIKE: If the post matches my interests (see preferences below). Click the heart/like button.
   - SKIP: If neutral or not relevant. Just scroll past.
   - MUTE: If it's rage bait, outrage-driven, or low quality. Click the three-dot menu and select "Not interested" or "Mute".
3. Scroll down to the next post.
4. Repeat.

After processing all posts, provide a summary of what you did.

## My Preferences
{preferences}

## De-Radicalization Rules
- If you see 5+ posts in a row with the same political/ideological lean, actively seek diverse content
- Skip inflammatory or outrage-driven content — never like or engage with rage bait
- Prefer substantive, informative content over engagement bait
- When in doubt, skip rather than engage

## Current Feed State
{feed_state}
"""


async def curate_feed(platform: str = "instagram", post_count: int = 10) -> str:
    """Open a social media platform and curate the feed using AI browser automation.

    Uses browser-use to physically operate the browser — scrolling through posts,
    liking quality content, skipping noise, and muting rage bait accounts.

    Args:
        platform: Which platform to curate ('instagram' or 'x').
        post_count: How many posts to process (default 10).

    Returns:
        JSON string with session summary and actions taken.
    """
    preferences = read_memory("preferences.md")
    feed_state = read_memory("feed_state.md")
    url = PLATFORM_URLS.get(platform.lower(), PLATFORM_URLS["instagram"])

    task = CURATION_TASK_TEMPLATE.format(
        url=url,
        post_count=post_count,
        preferences=preferences,
        feed_state=feed_state,
    )

    llm = _get_llm()
    browser = Browser(browser_profile=_get_browser_profile())

    agent = BUAgent(
        task=task,
        llm=llm,
        browser=browser,
        use_vision=True,
        max_actions_per_step=3,
        max_failures=3,
    )

    try:
        result = await agent.run(max_steps=post_count * 3)
        final = result.final_result() if result.final_result() else "Curation completed."

        # Check for login issues
        if any(kw in final.lower() for kw in ["log in", "login", "sign in", "not logged"]):
            return json.dumps({
                "platform": platform,
                "error": "not_logged_in",
                "message": f"Not logged in to {platform}. Use /login {platform} to log in first.",
            }, indent=2)

        # Collect actions from history
        actions = []
        for output in result.all_model_outputs:
            if isinstance(output, dict):
                actions.append(output)

        return json.dumps({
            "platform": platform,
            "posts_targeted": post_count,
            "actions_taken": len(actions),
            "summary": final,
        }, indent=2)

    except Exception as e:
        logger.exception("Feed curation failed")
        return json.dumps({
            "platform": platform,
            "error": str(e),
        }, indent=2)


async def _has_login_form(page) -> bool:
    """Check if the page has a login/password form (meaning user is NOT logged in)."""
    password_field = await page.query_selector('input[type="password"]')
    return password_field is not None


async def login_to_platform(platform: str = "instagram") -> str:
    """Open a browser to a platform so the user can log in manually.
    Keeps the browser open for up to 5 minutes, polling every 5 seconds
    until the login form disappears (meaning login succeeded).

    Args:
        platform: Which platform to log in to ('instagram' or 'x').

    Returns:
        Status message.
    """
    start_url = PLATFORM_URLS.get(platform.lower(), PLATFORM_URLS["instagram"])
    controller = BrowserController()

    try:
        page = await controller.start()
        await page.goto(start_url, wait_until="domcontentloaded")
        await asyncio.sleep(5)

        if not await _has_login_form(page):
            logger.info("Already logged in at: %s", page.url)
            return json.dumps({"status": "already_logged_in", "platform": platform, "url": page.url})

        logger.info("Login form detected at %s — waiting up to 5 min for user to log in...", start_url)

        for i in range(60):
            await asyncio.sleep(5)
            if not await _has_login_form(page):
                logger.info("Login succeeded! Now at: %s", page.url)
                await asyncio.sleep(3)
                return json.dumps({"status": "logged_in", "platform": platform, "url": page.url})
            if i % 12 == 11:
                logger.info("Still waiting for login... (%d/300 seconds)", (i + 1) * 5)

        return json.dumps({
            "status": "timeout",
            "platform": platform,
            "message": "Login window timed out after 5 minutes. Try /login again.",
        })
    finally:
        await controller.stop()
