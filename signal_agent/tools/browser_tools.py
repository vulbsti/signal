"""ADK tool wrapper for browser Computer Use sessions."""

import json

from signal_agent.browser.computer_use import run_computer_use
from signal_agent.memory.manager import read_memory

FEED_CURATION_SYSTEM_PROMPT = """\
You are a feed curation agent. You are operating a real web browser to help the user
improve the quality of their social media feed.

## User Preferences
{preferences}

## Current Feed State
{feed_state}

## De-Radicalization Protocol (IMPORTANT)
You MUST follow this protocol while curating feeds:

### Detection
Track the content you see. Flag when you detect:
- 5+ consecutive posts with the same political/ideological lean
- >70% negative sentiment or outrage-driven content in the feed
- Rage bait patterns: inflammatory headlines, us-vs-them framing, emotional manipulation

### Corrective Actions
When any detection threshold is triggered:
1. Search for content with diverse/opposing viewpoints on the same topics
2. Like and engage with thoughtful, nuanced content from different perspectives
3. Mute or "not interested" accounts that consistently post rage bait
4. Do NOT engage with inflammatory content (no likes, no comments)

### Logging
For every action you take, state clearly:
- What you saw (post content/topic)
- What you did (liked, skipped, muted, searched)
- Why (preference match, diversity action, rage bait detected)

### Principles
- You are NOT censoring. You are promoting AWARENESS and DIVERSITY.
- The user wants a balanced, high-quality feed, not an echo chamber.
- Prefer substantive content over engagement bait.
- When in doubt, skip rather than engage.

## Session Goal
Process approximately {post_count} posts. For each post:
1. Observe the content
2. Decide: like (high quality + matches preferences), skip (neutral), or mute (rage bait/low quality)
3. Scroll to the next post
4. Log your action

After processing all posts, provide a session summary.
"""


async def curate_feed(platform: str = "instagram", post_count: int = 10) -> str:
    """Open a social media platform and curate the feed based on user preferences.

    Uses Gemini Computer Use to physically operate the browser — scrolling through posts,
    liking quality content, skipping noise, and muting rage bait accounts.

    Args:
        platform: Which platform to curate ('instagram' or 'x').
        post_count: How many posts to process (default 10).

    Returns:
        JSON string with session summary and list of actions taken.
    """
    preferences = read_memory("preferences.md")
    feed_state = read_memory("feed_state.md")

    platform_urls = {
        "instagram": "https://www.instagram.com/",
        "x": "https://x.com/home",
    }
    start_url = platform_urls.get(platform.lower(), platform_urls["instagram"])

    system_prompt = FEED_CURATION_SYSTEM_PROMPT.format(
        preferences=preferences,
        feed_state=feed_state,
        post_count=post_count,
    )

    instruction = (
        f"Curate my {platform} feed. Process about {post_count} posts. "
        f"Like quality content matching my preferences, skip noise, mute rage bait. "
        f"Follow the de-radicalization protocol. Provide a summary when done."
    )

    actions_log = await run_computer_use(
        instruction=instruction,
        system_prompt=system_prompt,
        start_url=start_url,
        max_turns=post_count * 3,  # ~3 turns per post (observe, act, scroll)
    )

    return json.dumps({
        "platform": platform,
        "posts_targeted": post_count,
        "actions_taken": len(actions_log),
        "actions": actions_log,
    }, indent=2)
