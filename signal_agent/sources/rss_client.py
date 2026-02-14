"""RSS feed client using feedparser."""

import asyncio
import re
from dataclasses import dataclass

import feedparser


@dataclass
class RSSItem:
    title: str
    url: str
    summary: str
    source: str

    def to_dict(self) -> dict:
        return {
            "source": f"rss:{self.source}",
            "title": self.title,
            "url": self.url,
            "summary": self.summary,
        }


def _strip_html(text: str) -> str:
    """Remove HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", text).strip()


def _parse_feed(url: str) -> list[RSSItem]:
    """Parse a single RSS feed URL."""
    feed = feedparser.parse(url)
    source_name = feed.feed.get("title", url)
    items = []
    for entry in feed.entries[:15]:
        items.append(
            RSSItem(
                title=entry.get("title", ""),
                url=entry.get("link", ""),
                summary=_strip_html(entry.get("summary", "")),
                source=source_name,
            )
        )
    return items


async def fetch_feeds(feed_urls: list[str]) -> list[dict]:
    """Fetch multiple RSS feeds in parallel. Returns list of dicts ready for scoring."""
    loop = asyncio.get_running_loop()
    tasks = [loop.run_in_executor(None, _parse_feed, url) for url in feed_urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_items = []
    for result in results:
        if isinstance(result, list):
            all_items.extend(item.to_dict() for item in result)
    return all_items


def parse_feed_urls_from_preferences(preferences_text: str) -> list[str]:
    """Extract RSS feed URLs from preferences markdown."""
    urls = []
    in_rss_section = False
    for line in preferences_text.splitlines():
        if "## RSS Feeds" in line:
            in_rss_section = True
            continue
        if in_rss_section:
            if line.startswith("##"):
                break
            stripped = line.strip().lstrip("- ")
            if stripped.startswith("http"):
                urls.append(stripped)
    return urls
