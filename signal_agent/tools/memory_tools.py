"""ADK tool functions for memory operations."""

from signal_agent.memory.manager import (
    read_memory,
    write_memory,
    append_to_history,
    list_memory_files,
)


def read_memory_file(filename: str) -> str:
    """Read a memory file by name. Available files: preferences.md, history.md, profile.md, feed_state.md.

    Args:
        filename: Name of the memory file to read (e.g. 'preferences.md').

    Returns:
        The full contents of the memory file, or empty string if it doesn't exist.
    """
    return read_memory(filename)


def write_memory_file(filename: str, content: str) -> str:
    """Overwrite a memory file with new content. Use this to update preferences, profile, or feed state.

    Args:
        filename: Name of the memory file to write (e.g. 'preferences.md').
        content: The full markdown content to write.

    Returns:
        Confirmation message.
    """
    return write_memory(filename, content)


def append_history_entry(entry: str) -> str:
    """Append a new timestamped entry to the history log.

    Args:
        entry: The markdown-formatted entry to append (e.g. digest results, actions taken).

    Returns:
        Confirmation with timestamp.
    """
    return append_to_history(entry)


def list_memories() -> str:
    """List all available memory files.

    Returns:
        Comma-separated list of memory file names.
    """
    files = list_memory_files()
    return ", ".join(files) if files else "No memory files found."
