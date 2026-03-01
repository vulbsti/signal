"use client";

import { useState, useCallback } from "react";
import LiveView from "@/components/LiveView";
import { sendMessage } from "@/lib/adk-client";
import type { CurationAction, CurationReport } from "@/lib/types";

export default function LivePage() {
  const [isRunning, setIsRunning] = useState(false);
  const [platform, setPlatform] = useState<"instagram" | "twitter">("instagram");
  const [screenshotUrl, setScreenshotUrl] = useState<string | null>(null);
  const [actions, setActions] = useState<CurationAction[]>([]);
  const [stats, setStats] = useState({ processed: 0, liked: 0, skipped: 0, muted: 0 });

  const startCuration = useCallback(async () => {
    setIsRunning(true);
    setActions([]);
    setStats({ processed: 0, liked: 0, skipped: 0, muted: 0 });

    try {
      const response = await sendMessage(`Curate my ${platform}`);
      const jsonMatch = response.match(/```json\n?([\s\S]*?)\n?```/) || response.match(/(\{[\s\S]*\})/);
      if (jsonMatch) {
        const report: CurationReport = JSON.parse(jsonMatch[1]);
        // Stream actions in with delay for visual effect
        for (const action of report.actions_log) {
          await new Promise((r) => setTimeout(r, 500));
          setActions((prev) => [...prev, action]);
        }
        setStats({
          processed: report.posts_processed,
          liked: report.actions.liked,
          skipped: report.actions.skipped,
          muted: report.actions.muted,
        });
      }
    } catch (err) {
      console.error("Curation failed:", err);
      // Mock actions for development
      const mockActions: CurationAction[] = [
        { action: "scroll_down", reasoning: "Analyzing feed..." },
        { action: "like", reasoning: "Liked: @karpathy ML research post — matches AI interest" },
        { action: "scroll_down", reasoning: "Skipped: promotional content (score: 15)" },
        { action: "mute", reasoning: "Muted: @rage_account — 3rd rage bait post detected" },
        { action: "like", reasoning: "Liked: @nature documentary clip — diversity balance" },
        { action: "scroll_down", reasoning: "Skipped: engagement bait (score: 8)" },
        { action: "like", reasoning: "Liked: @simonw open-source project — from followed people" },
      ];
      for (const action of mockActions) {
        await new Promise((r) => setTimeout(r, 800));
        setActions((prev) => [...prev, action]);
      }
      setStats({ processed: 7, liked: 3, skipped: 2, muted: 1 });
    } finally {
      setIsRunning(false);
    }
  }, [platform]);

  return (
    <div>
      {/* Controls bar */}
      <div className="glass-card px-6 py-4 mb-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value as "instagram" | "twitter")}
            className="bg-signal-surface text-white text-sm rounded-lg px-3 py-2 border border-signal-border"
            disabled={isRunning}
          >
            <option value="instagram">Instagram</option>
            <option value="twitter">X / Twitter</option>
          </select>
        </div>
        <button
          onClick={startCuration}
          disabled={isRunning}
          className={`px-6 py-2 text-sm font-medium rounded-lg transition-all ${
            isRunning
              ? "bg-red-500/20 text-red-400 border border-red-500/30"
              : "bg-gradient-to-r from-signal-accent to-signal-accent-blue text-white hover:opacity-90"
          }`}
        >
          {isRunning ? "Curating..." : `Curate ${platform === "instagram" ? "Instagram" : "X"}`}
        </button>
      </div>

      {/* Live view */}
      <LiveView
        screenshotUrl={screenshotUrl}
        actions={actions}
        isRunning={isRunning}
        stats={stats}
      />
    </div>
  );
}
