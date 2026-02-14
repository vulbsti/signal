# Signal — Personalised Noise Reducer

## Context

Information overload is the modern attention tax. We check 5+ apps, dozens of newsletters, and multiple social feeds daily — 90% is noise. Worse, social media algorithms push us toward radicalization through engagement-optimized echo chambers.

**Signal** is a Gemini-powered personal AI agent that:
1. **Filters content** — Scans HN, Reddit, RSS, Gmail newsletters; scores and filters by your learned preferences
2. **Curates social feeds** — Uses Gemini Computer Use to physically operate Instagram/X.com, optimizing your feed and countering radicalization
3. **Learns continuously** — Preferences stored in `.md` files that evolve with every interaction

Built for the Gemini Hackathon. Weekend timeline (2-3 days).

---

## Models Reference

| Use Case | Model | Why |
|----------|-------|-----|
| Content analysis, scoring, memory, digest | `gemini-3-flash` | Fast, cheap ($0.50/1M input), pro-grade reasoning |
| Computer Use (browser automation) | `gemini-3-pro` | Best agentic capabilities, 1500+ Elo, supports Computer Use tool |
| ADK sub-agents (content, memory, digest) | `gemini-3-flash` | Each sub-agent runs Flash for speed |
| Live API voice (stretch) | `gemini-3-flash` | Native audio support, low latency |

---

## Architecture: ADK + Gemini APIs

```
                    Telegram Bot / Gemini Live Voice
                              |
                    +---------v----------+
                    |   Root Agent       |  (ADK, gemini-3-flash)
                    |   "Signal"         |  Coordinates all sub-agents
                    +----+----+----+-----+
                         |    |    |    |
          +--------------+    |    |    +--------------+
          v                   v    v                   v
  Content Agent        Memory Agent    Feed Agent     Digest Agent
  (fetch + score)      (read/write     (Computer Use  (format output)
                        .md files)      + Playwright)
```

**Gemini products used (4+):**
- **Gemini 3 Flash** (`gemini-3-flash`) — content analysis, scoring, memory management. 35% better coding, 3x faster than 2.5 Pro, $0.50/1M input tokens
- **Gemini 3 Pro** (`gemini-3-pro`) — Computer Use browser automation for social media. First model to break 1500 Elo. $2.00/1M input tokens
- **Gemini Live API** — voice briefings (stretch goal), native audio support
- **Google ADK** — agent orchestration
- **Function calling** — tool use throughout

---

## Project Structure

```
noise_init/
├── pyproject.toml
├── .env / .env.example
├── .gitignore
├── signal_agent/                 # ADK agent package
│   ├── __init__.py               # Exports root_agent
│   ├── agent.py                  # Root coordinator (ADK entry point)
│   ├── config.py                 # Env vars, constants
│   ├── agents/
│   │   ├── content_agent.py      # Module 1: fetch + filter content
│   │   ├── feed_agent.py         # Module 2: Computer Use browser curation
│   │   ├── digest_agent.py       # Format filtered content
│   │   └── memory_agent.py       # Read/write/update .md memory
│   ├── tools/
│   │   ├── hackernews_tools.py   # HN Firebase API
│   │   ├── rss_tools.py          # RSS feed parser
│   │   ├── gmail_tools.py        # Gmail newsletter parsing
│   │   ├── reddit_tools.py       # Reddit/PRAW
│   │   ├── memory_tools.py       # .md file read/write
│   │   ├── scoring_tools.py      # Gemini batch scoring
│   │   └── browser_tools.py      # Playwright + Computer Use helpers
│   ├── sources/
│   │   ├── hn_client.py          # Async HN Firebase client
│   │   ├── rss_client.py         # feedparser wrapper
│   │   ├── gmail_client.py       # Gmail API OAuth + fetch
│   │   └── reddit_client.py      # PRAW wrapper
│   ├── browser/
│   │   ├── controller.py         # Playwright lifecycle
│   │   ├── actions.py            # Coord denormalization, action execution
│   │   └── computer_use.py       # Gemini Computer Use agent loop
│   ├── interfaces/
│   │   ├── telegram_bot.py       # Telegram bot -> ADK root agent
│   │   └── live_voice.py         # Gemini Live API voice interface
│   └── memory/
│       ├── manager.py            # Memory read/write/update logic
│       └── schemas.py            # Markdown schemas and parsing
├── memory/                       # Persistent state (.md files)
│   ├── preferences.md
│   ├── history.md
│   ├── profile.md
│   └── feed_state.md
├── scripts/
│   ├── seed_preferences.py       # Interactive preference seeding
│   └── demo.py                   # Demo runner
└── tests/
    ├── test_hn_client.py
    └── test_memory.py
```

---

## Memory System (.md Files)

