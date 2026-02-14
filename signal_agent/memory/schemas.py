"""Default templates for memory files."""

PREFERENCES_TEMPLATE = """\
# Preferences

## Topics of Interest
| Topic | Weight | Notes |
|-------|--------|-------|
| AI/ML | 0.9 | Especially practical applications, new models, agent frameworks |
| Systems programming | 0.7 | Rust, performance, distributed systems |
| Startups | 0.6 | Founder stories, fundraising, product-market fit |
| Science | 0.5 | Physics, biology breakthroughs |
| Open source | 0.7 | New tools, community drama, licensing |

## Topics to Avoid
| Topic | Reason |
|-------|--------|
| Crypto/Web3 | Not interested unless major technical breakthrough |
| Celebrity gossip | Noise |
| Sports scores | Not relevant |

## Source Priority
| Tier | Sources |
|------|---------|
| High | Hacker News, ArXiv (via RSS) |
| Medium | Tech blogs (via RSS), Reddit r/programming |
| Low | General news RSS |

## RSS Feeds
- https://hnrss.org/newest?points=50
- https://feeds.arstechnica.com/arstechnica/index
- https://www.theverge.com/rss/index.xml

## Content Preferences
- Prefer in-depth technical articles over news summaries
- Prefer primary sources over commentary
- Ideal length: 5-15 minute reads
- Show me contrarian takes, not just consensus views
"""

HISTORY_TEMPLATE = """\
# History

<!-- Daily entries appended automatically -->
"""

PROFILE_TEMPLATE = """\
# Profile

## Interest Vector
<!-- Updated by the agent based on engagement patterns -->

## Behavioral Patterns
- Preferred reading times: not yet learned
- Content length preference: not yet learned
- Engagement style: not yet learned

## Bias Detection
- Echo chamber risk: not yet assessed
- Dominant viewpoints: not yet tracked
- Diversity score: not yet calculated

## Evolution Log
<!-- What changed and why -->
"""

FEED_STATE_TEMPLATE = """\
# Feed State

## Instagram
- Status: not configured
- Last session: never
- Login state: unknown
- Feed health score: N/A

## X.com
- Status: not configured
- Last session: never
- Login state: unknown
- Feed health score: N/A

## Recent Actions
<!-- Per-session action log -->

## Muted Accounts
<!-- Accounts muted by the agent with reasons -->
"""
