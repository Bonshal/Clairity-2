/**
 * API Client configuration for the Market Research Platform.
 *
 * In development, the Next.js frontend runs on :3000 and the
 * Express API on :3001. In production, both sit behind Nginx so
 * the API is served from /api on the same origin.
 */

const API_BASE =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001/api";

export interface APIError {
    error: string;
    message?: string;
}

/**
 * Typed fetch wrapper with error handling.
 */
async function apiFetch<T>(
    path: string,
    options?: RequestInit
): Promise<T> {
    const url = `${API_BASE}${path}`;
    const res = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options?.headers,
        },
    });

    if (!res.ok) {
        const errorBody = await res.json().catch(() => ({ error: res.statusText }));
        throw new Error(errorBody.message || errorBody.error || `API error ${res.status}`);
    }

    return res.json();
}

// ─── Dashboard ──────────────────────────────────────────────

export async function fetchDashboardKPIs() {
    return apiFetch<{
        totalContent: number;
        emergingTrends: number;
        viralSignals: number;
        avgSentiment: number;
        avgEngagement?: number;
        opportunityScore?: number;
        activePlatforms?: number;
        trendCount?: number;
        sentimentCounts?: { positive: number; neutral: number; negative: number };
        platformCounts?: Array<{
            platform: string;
            count: number;
            sentiment: number;
        }>;
    }>("/dashboard/kpis");
}

export async function fetchDashboardAlerts() {
    return apiFetch<{
        alerts: Array<{
            id: string;
            keyword: string;
            direction: string;
            platform: string;
            detectedAt: string;
        }>;
    }>("/dashboard/alerts");
}

export async function fetchDashboardHistory() {
    return apiFetch<{
        timeline: Array<{
            day: string;
            reddit: number;
            twitter: number;
            youtube: number;
        }>;
    }>("/dashboard/history");
}

// ─── Trends ─────────────────────────────────────────────────

export async function fetchTopTrends(limit = 20) {
    return apiFetch<{
        trends: Array<{
            keyword: string;
            direction: string;
            momentum7d: number;
            momentum30d: number;
            volumeCurrent: number;
            confidence: number;
            platforms: string[];
        }>;
    }>(`/trends/top?limit=${limit}`);
}

export async function fetchTrendTimeline(keyword?: string) {
    const params = keyword ? `?keyword=${encodeURIComponent(keyword)}` : "";
    return apiFetch<{
        timeline: Array<{ date: string; volume: number; emerging: number }>;
    }>(`/trends/timeline${params}`);
}

export async function fetchTrendDetail(keyword: string) {
    return apiFetch<{
        keyword: string;
        direction: string;
        momentum7d: number;
        momentum30d: number;
        volumeCurrent: number;
        volumePrevious: number;
        zScore: number;
        confidence: number;
        relatedKeywords: string[];
        platformBreakdown: Record<string, number>;
    }>(`/trends/${encodeURIComponent(keyword)}`);
}

// ─── Recommendations ────────────────────────────────────────

export async function fetchRecommendations(page = 1, limit = 20) {
    return apiFetch<{
        recommendations: Array<{
            id: string;
            title: string;
            contentAngle: string;
            targetAudience: string;
            suggestedFormat: string;
            confidence: number;
            seo: { primaryKeyword: string; seoScore: number };
            geo: { geoScore: number };
        }>;
        total: number;
    }>(`/recommendations?page=${page}&limit=${limit}`);
}

export async function fetchRecommendationDetail(id: string) {
    return apiFetch<{
        id: string;
        title: string;
        contentAngle: string;
        targetAudience: string;
        suggestedFormat: string;
        confidence: number;
        reasoning: string;
        seo: {
            primaryKeyword: string;
            longTailKeywords: string[];
            keywordIntent: string;
            titleVariants: string[];
            metaDescription: string;
            seoScore: number;
        };
        geo: {
            keyEntities: string[];
            citationWorthyClaims: number;
            recommendedStructure: string;
            faqSuggestions: Array<{ question: string; answer: string }>;
            schemaMarkup: string[];
            geoScore: number;
        };
    }>(`/recommendations/${id}`);
}

