"""ADK tool wrapper for the scoring engine."""

import json

from signal_agent.tools.scoring_tools import score_items
from signal_agent.memory.manager import read_memory


async def score_content(items_json: str) -> str:
    """Score content items against user preferences and filter out low-relevance items.

    Takes a JSON array of content items (from HN or RSS) and returns only the items
    that score above the relevance threshold, sorted by score descending.

    Args:
        items_json: JSON string containing an array of content items to score.

    Returns:
        JSON string of scored and filtered items, each with relevance_score, reason, and topics.
    """
    items = json.loads(items_json)
    preferences = read_memory("preferences.md")
    scored = await score_items(items, preferences)
    return json.dumps(scored, indent=2)
