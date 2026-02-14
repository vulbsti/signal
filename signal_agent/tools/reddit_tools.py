"""ADK tool functions for Reddit."""

import json

from signal_agent.sources.reddit_client import fetch_multiple_subreddits, parse_subreddits_from_preferences


async def fetch_reddit(subreddits_json: str = "") -> str:
    """Fetch hot posts from Reddit subreddits.

    If no subreddits provided, reads them from memory/preferences.md.

    Args:
        subreddits_json: Optional JSON array of subreddit names (without r/ prefix).
                         If empty, reads from preferences.

    Returns:
        JSON string of Reddit posts with title, url, score, comments, and source.
    """
    if subreddits_json:
        subreddits = json.loads(subreddits_json)
    else:
        from signal_agent.memory.manager import read_memory
        prefs = read_memory("preferences.md")
        subreddits = parse_subreddits_from_preferences(prefs)

    if not subreddits:
        return json.dumps({"error": "No subreddits configured in preferences"})

    posts = await fetch_multiple_subreddits(subreddits)
    return json.dumps(posts, indent=2)
