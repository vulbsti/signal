# Signal — Personalised Noise Reducer

> Improve the signal. Reduce the noise.

We live in a world of information overload. Our feeds are simultaneously our best source of knowledge and our biggest distraction. We scroll through hundreds of posts, newsletters pile up, and algorithms optimise for engagement — not for us. Before we know it, we're stuck in rabbit holes, our feeds are radicalised, and the content that actually matters gets buried.

Curating all of this manually? Impossible. Tuning your Instagram algorithm, filtering newsletters, diversifying your news diet — it's a full-time job. And even if you try, you're still one rage-bait click away from a feed that no longer serves you.

**Signal** is an autonomous AI agent that does this for you.

## The Idea

Signal is built on a simple premise: **what if an AI agent could manage your entire information diet?**

Not by building another feed algorithm that optimises for your attention. Not by training neural networks on your engagement patterns. But by giving an AI agent your actual preferences — in plain English — and letting it go to work.

It reads your news. It scrolls your Instagram. It filters your content. It learns what you care about. And critically — it watches for the patterns you can't see yourself: echo chambers forming, rage bait creeping in, your feed slowly radicalising.

### What Makes This Different

**No complex ML pipeline.** Signal doesn't use reinforcement learning, vector databases, or embedding similarity scores. Your preferences live in a simple markdown file. The agent reads it, reasons about it, and acts on it. When your tastes change, you tell it in natural language: *"I'm more interested in climate tech now"* — and it updates a markdown file. That's it.

**No black-box algorithm.** Every decision Signal makes is transparent. You can read `preferences.md` and see exactly what it thinks you care about. You can read `history.md` and see every digest it ever generated. There's no hidden model, no opaque weights. Just markdown files and an LLM that can reason.

**Actual computer use.** Signal doesn't just fetch RSS feeds. It opens a real browser, logs into your Instagram, scrolls through your feed, likes quality content, skips noise, and mutes rage-bait accounts. It operates your social media the way you would — if you had infinite patience and zero susceptibility to outrage bait.

## How It Works

Signal is built on [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) and powered by Gemini models. It runs as a backend service and is controlled through a Telegram bot.

### Architecture

```
You (Telegram) ──> Telegram Bot ──> ADK Backend (port 3030)
                                         │
                            ┌─────────────┼─────────────┐
                            │             │             │
                       Content Agent  Feed Agent   Memory Agent
                            │             │             │
                      ┌─────┴─────┐    Browser      Markdown
                      │     │     │   Automation      Files
                   Hacker  RSS  Reddit  (browser-use)
                    News  Feeds  Posts
```

**Root Agent (Signal)** — The orchestrator. Routes your requests to the right sub-agent.

**Content Agent** — Fetches articles from Hacker News, RSS feeds, and Reddit. Scores each item against your preferences using Gemini. Filters out the noise, keeps the signal.

**Digest Agent** — Takes scored content and formats it into a clean, readable daily digest. Groups by topic, adds diversity sections to counter echo chambers.

**Feed Agent** — The most interesting one. Uses [browser-use](https://github.com/browser-use/browser-use) to physically operate a browser. Scrolls through your Instagram or X feed, likes posts that match your interests, skips irrelevant content, and mutes rage-bait accounts. Follows a de-radicalisation protocol that detects when your feed is leaning too heavily in one direction.

**Memory Agent** — Reads and writes your preference files, history, and profile. All persistent state lives in simple `.md` files.

### The Memory System

This is the core of how Signal "learns." No neural networks, no vector stores. Just four markdown files:

| File | What It Stores |
|------|---------------|
| `preferences.md` | Your topics of interest with weights, RSS feeds, subreddits, content preferences |
| `history.md` | Log of every digest generated — what was shown, what was filtered |
| `profile.md` | Long-term patterns — engagement style, bias detection, echo chamber risk |
| `feed_state.md` | Platform login status, curation session logs, muted accounts |

When you say *"I don't care about crypto anymore"*, the memory agent reads `preferences.md`, removes the crypto entry, and writes it back. When you say *"Show me more science content"*, it bumps the science weight. The LLM does the reasoning. Markdown does the storage.

### De-Radicalisation Protocol

This isn't a feature bolted on as an afterthought — it's central to what Signal does.

When the feed agent curates your social media, it follows these rules:
- If it sees 5+ consecutive posts with the same political/ideological lean, it actively seeks diverse content
- It never engages with inflammatory or outrage-driven content
- It prefers substantive, informative content over engagement bait
- When in doubt, it skips rather than engages

The digest agent does the same for your news: it includes a "Different Perspective" section that deliberately surfaces viewpoints outside your usual bubble.

## Setup

### Prerequisites

- Python 3.12+
- A Gemini API key (or a LiteLLM proxy endpoint)
- Microsoft Edge (for browser automation — uses persistent profiles)
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))

