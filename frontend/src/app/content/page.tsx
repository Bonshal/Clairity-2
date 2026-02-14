"use client";

import AppShell from "@/components/AppShell";
import { Search, Filter, ExternalLink, ThumbsUp, MessageSquare, Eye, Zap } from "lucide-react";
import { useState, useEffect } from "react";
import { fetchContent, semanticSearch } from "@/lib/api";

const CONTENT_ITEMS = [
    {
        id: 1,
        title: "I built an AI code reviewer that catches bugs GPT-4 misses",
        platform: "reddit",
        author: "u/ml_engineer_42",
        date: "2h ago",
        sentiment: "positive",
        engagement: { upvotes: 847, comments: 234 },
        topics: ["AI code review", "developer tools"],
        isOutlier: true,
    },
    {
        id: 2,
        title: "MCP servers are going to change how we interact with AI models forever",
        platform: "twitter",
        author: "@devtools_weekly",
        date: "4h ago",
        sentiment: "positive",
        engagement: { upvotes: 1240, comments: 89 },
        topics: ["MCP server", "AI integration"],
        isOutlier: true,
    },
    {
        id: 3,
        title: "Comparing DeepSeek R2 vs Llama 4 for production code generation",
        platform: "youtube",
        author: "AI Engineering Hub",
        date: "6h ago",
        sentiment: "neutral",
        engagement: { upvotes: 12400, comments: 445 },
        topics: ["open source LLM", "code generation"],
        isOutlier: false,
    },
    {
        id: 4,
        title: "Why I switched from vibe coding back to traditional development",
        platform: "reddit",
        author: "u/senior_dev_opinions",
        date: "8h ago",
        sentiment: "negative",
        engagement: { upvotes: 623, comments: 512 },
        topics: ["vibe coding", "AI productivity"],
        isOutlier: false,
    },
    {
        id: 5,
        title: "RAG is dead, long live agentic RAG — how retrieval is evolving",
        platform: "twitter",
        author: "@ai_research_daily",
        date: "10h ago",
        sentiment: "positive",
        engagement: { upvotes: 2100, comments: 156 },
        topics: ["RAG pipeline", "AI agents"],
        isOutlier: false,
    },
    {
        id: 6,
        title: "Building production-grade browser automation with AI agents",
        platform: "youtube",
        author: "Code with AI",
        date: "12h ago",
        sentiment: "positive",
        engagement: { upvotes: 8700, comments: 312 },
        topics: ["browser automation", "AI agents"],
        isOutlier: false,
    },
];

