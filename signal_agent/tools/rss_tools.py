"""ADK tool functions for RSS feeds."""

import json

from signal_agent.sources.rss_client import fetch_feeds, parse_feed_urls_from_preferences


async def fetch_rss_feeds(feed_urls_json: str = "") -> str:
    """Fetch articles from RSS feeds.

    If no URLs provided, reads them from memory/preferences.md.

    Args:
        feed_urls_json: Optional JSON array of feed URLs. If empty, reads from preferences.

    Returns:
        JSON string of RSS items with title, url, summary, and source.
    """
    if feed_urls_json:
        urls = json.loads(feed_urls_json)
    else:
        from signal_agent.memory.manager import read_memory

        prefs = read_memory("preferences.md")
        urls = parse_feed_urls_from_preferences(prefs)

    if not urls:
        return json.dumps({"error": "No RSS feed URLs found"})

    items = await fetch_feeds(urls)
    return json.dumps(items, indent=2)
