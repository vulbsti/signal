"""Memory manager — reads and writes .md files that store user preferences and history."""

import os
from datetime import datetime, timezone

from signal_agent.config import MEMORY_DIR


def _memory_path(filename: str) -> str:
    return os.path.join(MEMORY_DIR, filename)


def read_memory(filename: str) -> str:
    """Read an entire memory file. Returns empty string if file doesn't exist."""
    path = _memory_path(filename)
    if not os.path.exists(path):
        return ""
    with open(path, "r") as f:
        return f.read()


def write_memory(filename: str, content: str) -> str:
    """Overwrite a memory file with new content. Returns confirmation."""
    path = _memory_path(filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return f"Updated {filename}"


def append_to_history(entry: str) -> str:
    """Append a timestamped entry to history.md."""
    path = _memory_path("history.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    block = f"\n## {timestamp}\n\n{entry}\n"
    with open(path, "a") as f:
        f.write(block)
    return f"Appended to history at {timestamp}"


def list_memory_files() -> list[str]:
    """List all .md files in the memory directory."""
    if not os.path.exists(MEMORY_DIR):
        return []
    return [f for f in os.listdir(MEMORY_DIR) if f.endswith(".md")]
