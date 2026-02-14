"""Batch scoring engine — scores content items against user preferences using Gemini."""

import json

from google import genai

from signal_agent.config import FLASH_MODEL, SCORE_THRESHOLD, BATCH_SIZE

_client = genai.Client()

SCORING_PROMPT = """\
You are a content relevance scorer. Given a user's preferences and a batch of content items,
score each item from 0-100 based on how relevant and interesting it would be to this user.

## User Preferences
{preferences}

## Content Items
{items_json}

## Instructions
For each item, return a JSON object with:
- "index": the item's position in the list (0-based)
- "score": integer 0-100
- "reason": one sentence explaining the score
- "topics": list of 1-3 topic tags

Return ONLY a JSON array of these objects, no other text.
Example: [{{"index": 0, "score": 85, "reason": "Directly about AI agents", "topics": ["AI", "agents"]}}]
"""


def _build_items_summary(items: list[dict]) -> str:
    """Build a concise summary of items for the scoring prompt."""
    summaries = []
    for i, item in enumerate(items):
        parts = [f"[{i}] {item.get('title', 'No title')}"]
        if item.get("url"):
            parts.append(f"  URL: {item['url']}")
        if item.get("summary"):
            parts.append(f"  Summary: {item['summary'][:200]}")
        if item.get("score"):
            parts.append(f"  HN Score: {item['score']}")
        if item.get("source"):
            parts.append(f"  Source: {item['source']}")
        summaries.append("\n".join(parts))
    return "\n\n".join(summaries)


async def score_items(items: list[dict], preferences: str) -> list[dict]:
    """Score a batch of content items against user preferences.

    Args:
        items: List of content item dicts (from HN/RSS clients).
        preferences: The raw text of preferences.md.

    Returns:
        List of items enriched with 'relevance_score', 'reason', and 'topics' fields,
        filtered to only items scoring >= SCORE_THRESHOLD.
    """
    if not items:
        return []

    all_scored = []

    # Process in batches
    for start in range(0, len(items), BATCH_SIZE):
        batch = items[start : start + BATCH_SIZE]
        items_summary = _build_items_summary(batch)
        prompt = SCORING_PROMPT.format(
            preferences=preferences, items_json=items_summary
        )

        response = await _client.aio.models.generate_content(
            model=FLASH_MODEL,
            contents=prompt,
        )

        try:
            text = response.text.strip()
            # Strip markdown code fences if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                text = text.rsplit("```", 1)[0]
            scores = json.loads(text)
        except (json.JSONDecodeError, IndexError):
            # If parsing fails, skip this batch
            continue

        for score_entry in scores:
            idx = score_entry.get("index", -1)
            if 0 <= idx < len(batch):
                item = batch[idx].copy()
                item["relevance_score"] = score_entry.get("score", 0)
                item["reason"] = score_entry.get("reason", "")
                item["topics"] = score_entry.get("topics", [])
                all_scored.append(item)

    # Filter and sort
    filtered = [i for i in all_scored if i["relevance_score"] >= SCORE_THRESHOLD]
    filtered.sort(key=lambda x: x["relevance_score"], reverse=True)
    return filtered
