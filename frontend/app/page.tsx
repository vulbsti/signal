"use client";

import { useState, useCallback } from "react";
import FeedGrid from "@/components/FeedGrid";
import SignalScore from "@/components/SignalScore";
import type { ContentItem, DigestResponse } from "@/lib/types";
import { sendMessage } from "@/lib/adk-client";

// Mock data for development — remove when ADK is connected
const MOCK_ITEMS: ContentItem[] = [
  {
    title: "Google Just Open-Sourced Their Internal Agent Framework",
    url: "https://news.ycombinator.com/item?id=1",
    source: "hackernews",
    source_detail: "Hacker News",
    score: 94,
    tier: "top",
    summary: "Google released AgentCore, the internal framework powering Gemini's agentic capabilities. Full open-source release with production-ready tools.",
    reason: "Matches AI + agents interest at 94%. High-quality source with 342 upvotes.",
    topics: ["ai", "agents", "open-source"],
    timestamp: "2h ago",
    id: 1,
  },
  {
    title: "Transformer Alternatives Are Finally Here",
    url: "https://news.ycombinator.com/item?id=2",
    source: "hackernews",
    source_detail: "Hacker News",
    score: 91,
    tier: "top",
    summary: "State-space models and hybrid architectures are showing competitive results on language tasks while using 10x less compute.",
    reason: "Strong ML research match. Novel architectures are high interest.",
    topics: ["ml", "research", "transformers"],
    timestamp: "4h ago",
    id: 2,
  },
  {
    title: "Why RSS Is Making a Comeback in 2026",
    url: "https://example.com/rss-comeback",
    source: "rss",
    source_detail: "Simon Willison's Blog",
    score: 78,
    tier: "strong",
    summary: "The algorithmic feed broke trust. RSS never did. A look at the resurgence of RSS readers and the indie web movement.",
    reason: "Matches open web + tech culture interest. From followed person.",
    topics: ["web", "rss", "open-source"],
    timestamp: "6h ago",
    id: 3,
  },
  {
    title: "PostgreSQL 18: Performance Deep Dive",
    url: "https://news.ycombinator.com/item?id=4",
    source: "hackernews",
    source_detail: "Hacker News",
    score: 75,
    tier: "strong",
    summary: "Benchmarks show 40% improvement in concurrent workloads with new parallel query optimizer and improved VACUUM.",
    reason: "Systems programming interest. Solid technical depth.",
    topics: ["databases", "postgres", "performance"],
    timestamp: "3h ago",
    id: 4,
  },
  {
    title: "The State of WebAssembly in 2026",
    url: "https://example.com/wasm-2026",
    source: "rss",
    source_detail: "The Pragmatic Engineer",
    score: 72,
    tier: "strong",
    summary: "WASM component model is production-ready. Major frameworks now support WASM targets. Server-side WASM is the next frontier.",
    reason: "Web dev + systems crossover. From medium-priority source.",
    topics: ["wasm", "web", "systems"],
    timestamp: "8h ago",
    id: 5,
  },
  {
    title: "Building AI Agents That Actually Work",
    url: "https://news.ycombinator.com/item?id=6",
    source: "hackernews",
    source_detail: "Hacker News",
    score: 88,
    tier: "top",
    summary: "Practical lessons from deploying AI agents in production: tool design matters more than model choice, and reliability beats capability.",
    reason: "Core AI + agents interest. Practical insights from production deployment.",
    topics: ["ai", "agents", "production"],
    timestamp: "1h ago",
    id: 6,
  },
];

export default function FeedPage() {
  const [items, setItems] = useState<ContentItem[]>(MOCK_ITEMS);
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState({ total_scanned: 847, total_curated: 6 });

  const fetchDigest = useCallback(async () => {
    setIsLoading(true);
    setItems([]);
    try {
      const response = await sendMessage("Give me my digest");
      // Parse JSON from agent response
      const jsonMatch = response.match(/```json\n?([\s\S]*?)\n?```/) || response.match(/(\{[\s\S]*\})/);
      if (jsonMatch) {
        const digest: DigestResponse = JSON.parse(jsonMatch[1]);
        setStats({
          total_scanned: digest.stats.total_scanned,
          total_curated: digest.stats.total_curated,
        });
        // Stream items in with delay for animation
        for (let i = 0; i < digest.items.length; i++) {
          await new Promise((r) => setTimeout(r, 150));
          setItems((prev) => [...prev, digest.items[i]]);
        }
      }
    } catch (err) {
      console.error("Failed to fetch digest:", err);
      // Fall back to mock data in development
      setItems(MOCK_ITEMS);
      setStats({ total_scanned: 847, total_curated: MOCK_ITEMS.length });
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleCardClick = (item: ContentItem, index: number) => {
    window.location.href = `/focus?start=${index}`;
  };

  return (
    <div>
      {/* Stats banner */}
      <SignalScore
        totalScanned={stats.total_scanned}
        totalCurated={stats.total_curated}
        isLoading={isLoading}
      />

      {/* Refresh button */}
      <div className="flex justify-end mb-4">
        <button
          onClick={fetchDigest}
          disabled={isLoading}
          className="px-4 py-2 text-sm font-medium rounded-lg bg-gradient-to-r from-signal-accent to-signal-accent-blue text-white hover:opacity-90 transition-opacity disabled:opacity-50"
        >
          {isLoading ? "Generating..." : "Generate Digest"}
        </button>
      </div>

      {/* Feed grid */}
      <FeedGrid items={items} onCardClick={handleCardClick} />
    </div>
  );
}