The core differentiator — no vector DBs, just transparent markdown that Gemini reads/writes natively.

### `memory/preferences.md`
- Topics with weights (0-1): what user cares about, what to avoid
- Sources by priority tier (high/medium/low)
- People followed
- Content style preferences
- RSS feed URLs

### `memory/history.md`
- Daily entries with items shown, scores, user actions (liked/dismissed/saved)
- Feed curation logs (platform, actions taken, duration)

### `memory/profile.md`
- Rolling interest vector with engagement rates and trends
- Behavioral patterns (time preferences, content length preferences)
- Bias detection section (echo chamber risk level, dominant viewpoints)
- Evolution log (what changed and why)

### `memory/feed_state.md`
- Per-platform status, last session, login state
- Feed health score
- Recent actions log
- Muted accounts list

**Key principle**: The Gemini model decides *what* to write (content, formatting, analysis). Python code just handles file I/O.

---

## Implementation Plan (Day-by-Day)

### Day 1: Foundation + Content Pipeline

**Step 1: Project scaffold**
- Save this plan to `docs/plan.md`
- Create `pyproject.toml` with dependencies
- Set up virtual environment
- Create `.env.example` template
- Create `.gitignore`
- Initialize git repo
- **Dependencies**: `google-adk`, `google-genai`, `playwright`, `python-telegram-bot`, `feedparser`, `httpx`, `praw`, `google-api-python-client`, `google-auth-oauthlib`, `pyaudio`, `python-dotenv`

**Step 2: Memory system**
- `signal_agent/memory/manager.py` — read_memory(), write_memory(), append_to_history()
- Seed initial `memory/preferences.md` with sample preferences
- Seed initial empty `memory/history.md`, `memory/profile.md`, `memory/feed_state.md`

**Step 3: Data source clients**
- `sources/hn_client.py` — async fetch via Firebase API (`httpx`). No auth, no rate limits.
  - Endpoint: `https://hacker-news.firebaseio.com/v0/topstories.json`
  - Fetch item details in parallel
- `sources/rss_client.py` — `feedparser` wrapper. No auth.
  - Fetch from list of URLs in preferences

**Step 4: Scoring engine**
- `tools/scoring_tools.py` — batch scoring with Gemini 3 Flash
  - Score up to 20 items per API call (critical for rate limits on free tier)
  - Prompt includes user preferences, returns JSON with score/reason/topics per item
  - Filter threshold: score >= 60

**Step 5: ADK agents — content pipeline**
- `agents/memory_agent.py` — sub-agent with memory read/write tools
- `agents/content_agent.py` — sub-agent with HN/RSS/scoring tools
- `agents/digest_agent.py` — sub-agent that formats scored items into readable digest
- `agent.py` — root coordinator that delegates to sub-agents

**Step 6: Test via ADK web UI**
- Run `adk web signal_agent`
- Verify: "Give me my digest" produces a filtered, scored content list from HN + RSS

**Day 1 deliverable**: Working content digest pipeline via ADK web UI.

---

### Day 2: Browser Automation + Telegram

**Step 7: Playwright + Computer Use**
- `browser/controller.py` — launch Chromium, manage lifecycle, cookie persistence
- `browser/actions.py` — execute Computer Use actions (click, scroll, type), coordinate denormalization (model uses 0-999 grid, convert to actual pixels for 1440x900 viewport)
- `browser/computer_use.py` — the agent loop:
  1. Screenshot page
  2. Send to `gemini-3-pro` with Computer Use tool enabled and preferences as system context
  3. Receive function_call actions
  4. Execute via Playwright
  5. Screenshot again, loop
  - System prompt includes de-radicalization protocol
  - Default: process 10 posts per session

**Step 8: Feed agent**
- `agents/feed_agent.py` — ADK sub-agent wrapping the Computer Use loop
- Integrate with memory (reads preferences + feed_state, writes actions back)
- Test: launch browser, navigate to Instagram, process 5-10 posts

**Step 9: De-radicalization logic**
- Built into Computer Use system prompt:
  - Track topic/sentiment distribution per session
  - Trigger on: 5+ same-lean posts, >70% negative sentiment, rage bait detected
  - Corrective: search for opposing viewpoints, like diverse content, mute rage bait accounts
- Built into digest scoring: diversity check, inject alternative perspectives if echo chamber detected
- Built into profile updates: bias detection section tracks trends over time

**Step 10: Telegram bot**
- `interfaces/telegram_bot.py` — connect Telegram to ADK root agent
- Commands: `/start`, `/digest`, `/curate [platform]`
- Free-form messages forwarded to root agent
- ADK session per Telegram user
- Setup: create bot via @BotFather, get token

**Day 2 deliverable**: Full working system — Telegram bot that generates filtered digests AND curates Instagram via Computer Use.

