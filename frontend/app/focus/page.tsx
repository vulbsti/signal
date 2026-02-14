"use client";

import { useState, useEffect, useCallback } from "react";
import { AnimatePresence } from "framer-motion";
import FocusCard from "@/components/FocusCard";
import type { ContentItem } from "@/lib/types";

// Same mock data — in production, this comes from shared state or ADK
const MOCK_ITEMS: ContentItem[] = [
  {
    title: "Google Just Open-Sourced Their Internal Agent Framework",
    url: "#", source: "hackernews", source_detail: "Hacker News",
    score: 94, tier: "top",
    summary: "Google released AgentCore, the internal framework powering Gemini's agentic capabilities. Full open-source release with production-ready tools for building multi-agent systems.",
    reason: "Matches AI + agents interest at 94%. High-quality source with 342 upvotes in 2h.",
    topics: ["ai", "agents", "open-source"], timestamp: "2h ago", id: 1,
  },
  {
    title: "Transformer Alternatives Are Finally Here",
    url: "#", source: "hackernews", source_detail: "Hacker News",
    score: 91, tier: "top",
    summary: "State-space models and hybrid architectures are showing competitive results on language tasks while using 10x less compute. Mamba-2 and RWKV-7 lead the charge.",
    reason: "Strong ML research match. Novel architectures are a high-interest topic.",
    topics: ["ml", "research", "transformers"], timestamp: "4h ago", id: 2,
  },
  {
    title: "Building AI Agents That Actually Work",
    url: "#", source: "hackernews", source_detail: "Hacker News",
    score: 88, tier: "top",
    summary: "Practical lessons from deploying AI agents in production: tool design matters more than model choice, and reliability beats capability every time.",
    reason: "Core AI + agents interest. Practical insights from production deployment.",
    topics: ["ai", "agents", "production"], timestamp: "1h ago", id: 6,
  },
];

export default function FocusPage() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState(0);
  const items = MOCK_ITEMS; // Replace with shared state

  const goNext = useCallback(() => {
    if (currentIndex < items.length - 1) {
      setDirection(1);
      setCurrentIndex((prev) => prev + 1);
    }
  }, [currentIndex, items.length]);

  const goPrev = useCallback(() => {
    if (currentIndex > 0) {
      setDirection(-1);
      setCurrentIndex((prev) => prev - 1);
    }
  }, [currentIndex]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === "ArrowDown") goNext();
      if (e.key === "ArrowLeft" || e.key === "ArrowUp") goPrev();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [goNext, goPrev]);

  const item = items[currentIndex];

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-8rem)]">
      {/* Progress bar */}
      <div className="w-full max-w-2xl mb-8 flex items-center gap-3">
        <span className="text-sm text-signal-muted font-mono">
          {currentIndex + 1} / {items.length}
        </span>
        <div className="flex-1 h-1 bg-signal-surface rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-signal-accent to-signal-accent-blue rounded-full transition-all duration-300"
            style={{ width: `${((currentIndex + 1) / items.length) * 100}%` }}
          />
        </div>
        <span className="text-sm text-signal-muted">
          Use <kbd className="px-1.5 py-0.5 rounded bg-signal-surface text-xs">arrow keys</kbd>
        </span>
      </div>

      {/* Card */}
      <AnimatePresence mode="wait" custom={direction}>
        <FocusCard key={item.id} item={item} direction={direction} />
      </AnimatePresence>
    </div>
  );
}
