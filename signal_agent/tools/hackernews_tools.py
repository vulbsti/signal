"""ADK tool functions for Hacker News."""

import json

from signal_agent.sources.hn_client import fetch_top_stories


async def fetch_hackernews(limit: int = 30) -> str:
    """Fetch top stories from Hacker News.

    Args:
        limit: Maximum number of stories to fetch (default 30, max 50).

    Returns:
        JSON string of top HN stories with title, url, score, author, and comment count.
    """
    limit = min(limit, 50)
    stories = await fetch_top_stories(limit)
    return json.dumps(stories, indent=2)