---

### Day 3: Polish + Stretch Goals + Demo

**Step 11: Stretch — Gmail integration**
- `sources/gmail_client.py` — Gmail API with OAuth
- Requires: Google Cloud project, OAuth consent screen, credentials.json
- `scripts/setup_gmail.py` — one-time OAuth flow
- Parse newsletters: extract subject, sender, body text

**Step 12: Stretch — Reddit integration**
- `sources/reddit_client.py` — PRAW wrapper
- Requires: Reddit app registration at reddit.com/prefs/apps
- Fetch hot posts from configured subreddits

**Step 13: Stretch — Gemini Live API voice**
- `interfaces/live_voice.py` — voice briefing via Gemini 3 Flash with Live API native audio
- WebSocket connection, 16kHz PCM input, 24kHz output
- System prompt: "Read this digest aloud, be concise"
- Requires: `pyaudio` for microphone/speaker

**Step 14: Demo prep**
- End-to-end testing
- Record backup demo video
- Polish Telegram message formatting
- README with architecture diagram

---

## De-Radicalization Algorithm (3 Levels)

### Level 1 — Digest (Passive)
Scoring prompt includes diversity check. If >40% of items share a single political viewpoint, inject 2-3 alternative perspectives with transparency: "Different perspective:".

### Level 2 — Feed Curation (Active)
Computer Use agent prompt includes protocol: detect same-lean streaks (5+ posts), negative sentiment dominance (>70%), rage bait patterns. Corrective: search opposing queries, like diverse content, mute rage bait accounts.

### Level 3 — Profile (Long-term)
Memory agent analyzes weekly topic distribution trends. Flags >20% growth in any controversial topic. Suggests perspective-broadening items. Always transparent — tells user what it detected and why.

**Principle**: NOT censorship. AWARENESS. Always explain what was detected and why diverse content is suggested.

---

## Key Dependencies

```toml
[project]
name = "signal-noise-reducer"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "google-adk>=1.25.0",
    "google-genai>=1.63.0",
    "playwright>=1.49.0",
    "python-telegram-bot>=22.6",
    "feedparser>=6.0.0",
    "httpx>=0.27.0",
    "praw>=7.8.0",
    "google-api-python-client>=2.150.0",
    "google-auth-oauthlib>=1.2.0",
    "pyaudio>=0.2.14",
    "python-dotenv>=1.0.0",
]
```

## Environment Variables (.env)

```
GOOGLE_API_KEY=<AI Studio key>
GOOGLE_GENAI_USE_VERTEXAI=FALSE
TELEGRAM_BOT_TOKEN=<from @BotFather>
REDDIT_CLIENT_ID=<optional>
REDDIT_CLIENT_SECRET=<optional>
```

---

## Verification

1. **Memory system**: Write and read back each .md file, verify content integrity
2. **HN client**: Fetch top 10 stories, verify titles and URLs are populated
3. **RSS client**: Fetch from 2-3 test feeds, verify parsing
4. **Scoring**: Score 20 HN stories against seed preferences, verify JSON output with scores
5. **Content pipeline**: Run `adk web signal_agent`, type "Give me my digest", verify filtered output
6. **Computer Use**: Launch browser to Instagram, process 3 posts, verify actions logged
7. **Telegram**: Send `/digest` to bot, receive formatted digest on phone
8. **De-radicalization**: Seed history with biased consumption pattern, verify bias detection fires
9. **End-to-end demo**: Run the full demo script (digest + feed curation) in under 5 minutes

---

## Demo Script (5 min)

1. **Problem** (30s): "90% of what we consume is noise. Social algorithms push radicalization."
2. **Architecture** (30s): Show agent diagram. "4 Gemini products, one coherent agent."
3. **Live: Content Digest** (90s): `/digest` in Telegram → filtered HN+RSS results with scores
4. **Live: Feed Curation** (90s): "Curate my Instagram" → watch Computer Use scroll, like, skip, mute in real-time browser
5. **Memory** (30s): Open `preferences.md` — "Just markdown. Transparent. Editable. No black box."
6. **Close** (30s): "Clear the noise. Just signal."

---

## Critical Files (Priority Order)

1. `signal_agent/agent.py` — Root ADK coordinator
2. `signal_agent/memory/manager.py` — Memory persistence layer
3. `signal_agent/tools/scoring_tools.py` — Gemini batch scoring (core intelligence)
4. `signal_agent/sources/hn_client.py` — First data source (no auth needed)
5. `signal_agent/sources/rss_client.py` — Second data source (no auth needed)
6. `signal_agent/browser/computer_use.py` — Gemini Computer Use + Playwright loop
7. `signal_agent/interfaces/telegram_bot.py` — Primary demo interface