### Installation

```bash
git clone <repo-url> && cd noise_v1
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Install browser dependencies
playwright install
```

### Configuration

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

```env
GOOGLE_API_KEY=your-gemini-api-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

If you use a LiteLLM proxy, set these in your shell:
```bash
export GOOGLE_GEMINI_BASE_URL=https://your-proxy-url
export GEMINI_API_KEY=your-key
export OPENAI_BASE_URL=https://your-proxy-url
```

### Running

**1. Start the ADK backend:**

```bash
bash scripts/start.sh
```

This launches the agent backend on `http://localhost:3030` with both a web UI and API.

**2. Start the Telegram bot (in a separate terminal):**

```bash
source .venv/bin/activate
python -m signal_agent.interfaces.telegram_bot
```

### Usage (Telegram Commands)

| Command | What It Does |
|---------|-------------|
| `/digest` | Get your filtered daily news digest |
| `/voice` | Get your digest as a voice briefing |
| `/login instagram` | Open a browser to log into Instagram (you log in manually, agent detects it) |
| `/curate instagram` | Let the agent scroll and curate your Instagram feed |
| `/preferences` | View your current preferences |
| `/history` | View past digest logs |
| Or just type anything | Chat naturally — ask questions, update preferences, etc. |

### Customising Your Preferences

Edit `signal_agent/memory_data/preferences.md` directly, or just tell the agent:

- *"I'm really into climate tech lately"*
- *"Stop showing me crypto stuff"*
- *"Add r/rust to my subreddits"*
- *"I prefer shorter articles, 5 minutes max"*

The agent updates the markdown file for you.

## Project Structure

```
signal_agent/
├── agent.py                  # Root agent (ADK entry point)
├── config.py                 # Environment & configuration
├── __init__.py
├── agents/                   # Sub-agent definitions
│   ├── content_agent.py      # Fetches & scores content
│   ├── digest_agent.py       # Formats daily digests
│   ├── feed_agent.py         # Browser-based feed curation
│   └── memory_agent.py       # Manages preference/history files
├── tools/                    # ADK tool functions
│   ├── hackernews_tools.py   # Hacker News API client
│   ├── rss_tools.py          # RSS feed fetcher
│   ├── reddit_tools.py       # Reddit JSON API client
│   ├── scoring_tools.py      # LLM-based content scoring
│   ├── browser_tools.py      # Browser automation (browser-use)
│   └── memory_tools.py       # Read/write markdown memory files
├── sources/                  # Raw data source clients
│   ├── hn_client.py
│   ├── rss_client.py
│   └── reddit_client.py
├── browser/                  # Playwright browser controller
│   ├── controller.py         # Persistent Edge profile management
│   └── computer_use.py       # Gemini Computer Use integration
├── memory/                   # Memory system
│   ├── manager.py            # Read/write/append operations
│   └── schemas.py            # Default file templates
├── memory_data/              # Persistent state (markdown files)
│   ├── preferences.md        # Your interests & weights
│   ├── history.md            # Digest generation log
│   ├── profile.md            # Long-term behavioural patterns
│   └── feed_state.md         # Platform status & muted accounts
├── interfaces/
│   ├── telegram_bot.py       # Telegram bot interface
│   └── live_voice.py         # Voice briefing generation
└── scripts/
    └── start.sh              # Start ADK backend
```

## Tech Stack

- **[Google ADK](https://google.github.io/adk-docs/)** — Agent orchestration framework
- **Gemini 3 Flash** — LLM for reasoning, scoring, and agent coordination
- **[browser-use](https://github.com/browser-use/browser-use)** — AI browser automation for feed curation
- **Playwright** — Browser engine (persistent Edge profiles for social media login)
- **python-telegram-bot** — Telegram bot interface
- **httpx** — Async HTTP client for API communication
- **feedparser** — RSS feed parsing

## The Vision

The long-term vision for Signal is an agent that truly understands your information needs and manages your entire digital information diet:

- **Adaptive learning** — Automatically adjust topic weights based on what you actually engage with over time
- **Cross-platform curation** — Instagram, X, YouTube, LinkedIn, email newsletters — all managed by one agent
- **Bias detection** — Surface when your information diet is becoming one-sided and actively diversify it
- **Proactive briefings** — Don't wait for you to ask. Wake you up with exactly what matters, nothing more
- **Community knowledge** — Share anonymised filtering patterns across users to improve content quality for everyone

The world doesn't need another recommendation algorithm optimising for engagement. It needs a tool that's on your side. Signal is that tool.

---

*Built with Google ADK + Gemini for the Google AI Hackathon 2025.*
