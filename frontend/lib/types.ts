export interface ContentItem {
  title: string;
  url: string;
  source: "hackernews" | "rss" | "reddit";
  source_detail: string;
  score: number;
  tier: "top" | "strong" | "peripheral";
  summary: string;
  reason: string;
  topics: string[];
  timestamp: string;
  id?: string | number;
}

export interface DigestResponse {
  stats: {
    total_scanned: number;
    total_curated: number;
    noise_filtered_pct: number;
  };
  items: ContentItem[];
}

export interface CurationAction {
  action: string;
  reasoning: string;
  result?: string;
  x?: number;
  y?: number;
}

export interface CurationReport {
  platform: string;
  posts_processed: number;
  actions: {
    liked: number;
    skipped: number;
    muted: number;
  };
  feed_health_change: string;
  actions_log: CurationAction[];
}

export type ViewMode = "feed" | "focus" | "live";
