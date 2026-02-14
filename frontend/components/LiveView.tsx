"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { CurationAction } from "@/lib/types";

interface LiveViewProps {
  screenshotUrl: string | null;
  actions: CurationAction[];
  isRunning: boolean;
  stats: { processed: number; liked: number; skipped: number; muted: number };
}

function actionColor(action: string): string {
  if (action.toLowerCase().includes("like")) return "text-signal-score-green";
  if (action.toLowerCase().includes("mute")) return "text-red-400";
  if (action.toLowerCase().includes("skip") || action.toLowerCase().includes("scroll")) return "text-signal-muted";
  return "text-signal-score-blue";
}

function actionIcon(action: string): string {
  if (action.toLowerCase().includes("like")) return "\u2713";
  if (action.toLowerCase().includes("mute")) return "\u2717";
  if (action.toLowerCase().includes("skip") || action.toLowerCase().includes("scroll")) return "\u2193";
  return "\u25CF";
}

export default function LiveView({ screenshotUrl, actions, isRunning, stats }: LiveViewProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 h-[calc(100vh-8rem)]">
      {/* Browser view (left 60%) */}
      <div className="lg:col-span-3 glass-card p-4 flex flex-col">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-signal-muted">Live Browser</h3>
          {isRunning && (
            <motion.div
              className="flex items-center gap-2"
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <div className="w-2 h-2 rounded-full bg-red-500" />
              <span className="text-xs text-red-400 font-mono">LIVE</span>
            </motion.div>
          )}
        </div>

        <div className="flex-1 bg-signal-bg rounded-lg overflow-hidden flex items-center justify-center">
          {screenshotUrl ? (
            <img src={screenshotUrl} alt="Browser view" className="w-full h-full object-contain" />
          ) : (
            <div className="text-center text-signal-muted">
              <svg className="w-20 h-20 mx-auto mb-4 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <p className="text-lg">Ready to curate</p>
              <p className="text-sm mt-1">Select a platform and hit start</p>
            </div>
          )}
        </div>
      </div>

      {/* Activity log (right 40%) */}
      <div className="lg:col-span-2 glass-card p-4 flex flex-col">
        <h3 className="text-sm font-medium text-signal-muted mb-3">AI Activity Log</h3>

        {/* Action log */}
        <div className="flex-1 overflow-y-auto space-y-2 mb-4">
          <AnimatePresence>
            {actions.map((action, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-start gap-2 text-sm"
              >
                <span className={`font-mono ${actionColor(action.action)}`}>
                  {actionIcon(action.action)}
                </span>
                <span className="text-gray-300">{action.reasoning}</span>
              </motion.div>
            ))}
          </AnimatePresence>

          {actions.length === 0 && (
            <p className="text-signal-muted text-sm">No actions yet. Start a curation session.</p>
          )}
        </div>

        {/* Divider */}
        <div className="border-t border-signal-border pt-4">
          <h4 className="text-xs font-medium text-signal-muted mb-2">Session Stats</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="flex justify-between">
              <span className="text-signal-muted">Posts:</span>
              <span className="text-white font-mono">{stats.processed}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-signal-score-green">Liked:</span>
              <span className="text-white font-mono">{stats.liked}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-signal-muted">Skipped:</span>
              <span className="text-white font-mono">{stats.skipped}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-red-400">Muted:</span>
              <span className="text-white font-mono">{stats.muted}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
