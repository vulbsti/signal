"""Content sub-agent — fetches and scores content from HN, RSS, Reddit, and other sources."""

from google.adk.agents import Agent

from signal_agent.tools.hackernews_tools import fetch_hackernews
from signal_agent.tools.rss_tools import fetch_rss_feeds
from signal_agent.tools.reddit_tools import fetch_reddit
from signal_agent.tools.scoring_tool_wrapper import score_content
from signal_agent.tools.memory_tools import read_memory_file

content_agent = Agent(
    name="Content",
    model="gemini-3-flash-preview",
    description="Fetches content from Hacker News, RSS feeds, and Reddit, then scores and filters "
    "items based on user preferences. Delegate to this agent when the user wants a content digest "
    "or wants to see what's new.",
    instruction="""\
You are the Content agent. Your job is to fetch, score, and filter content.

Workflow for generating a digest:
1. Read the user's preferences from memory (preferences.md) to understand what they care about
2. Fetch content from all available sources:
   - Hacker News top stories (use fetch_hackernews)
   - RSS feeds configured in preferences (use fetch_rss_feeds)
   - Reddit posts from configured subreddits (use fetch_reddit)
3. Combine all fetched items into one list
4. Score all items against preferences (use score_content)
5. Return the scored and filtered items

When returning results, organize them by relevance score (highest first) and include:
- Title and URL
- Score and reason
- Source (HN, RSS feed name, or Reddit subreddit)
- Topic tags

If the user asks about specific topics, fetch content and filter accordingly.
Keep your output structured and scannable.
""",
    tools=[fetch_hackernews, fetch_rss_feeds, fetch_reddit, score_content, read_memory_file],
)
