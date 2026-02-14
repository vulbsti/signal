"use client";

import { motion } from "framer-motion";

interface SignalScoreProps {
  totalScanned: number;
  totalCurated: number;
  isLoading?: boolean;
}

export default function SignalScore({ totalScanned, totalCurated, isLoading }: SignalScoreProps) {
  const pct = totalScanned > 0 ? ((1 - totalCurated / totalScanned) * 100).toFixed(1) : "0";

  return (
    <div className="glass-card px-6 py-4 mb-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        {isLoading ? (
          <div className="flex items-center gap-2">
            <motion.div
              className="w-2 h-2 rounded-full bg-signal-accent"
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
            <span className="text-sm text-signal-muted">Scanning sources...</span>
          </div>
        ) : (
          <>
            <span className="text-sm text-signal-muted">
              <span className="text-white font-semibold">{totalScanned}</span> scanned
            </span>
            <svg className="w-4 h-4 text-signal-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
            <span className="text-sm text-signal-muted">
              <span className="text-white font-semibold">{totalCurated}</span> curated
            </span>
          </>
        )}
      </div>

      {!isLoading && totalScanned > 0 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-2"
        >
          <span className="text-xs text-signal-muted">Noise filtered:</span>
          <span className="text-sm font-mono font-semibold text-signal-accent">{pct}%</span>
        </motion.div>
      )}
    </div>
  );
}
