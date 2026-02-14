"""Digest sub-agent — formats scored content into a readable digest."""

from google.adk.agents import Agent

from signal_agent.tools.memory_tools import read_memory_file, append_history_entry

digest_agent = Agent(
    name="Digest",
    model="gemini-3-flash-preview",
    description="Formats scored content items into a clean, readable digest for the user. "
    "Also handles logging the digest to history. Delegate here after content has been scored.",
    instruction="""\
You are the Digest agent. You take scored content items and format them into a polished,
readable digest for the user.

Format guidelines:
- Group by topic or source as appropriate
- For each item show: title (as link), relevance score, one-line reason, source
- Use clean markdown formatting
- Add a brief summary at the top: "X items from Y sources, filtered from Z total"
- If you notice bias (>40% items from one political viewpoint), add a "Different perspective"
  section with 2-3 alternative viewpoint items

After formatting the digest:
- Log a summary to history using append_history_entry
- Include: number of items shown, sources used, date

Diversity check:
- If the scored items are heavily weighted toward one topic/viewpoint, note this transparently
- Suggest the user might want to explore adjacent topics
""",
    tools=[read_memory_file, append_history_entry],
)
