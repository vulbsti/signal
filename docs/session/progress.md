# Signal — Implementation Progress

## Session Date: 2026-02-14

## Status: All 3 Days Implemented

---

## Day 1: Foundation + Content Pipeline ✅

### Step 1: Project Scaffold
- `pyproject.toml` with all dependencies (pyaudio optional)
- `.env.example`, `.gitignore`
- Full directory structure: `signal_agent/` with `agents/`, `tools/`, `sources/`, `browser/`, `interfaces/`, `memory/`
- `config.py` — env vars, model names, paths
- `__init__.py` exports `from . import agent` (ADK convention)

### Step 2: Memory System
- `signal_agent/memory/manager.py` — `read_memory()`, `write_memory()`, `append_to_history()`, `list_memory_files()`
- `signal_agent/memory/schemas.py` — default templates for all memory files
- Seeded: `signal_agent/memory_data/preferences.md`, `history.md`, `profile.md`, `feed_state.md`
- Memory data lives in `signal_agent/memory_data/` (NOT project root, to avoid ADK scanner conflict)

### Step 3: Data Source Clients
- `sources/hn_client.py` — async HN Firebase API with `httpx`, parallel item fetching
- `sources/rss_client.py` — `feedparser` wrapper, `asyncio.get_running_loop()` for thread executor

### Step 4: Scoring Engine
- `tools/scoring_tools.py` — batch scoring with Gemini, up to 20 items per API call
- Lazy `genai.Client()` initialization (avoids import-time errors)
- Parses JSON from model response, handles markdown code fences
- Filters at score >= 60, sorts descending

### Step 5: ADK Agents
- `agents/memory_agent.py` — reads/writes .md memory files
- `agents/content_agent.py` — fetches HN + RSS + Reddit, scores content
- `agents/digest_agent.py` — formats scored items into readable digest
- `agent.py` — root coordinator "Signal" with 4 sub-agents
- Tool wrappers: `hackernews_tools.py`, `rss_tools.py`, `memory_tools.py`, `scoring_tool_wrapper.py`
- All tool functions are `async` (required — ADK runs its own event loop)

### Step 6: Verification
- All imports pass
- HN client fetches real stories
- RSS client fetches from 3 feeds
- Memory read/write/append works
- `adk web .` loads and works

---

## Day 2: Browser Automation + Telegram ✅

### Step 7: Playwright + Computer Use
- `browser/controller.py` — Microsoft Edge via `launch_persistent_context`, 1440x900 viewport
- `browser/actions.py` — 13 Computer Use actions, coordinate denormalization (0-999 grid → pixels)
- `browser/computer_use.py` — full agent loop: screenshot → Gemini 3 Pro → execute actions → repeat
  - Strips old screenshots (keeps last 3 turns) for token management
  - Handles safety confirmations
  - Temperature must be 1.0 for Gemini 3

### Step 8: Feed Agent
- `agents/feed_agent.py` — ADK sub-agent wrapping Computer Use
- `tools/browser_tools.py` — `curate_feed()` tool with full de-radicalization system prompt

### Step 9: De-Radicalization Logic
- Embedded in feed curation system prompt (Level 2 — Active)
- Detection: same-lean streaks (5+), negative sentiment (>70%), rage bait patterns
- Corrective: search opposing viewpoints, like diverse content, mute rage bait
- Transparency principle: always explains what was detected and why
- Level 1 (Passive) built into digest scoring prompt
- Level 3 (Long-term) built into profile.md structure

### Step 10: Telegram Bot
- `interfaces/telegram_bot.py` — full Telegram integration
- Commands: `/start`, `/digest`, `/voice`, `/curate [platform]`, `/preferences`, `/history`
- Free-form chat forwarded to root agent
- ADK session per Telegram user (explicit `create_session()` required)
- Message splitting for 4096 char limit
- Markdown send with plain text fallback

---

## Day 3: Reddit + Voice + Demo ✅

### Step 11: Edge Browser
- Switched from Chromium to `channel="msedge"`
- Uses persistent profile at `signal_agent/browser/.edge_profile/`
- `--disable-blink-features=AutomationControlled` to avoid detection

### Step 12: Reddit Web-Fetch
- `sources/reddit_client.py` — fetches from Reddit JSON endpoints (no API key needed)
- Appending `.json` to any Reddit URL returns structured data
- `tools/reddit_tools.py` — ADK tool wrapper
- Subreddits configured in preferences.md: r/programming, r/MachineLearning, r/LocalLLaMA, r/ExperiencedDevs, r/science
- Wired into content agent as `fetch_reddit` tool

