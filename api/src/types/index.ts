export interface TrendSignal {
    id: string;
    keyword: string;
    platform: "reddit" | "twitter" | "youtube";
    direction: "emerging" | "declining" | "stable" | "viral";
    momentum7d: number;
    momentum30d: number;
    volumeCurrent: number;
    volumePrevious: number;
    confidence: number;
    detectedAt: string;
}

export interface Recommendation {
    id: string;
    title: string;
    contentAngle: string;
    targetAudience: string;
    suggestedFormat: string;
    estimatedEffort: "low" | "medium" | "high";
    confidence: number;
    reasoning: string;
    seoScore: number;
    geoScore: number;
    createdAt: string;
}

export interface ContentItem {
    id: string;
    platform: "reddit" | "twitter" | "youtube";
    platformId: string;
    contentType: string;
    title: string | null;
    body: string | null;
    author: string | null;
    url: string | null;
    likes: number;
    views: number;
    commentsCount: number;
    platformCreatedAt: string;
}

export interface Niche {
    id: string;
    name: string;
    keywords: string[];
    subreddits: string[];
    twitterQueries: string[];
    youtubeQueries: string[];
}

export interface PipelineRun {
    id: string;
    startedAt: string;
    completedAt: string | null;
    status: "running" | "completed" | "failed";
    platformsProcessed: string[];
    itemsProcessed: number;
    evaluationScore: number | null;
}