export async function generateRecommendations() {
    return apiFetch<{ jobId: string; status: string }>("/recommendations/generate", {
        method: "POST",
    });
}

// ─── Content ────────────────────────────────────────────────

export async function fetchContent(page = 1, limit = 20, platform?: string) {
    let path = `/content?page=${page}&limit=${limit}`;
    if (platform) path += `&platform=${platform}`;
    return apiFetch<{
        items: Array<{
            id: string;
            title: string;
            platform: string;
            author: string;
            sentiment: string;
            engagementScore: number;
            createdAt: string;
            topics: string[];
        }>;
        total: number;
    }>(path);
}

export async function semanticSearch(query: string, limit = 20) {
    return apiFetch<{
        results: Array<{
            id: string;
            title: string;
            platform: string;
            similarity: number;
            sentiment: string;
        }>;
    }>(`/content/search?q=${encodeURIComponent(query)}&limit=${limit}`);
}

export async function fetchViralOutliers(limit = 10) {
    return apiFetch<{
        outliers: Array<{
            id: string;
            title: string;
            platform: string;
            engagementScore: number;
            anomalyScore: number;
        }>;
    }>(`/content/outliers?limit=${limit}`);
}

// ─── SEO & GEO ──────────────────────────────────────────────

export async function fetchSEOKeywords() {
    return apiFetch<{
        keywords: Array<{
            keyword: string;
            volume: number;
            difficulty: number;
            opportunity: number;
            intent: string;
            trend: string;
        }>;
    }>("/seo/keywords");
}

export async function fetchGEOAnalysis(recommendationId: string) {
    return apiFetch<{
        geoScore: number;
        keyEntities: string[];
        citationWorthyClaims: number;
        faqSuggestions: Array<{ question: string; answer: string }>;
        schemaMarkup: string[];
        recommendedStructure: string;
    }>(`/geo/analysis/${recommendationId}`);
}

// ─── Pipeline ───────────────────────────────────────────────

export async function triggerPipeline(nicheId?: string) {
    return apiFetch<{ runId: string; status: string }>("/pipeline/trigger", {
        method: "POST",
        body: JSON.stringify({ niche_id: nicheId }),
    });
}

export async function fetchPipelineStatus(runId: string) {
    return apiFetch<{
        runId: string;
        status: string;
        agents: Array<{
            name: string;
            status: string;
            startedAt?: string;
            completedAt?: string;
            duration?: string;
        }>;
        itemsProcessed: number;
        evaluationScore?: number;
        logs?: Array<{
            timestamp: string;
            step: string;
            status: string;
            message: string;
        }>;
    }>(`/pipeline/status/${runId}`);
}

export async function fetchPipelineHistory(limit = 10) {
    return apiFetch<{
        runs: Array<{
            runId: string;
            status: string;
            startedAt: string;
            completedAt?: string;
            duration: string;
            itemsProcessed: number;
            evaluationScore?: number;
            platforms: string[];
        }>;
    }>(`/pipeline/history?limit=${limit}`);
}

// ─── Niches ─────────────────────────────────────────────────

export async function fetchNiches() {
    return apiFetch<{
        niches: Array<{
            id: string;
            name: string;
            keywords: string[];
            active: boolean;
        }>;
    }>("/niches");
}

export async function createNiche(data: { name: string; keywords: string[] }) {
    return apiFetch<{ id: string; name: string; keywords: string[]; active: boolean }>("/niches", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export async function updateNiche(id: string, data: { name?: string; keywords?: string[]; active?: boolean }) {
    return apiFetch<{ id: string; name: string; keywords: string[]; active: boolean }>(`/niches/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
}

export async function deleteNiche(id: string) {
    return apiFetch<{ success: boolean }>(`/niches/${id}`, { method: "DELETE" });
}
