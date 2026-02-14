"""Memory sub-agent — reads and writes .md memory files."""

from google.adk.agents import Agent

from signal_agent.tools.memory_tools import (
    read_memory_file,
    write_memory_file,
    append_history_entry,
    list_memories,
)

memory_agent = Agent(
    name="Memory",
    model="gemini-3-flash-preview",
    description="Reads and writes user memory files (preferences, history, profile, feed state). "
    "Delegate to this agent when you need to access or update the user's stored preferences, "
    "history, profile, or feed curation state.",
    instruction="""\
You are the Memory agent. You manage the user's persistent memory stored in markdown files.

Available memory files:
- preferences.md: Topics of interest, topics to avoid, source priorities, RSS feeds, content preferences
- history.md: Log of past digests, items shown, user actions (liked/dismissed/saved)
- profile.md: Interest vector, behavioral patterns, bias detection, evolution log
- feed_state.md: Per-platform feed curation status, recent actions, muted accounts

When asked to update memory:
1. Read the current file first
2. Make the requested changes while preserving the overall structure
3. Write the updated content back

When updating profile.md:
- Track engagement patterns over time
- Update the bias detection section if you notice echo chamber patterns
- Log changes in the evolution section with reasons

Always be transparent about what you're reading or changing.
""",
    tools=[read_memory_file, write_memory_file, append_history_entry, list_memories],
)
