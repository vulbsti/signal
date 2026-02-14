"""Reddit client using web-fetch (JSON endpoints, no API key needed)."""

import re
from dataclasses import dataclass

import httpx

# Reddit requires a User-Agent or it returns 429
_HEADERS = {"User-Agent": "Signal-NoiseReducer/0.1 (content aggregator)"}


@dataclass
class RedditPost:
    title: str
    url: str
    score: int
    num_comments: int
    subreddit: str
    author: str
    selftext: str

    def to_dict(self) -> dict:
        return {
            "source": f"reddit:r/{self.subreddit}",
            "title": self.title,
            "url": self.url,
            "score": self.score,
            "num_comments": self.num_comments,
            "author": self.author,
            "summary": self.selftext[:300] if self.selftext else "",
        }


async def fetch_subreddit(subreddit: str, sort: str = "hot", limit: int = 15) -> list[RedditPost]:
    """Fetch posts from a subreddit using Reddit's JSON endpoint."""
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
    async with httpx.AsyncClient(timeout=15, headers=_HEADERS) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

    posts = []
    for child in data.get("data", {}).get("children", []):
        d = child.get("data", {})
        if d.get("stickied"):
            continue
        posts.append(RedditPost(
            title=d.get("title", ""),
            url=d.get("url", ""),
            score=d.get("score", 0),
            num_comments=d.get("num_comments", 0),
            subreddit=d.get("subreddit", subreddit),
            author=d.get("author", ""),
            selftext=d.get("selftext", ""),
        ))
    return posts


async def fetch_multiple_subreddits(subreddits: list[str]) -> list[dict]:
    """Fetch from multiple subreddits. Returns list of dicts ready for scoring."""
    import asyncio
    tasks = [fetch_subreddit(sub) for sub in subreddits]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_posts = []
    for result in results:
        if isinstance(result, list):
            all_posts.extend(post.to_dict() for post in result)
    return all_posts


def parse_subreddits_from_preferences(preferences_text: str) -> list[str]:
    """Extract subreddit names from preferences markdown."""
    subreddits = []
    in_section = False
    for line in preferences_text.splitlines():
        if "## Subreddits" in line or "## Reddit" in line:
            in_section = True
            continue
        if in_section:
            if line.startswith("##"):
                break
            # Match r/name or just name after a bullet
            match = re.search(r"r/(\w+)", line)
            if match:
                subreddits.append(match.group(1))
            elif line.strip().startswith("- ") and line.strip()[2:].strip():
                name = line.strip()[2:].strip()
                if name.isalnum() or "_" in name:
                    subreddits.append(name)
    return subreddits
