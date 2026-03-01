"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import type { ViewMode } from "@/lib/types";

const views: { mode: ViewMode; label: string; href: string }[] = [
  { mode: "feed", label: "Feed", href: "/" },
  { mode: "focus", label: "Focus", href: "/focus" },
  { mode: "live", label: "AI Live", href: "/live" },
];

export default function NavBar() {
  const pathname = usePathname();
  const currentView = pathname === "/" ? "feed" : pathname.slice(1) as ViewMode;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-card border-t-0 border-x-0 rounded-none">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-signal-accent to-signal-accent-blue flex items-center justify-center">
            <span className="text-white font-bold text-sm">S</span>
          </div>
          <span className="text-lg font-semibold text-white tracking-tight">
            Signal Flow
          </span>
        </div>

        {/* View toggles */}
        <div className="flex items-center gap-1 bg-signal-surface/50 rounded-lg p-1">
          {views.map(({ mode, label, href }) => (
            <Link key={mode} href={href}>
              <button
                className={`relative px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  currentView === mode ? "text-white" : "text-signal-muted hover:text-gray-300"
                }`}
              >
                {currentView === mode && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-0 bg-gradient-to-r from-signal-accent/20 to-signal-accent-blue/20 rounded-md border border-signal-accent/30"
                    transition={{ type: "spring", duration: 0.4 }}
                  />
                )}
                <span className="relative z-10">{label}</span>
              </button>
            </Link>
          ))}
        </div>

        {/* Right controls */}
        <div className="flex items-center gap-3">
          {/* Voice button */}
          <button
            className="w-10 h-10 rounded-full bg-signal-surface border border-signal-border flex items-center justify-center hover:border-signal-accent/50 transition-colors"
            title="Voice briefing"
          >
            <svg className="w-5 h-5 text-signal-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </button>
          {/* Settings */}
          <button
            className="w-10 h-10 rounded-full bg-signal-surface border border-signal-border flex items-center justify-center hover:border-signal-accent/50 transition-colors"
            title="Settings"
          >
            <svg className="w-5 h-5 text-signal-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>
      </div>
    </nav>
  );
}
