"use client";

import { AnimatePresence } from "framer-motion";
import ContentCard from "./ContentCard";
import type { ContentItem } from "@/lib/types";

interface FeedGridProps {
  items: ContentItem[];
  onCardClick?: (item: ContentItem, index: number) => void;
}

export default function FeedGrid({ items, onCardClick }: FeedGridProps) {
  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-signal-muted">
        <svg className="w-16 h-16 mb-4 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
        </svg>
        <p className="text-lg">No items yet</p>
        <p className="text-sm mt-1">Click refresh or wait for your digest to generate</p>
      </div>
    );
  }

  return (
    <div className="columns-1 md:columns-2 lg:columns-3 gap-4 space-y-4">
      <AnimatePresence>
        {items.map((item, index) => (
          <div key={item.id || item.title} className="break-inside-avoid">
            <ContentCard
              item={item}
              index={index}
              onClick={() => onCardClick?.(item, index)}
            />
          </div>
        ))}
      </AnimatePresence>
    </div>
  );
}
