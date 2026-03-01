"use client";

import { motion } from "framer-motion";
import type { ContentItem } from "@/lib/types";

interface ContentCardProps {
  item: ContentItem;
  index: number;
  onClick?: () => void;
}

function scoreColor(score: number): string {
  if (score >= 80) return "text-signal-score-green border-signal-score-green/30 bg-signal-score-green/10";
  if (score >= 60) return "text-signal-score-yellow border-signal-score-yellow/30 bg-signal-score-yellow/10";
  return "text-signal-score-blue border-signal-score-blue/30 bg-signal-score-blue/10";
}

function sourceIcon(source: string): string {
  switch (source) {
    case "hackernews": return "HN";
    case "rss": return "RSS";
    case "reddit": return "R";
    default: return "?";
  }
}

export default function ContentCard({ item, index, onClick }: ContentCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.4, ease: "easeOut" }}
      onClick={onClick}
      className="glass-card p-5 cursor-pointer hover:border-signal-accent/40 transition-all duration-200 group"
    >
      {/* Score badge */}
      <div className="flex items-center justify-between mb-3">
        <span className={`text-xs font-mono px-2 py-0.5 rounded border ${scoreColor(item.score)}`}>
          {item.score}
        </span>
        <span className="text-xs text-signal-muted">
          {item.timestamp}
        </span>
      </div>

      {/* Title */}
      <h3 className="font-serif text-lg font-bold text-white mb-2 group-hover:text-signal-accent transition-colors leading-tight">
        {item.title}
      </h3>

      {/* Summary */}
      <p className="text-sm text-gray-400 mb-3 line-clamp-2">
        {item.summary}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono px-1.5 py-0.5 rounded bg-signal-surface text-signal-muted">
            {sourceIcon(item.source)}
          </span>
          <span className="text-xs text-signal-muted">{item.source_detail}</span>
        </div>
        <div className="flex gap-1">
          {item.topics.slice(0, 3).map((topic) => (
            <span key={topic} className="text-xs px-1.5 py-0.5 rounded bg-signal-accent/10 text-signal-accent">
              {topic}
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
