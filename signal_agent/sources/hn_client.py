"""Async Hacker News client using the Firebase API."""

import asyncio
from dataclasses import dataclass

import httpx

HN_BASE = "https://hacker-news.firebaseio.com/v0"


@dataclass
class HNItem:
    id: int
    title: str
    url: str
    score: int
    by: str
    num_comments: int

    def to_dict(self) -> dict:
        return {
            "source": "hackernews",
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "score": self.score,
            "by": self.by,
            "num_comments": self.num_comments,
        }


async def _fetch_item(client: httpx.AsyncClient, item_id: int) -> HNItem | None:
    """Fetch a single HN item by ID."""
    try:
        resp = await client.get(f"{HN_BASE}/item/{item_id}.json")
        resp.raise_for_status()
        data = resp.json()
        if data is None or data.get("type") != "story":
            return None
        return HNItem(
            id=data["id"],
            title=data.get("title", ""),
            url=data.get("url", ""),
            score=data.get("score", 0),
            by=data.get("by", ""),
            num_comments=data.get("descendants", 0),
        )
    except (httpx.HTTPError, KeyError):
        return None


async def fetch_top_stories(limit: int = 30) -> list[dict]:
    """Fetch top HN stories. Returns list of dicts ready for scoring."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{HN_BASE}/topstories.json")
        resp.raise_for_status()
        story_ids = resp.json()[:limit]

        tasks = [_fetch_item(client, sid) for sid in story_ids]
        results = await asyncio.gather(*tasks)

    return [item.to_dict() for item in results if item is not None]