export default function ContentPage() {
    const [searchQuery, setSearchQuery] = useState("");
    const [platformFilter, setPlatformFilter] = useState("all");
    const [items, setItems] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadContent() {
            setLoading(true);
            try {
                if (searchQuery.length > 2) {
                    const res = await semanticSearch(searchQuery);
                    // Map semantic search results
                    const mapped = res.results.map((item: any) => ({
                        id: item.id,
                        title: item.title,
                        platform: item.platform,
                        author: item.author || "Unknown",
                        date: "Just now", // Search doesn't usually return date, assume recent or fix in API
                        sentiment: item.sentiment || "neutral",
                        engagement: { upvotes: 0, comments: 0 }, // Search result might lack metrics
                        topics: [],
                        isOutlier: false,
                    }));
                    setItems(mapped);
                } else {
                    const res = await fetchContent(1, 20, platformFilter === "all" ? undefined : platformFilter);
                    const mapped = res.items.map((item: any) => ({
                        id: item.id,
                        title: item.title || item.body?.slice(0, 80) + "...",
                        platform: item.platform,
                        author: item.author || "Unknown",
                        date: new Date(item.fetchedAt).toLocaleDateString(),
                        sentiment: item.sentimentResults?.[0]?.sentiment || "neutral",
                        engagement: {
                            upvotes: item.upvotes || item.likes || 0,
                            comments: item.commentsCount || 0
                        },
                        topics: item.topics || [], // API response doesn't have topics on item directly yet, assume empty or fix API
                        isOutlier: false,
                    }));
                    setItems(mapped);
                }
            } catch (err) {
                console.error("Failed to fetch content:", err);
            } finally {
                setLoading(false);
            }
        }

        // Debounce search slightly
        const timer = setTimeout(loadContent, 500);
        return () => clearTimeout(timer);
    }, [searchQuery, platformFilter]);

    return (
        <AppShell>
            <div className="page-header">
                <h2 className="page-title">
                    Content <span className="gradient-text">Explorer</span>
                </h2>
                <p className="page-subtitle">
                    Browse, search, and analyze indexed items across all platforms
                </p>
            </div>

            {/* Search bar */}
            <div
                style={{
                    display: "flex",
                    gap: 12,
                    marginBottom: 24,
                }}
            >
                <div
                    style={{
                        flex: 1,
                        display: "flex",
                        alignItems: "center",
                        gap: 12,
                        background: "var(--glass-bg)",
                        border: "1px solid var(--glass-border)",
                        borderRadius: "var(--radius-md)",
                        padding: "10px 16px",
                        backdropFilter: "blur(20px)",
                    }}
                >
                    <Search size={18} color="var(--text-muted)" />
                    <input
                        type="text"
                        placeholder="Semantic search across all content..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        style={{
                            flex: 1,
                            background: "transparent",
                            border: "none",
                            outline: "none",
                            color: "var(--text-primary)",
                            fontSize: "0.92rem",
                            fontFamily: "'Inter', sans-serif",
                        }}
                    />
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                    {["all", "reddit", "twitter", "youtube"].map((p) => (
                        <button
                            key={p}
                            className={`btn ${platformFilter === p ? "btn-primary" : "btn-ghost"}`}
                            onClick={() => setPlatformFilter(p)}
                            style={{ textTransform: "capitalize" }}
                        >
                            {p}
                        </button>
                    ))}
                </div>
            </div>

            {/* Content list */}
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {loading && <div style={{ padding: 20, textAlign: "center", color: "var(--text-muted)" }}>Loading content...</div>}

                {!loading && items.length === 0 && (
                    <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>
                        No content found. Try adjusting filters or search.
                    </div>
                )}

                {items.map((item) => (
                    <div
                        key={item.id}
                        className="glass-card"
                        style={{
                            padding: "18px 24px",
                            cursor: "pointer",
                            display: "flex",
                            flexDirection: "column",
                            gap: 10,
                        }}
                    >
                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                            <span className={`tag tag-platform ${item.platform.toLowerCase()}`}>
                                {item.platform === "twitter" ? "X" : item.platform}
                            </span>
                            <span style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
                                {item.author}
                            </span>
                            <span style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginLeft: "auto" }}>
                                {item.date}
                            </span>
                            {item.isOutlier && (
                                <span
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 4,
                                        background: "rgba(192, 132, 252, 0.12)",
                                        color: "#c084fc",
                                        padding: "3px 8px",
                                        borderRadius: 6,
                                        fontSize: "0.72rem",
                                        fontWeight: 600,
                                    }}
                                >
                                    <Zap size={10} /> Viral
                                </span>
                            )}
                        </div>

                        <div style={{ fontSize: "1rem", fontWeight: 600, lineHeight: 1.4 }}>
                            {item.title}
                        </div>

                        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                            {/* Sentiment */}
                            <span
                                style={{
                                    width: 8,
                                    height: 8,
                                    borderRadius: "50%",
                                    background:
                                        item.sentiment === "positive"
                                            ? "var(--positive)"
                                            : item.sentiment === "negative"
                                                ? "var(--negative)"
                                                : "var(--text-muted)",
                                    display: "inline-block",
                                }}
                            />
                            <span style={{ fontSize: "0.78rem", color: "var(--text-muted)", textTransform: "capitalize" }}>
                                {item.sentiment}
                            </span>

                            <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                                <ThumbsUp size={13} />
                                <span style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                                    {item.engagement.upvotes.toLocaleString()}
                                </span>
                            </div>

                            <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                                <MessageSquare size={13} />
                                <span style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                                    {item.engagement.comments}
                                </span>
                            </div>

                            <div style={{ display: "flex", gap: 4, marginLeft: "auto" }}>
                                {item.topics.map((t: string) => (
                                    <span key={t} className="tag">{t}</span>
                                ))}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </AppShell>
    );
}