### Step 13: Voice Briefing
- `interfaces/live_voice.py` — Gemini Live API (`gemini-2.5-flash-native-audio-preview-12-2025`)
- Text-in → 24kHz PCM audio-out via WebSocket
- Saves to WAV file, plays with pyaudio or system player fallback
- `/voice` Telegram command generates and sends audio file

### Step 14: Demo Script
- `scripts/demo.py` — end-to-end terminal demo
- Tested: 127 items from 3 sources → 66 passed scoring → top 10 displayed
- Sources: HN(19), RSS(40), Reddit(68)
- Top topics: AI/ML(30), Systems programming(16), Open source(13)

---

## Key Bugs Fixed During Implementation

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| `asyncio.run()` inside ADK | ADK runs its own event loop | Made all tool functions `async` |
| ADK scanner finds `memory/` | `memory/` dir at project root treated as agent | Moved to `signal_agent/memory_data/` |
| `adk web signal_agent` fails | ADK argument is agents_dir, not agent | Use `adk web .` instead |
| LiteLLM auth error | `GOOGLE_GEMINI_BASE_URL` pointed to LiteLLM proxy | Cleaned env vars in `.bashrc` |
| Session not found | `InMemoryRunner` needs explicit session creation | Added `_ensure_session()` with `create_session()` |
| Telegram Markdown parse error | Model output has invalid Markdown for Telegram | Added fallback: try Markdown, catch → plain text |
| `genai.Client()` at import time | Fails if env vars not loaded yet | Lazy init with `_get_client()` |
| `pyproject.toml` build backend | Used wrong setuptools backend path | Fixed to `setuptools.build_meta` |
| Setuptools multi-package error | `memory/` and `signal_agent/` both detected | Added `[tool.setuptools.packages.find]` with include filter |

---

## Model Configuration

| Use Case | Model |
|----------|-------|
| All ADK agents (root, content, digest, memory, feed) | `gemini-3-flash-preview` |
| Scoring engine (batch content scoring) | `gemini-3-flash-preview` |
| Computer Use (browser automation) | `gemini-3-pro-preview` |
| Voice briefing (Live API) | `gemini-2.5-flash-native-audio-preview-12-2025` |

---

## How to Run

```bash
cd ~/proj/noise_reduction/noise_v1
source .venv/bin/activate

# ADK Web UI
adk web .

# Telegram Bot
python -m signal_agent.interfaces.telegram_bot

# Demo Script
python scripts/demo.py

# Voice Test
python -c "import asyncio; from signal_agent.interfaces.live_voice import briefing_from_digest; asyncio.run(briefing_from_digest('Test briefing'))"

# Browser Curation (needs: playwright install msedge)
# Use /curate instagram in Telegram
```

---

## File Tree (Final)

```
noise_v1/
├── pyproject.toml
├── .env / .env.example
├── .gitignore
├── docs/
│   ├── plan.md
│   └── session/progress.md
├── scripts/
│   └── demo.py
├── signal_agent/
│   ├── __init__.py              # from . import agent
│   ├── agent.py                 # Root agent "Signal" (4 sub-agents)
│   ├── config.py                # Env vars, model names, paths
│   ├── agents/
│   │   ├── content_agent.py     # Fetch + score content
│   │   ├── digest_agent.py      # Format digest
│   │   ├── feed_agent.py        # Browser feed curation
│   │   └── memory_agent.py      # Read/write memory files
│   ├── tools/
│   │   ├── hackernews_tools.py  # HN tool wrapper
│   │   ├── rss_tools.py         # RSS tool wrapper
│   │   ├── reddit_tools.py      # Reddit tool wrapper
│   │   ├── scoring_tools.py     # Gemini batch scoring engine
│   │   ├── scoring_tool_wrapper.py  # ADK tool for scoring
│   │   ├── memory_tools.py      # Memory read/write tools
│   │   └── browser_tools.py     # Feed curation tool
│   ├── sources/
│   │   ├── hn_client.py         # Async HN Firebase client
│   │   ├── rss_client.py        # feedparser wrapper
│   │   └── reddit_client.py     # Reddit JSON endpoint client
│   ├── browser/
│   │   ├── controller.py        # Edge browser lifecycle
│   │   ├── actions.py           # Action execution + coord denorm
│   │   └── computer_use.py      # Gemini Computer Use agent loop
│   ├── interfaces/
│   │   ├── telegram_bot.py      # Telegram → ADK bridge
│   │   └── live_voice.py        # Gemini Live API voice briefing
│   ├── memory/
│   │   ├── manager.py           # File I/O for memory
│   │   └── schemas.py           # Default templates
│   └── memory_data/
│       ├── preferences.md       # User preferences (tracked)
│       ├── history.md           # Session history (gitignored)
│       ├── profile.md           # User profile (gitignored)
│       └── feed_state.md        # Feed state (gitignored)
└── tests/
```
