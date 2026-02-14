"use client";

import { motion } from "framer-motion";
import type { ContentItem } from "@/lib/types";

interface FocusCardProps {
  item: ContentItem;
  direction: number; // -1 for prev, 1 for next
}

const variants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 300 : -300,
    opacity: 0,
    scale: 0.95,
  }),
  center: { x: 0, opacity: 1, scale: 1 },
  exit: (direction: number) => ({
    x: direction > 0 ? -300 : 300,
    opacity: 0,
    scale: 0.95,
  }),
};

function scoreColor(score: number): string {
  if (score >= 80) return "text-signal-score-green";
  if (score >= 60) return "text-signal-score-yellow";
  return "text-signal-score-blue";
}

export default function FocusCard({ item, direction }: FocusCardProps) {
  return (
    <motion.div
      custom={direction}
      variants={variants}
      initial="enter"
      animate="center"
      exit="exit"
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="glass-card max-w-2xl w-full mx-auto p-8"
    >
      {/* Source + Score */}
      <div className="flex items-center justify-between mb-6">
        <span className="text-sm text-signal-muted">
          {item.source_detail}
        </span>
        <span className={`text-2xl font-mono font-bold ${scoreColor(item.score)}`}>
          {item.score}
        </span>
      </div>

      {/* Title */}
      <h1 className="font-serif text-3xl font-bold text-white mb-4 leading-tight">
        {item.title}
      </h1>

      {/* Summary */}
      <p className="text-lg text-gray-300 mb-6 leading-relaxed">
        {item.summary}
      </p>

      {/* AI Reasoning */}
      <div className="bg-signal-accent/5 border border-signal-accent/20 rounded-lg p-4 mb-6">
        <p className="text-sm text-signal-muted mb-1">Why this matters to you:</p>
        <p className="text-sm text-gray-300">{item.reason}</p>
      </div>

      {/* Topics */}
      <div className="flex gap-2 mb-8">
        {item.topics.map((topic) => (
          <span key={topic} className="text-xs px-2 py-1 rounded bg-signal-accent/10 text-signal-accent">
            {topic}
          </span>
        ))}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-center gap-4">
        <button className="px-6 py-3 rounded-lg border border-signal-border text-signal-muted hover:border-red-500/50 hover:text-red-400 transition-colors">
          Not for me
        </button>
        <button className="px-6 py-3 rounded-lg border border-signal-border text-signal-muted hover:border-signal-accent/50 hover:text-signal-accent transition-colors">
          Save
        </button>
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="px-6 py-3 rounded-lg bg-gradient-to-r from-signal-accent to-signal-accent-blue text-white font-medium hover:opacity-90 transition-opacity"
        >
          Open Source
        </a>
      </div>
    </motion.div>
  );
}
