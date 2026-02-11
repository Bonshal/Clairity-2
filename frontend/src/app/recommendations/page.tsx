"use client";

import AppShell from "@/components/AppShell";
import { Lightbulb, ArrowUpRight, Search, Target, Globe, Sparkles } from "lucide-react";

const RECS = [
    {
        title: "Complete Guide to AI Code Review Tools in 2026",
        angle: "Compare top 8 AI code review tools with hands-on benchmarks. Cover accuracy, speed, language support, and pricing.",
        format: "Guide",
        audience: "Senior developers & tech leads",
        effort: "medium",
        confidence: 0.94,
        seoScore: 0.89,
        geoScore: 0.82,
        keywords: ["AI code review", "code review tools", "automated code review"],
        platforms: ["reddit", "youtube"],
    },
    {
        title: "How to Build MCP Server Integrations from Scratch",
        angle: "Step-by-step tutorial covering the Model Context Protocol specification, building custom tools, and connecting to popular AI assistants.",
        format: "Tutorial",
        audience: "AI developers & tool builders",
        effort: "high",
        confidence: 0.91,
        seoScore: 0.92,
        geoScore: 0.88,
        keywords: ["MCP server", "model context protocol", "AI tool integration"],
        platforms: ["reddit", "twitter", "youtube"],
    },
    {
        title: "Open-Source LLM Alternatives: The Definitive Comparison",
        angle: "In-depth comparison of Llama 4, Mistral, Qwen, and DeepSeek. Benchmark on coding, reasoning, and creative tasks with real examples.",
        format: "Comparison",
        audience: "ML engineers & AI enthusiasts",
        effort: "high",
        confidence: 0.87,
        seoScore: 0.85,
        geoScore: 0.79,
        keywords: ["open source LLM", "LLM comparison", "best open source AI"],
        platforms: ["reddit", "youtube"],
    },
    {
        title: "Vibe Coding: Why AI Pair Programming is Changing Everything",
        angle: "Explore the emerging 'vibe coding' workflow — using AI to describe intent and let the model write code. Include productivity data and developer sentiment.",
        format: "Blog",
        audience: "Junior-mid developers",
        effort: "low",
        confidence: 0.82,
        seoScore: 0.78,
        geoScore: 0.85,
        keywords: ["vibe coding", "AI pair programming", "coding with AI"],
        platforms: ["twitter"],
    },
    {
        title: "RAG Pipeline Optimization: 7 Techniques That Actually Work",
        angle: "Advanced techniques for improving RAG accuracy: hybrid search, reranking, chunk optimization, query decomposition, and evaluation frameworks.",
        format: "Guide",
        audience: "AI engineers building RAG systems",
        effort: "medium",
        confidence: 0.78,
        seoScore: 0.88,
        geoScore: 0.76,
        keywords: ["RAG optimization", "RAG pipeline", "retrieval augmented generation"],
        platforms: ["reddit"],
    },
];

const formatColors: Record<string, string> = {
    Guide: "#00e5c8",
    Tutorial: "#0ea5e9",
    Comparison: "#c084fc",
    Blog: "#fbbf24",
    Video: "#ff4444",
};

export default function RecommendationsPage() {
    return (
        <AppShell>
            <div className="page-header">
                <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
                    <div>
                        <h2 className="page-title">
                            Content <span className="gradient-text">Recommendations</span>
                        </h2>
                        <p className="page-subtitle">
                            AI-generated content strategies with SEO & GEO optimization scores
                        </p>
                    </div>
                    <button className="btn btn-primary">
                        <Sparkles size={16} /> Generate New
                    </button>
                </div>
            </div>

            <div className="rec-grid">
                {RECS.map((rec, i) => (
                    <div key={i} className="rec-card">
                        {/* Format badge */}
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                            <span
                                className="rec-format"
                                style={{ borderColor: `${formatColors[rec.format]}30`, color: formatColors[rec.format] }}
                            >
                                {rec.format}
                            </span>
                            <div style={{ display: "flex", gap: 4 }}>
                                {rec.platforms.map((p) => (
                                    <span key={p} className={`tag tag-platform ${p}`} style={{ fontSize: "0.65rem", padding: "2px 6px" }}>
                                        {p === "twitter" ? "X" : p}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* Title */}
                        <div className="rec-title">{rec.title}</div>

                        {/* Angle */}
                        <div className="rec-angle">{rec.angle}</div>

                        {/* Keywords */}
                        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                            {rec.keywords.map((kw) => (
                                <span key={kw} className="tag">{kw}</span>
                            ))}
                        </div>

                        {/* Audience + Effort */}
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", color: "var(--text-muted)" }}>
                            <span>{rec.audience}</span>
                            <span style={{
                                textTransform: "capitalize",
                                color: rec.effort === "low" ? "var(--positive)" : rec.effort === "high" ? "var(--warning)" : "var(--text-secondary)",
                            }}>
                                {rec.effort} effort
                            </span>
                        </div>

                        {/* Score pills */}
                        <div className="rec-scores">
                            <span className="score-pill seo">
                                <Target size={12} /> SEO {Math.round(rec.seoScore * 100)}
                            </span>
                            <span className="score-pill geo">
                                <Globe size={12} /> GEO {Math.round(rec.geoScore * 100)}
                            </span>
                            <span className="score-pill confidence">
                                <Sparkles size={12} /> {Math.round(rec.confidence * 100)}%
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </AppShell>
    );
}
