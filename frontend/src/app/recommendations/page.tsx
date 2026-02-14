"use client";

import AppShell from "@/components/AppShell";
import { Lightbulb, ArrowUpRight, Search, Target, Globe, Sparkles } from "lucide-react";
import { useState, useEffect } from "react";
import { fetchRecommendations, generateRecommendations } from "@/lib/api";

const formatColors: Record<string, string> = {
    Guide: "#00e5c8",
    Tutorial: "#0ea5e9",
    Comparison: "#c084fc",
    Blog: "#fbbf24",
    Video: "#ff4444",
};

export default function RecommendationsPage() {
    const [recs, setRecs] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    async function loadData() {
        setLoading(true);
        try {
            const res = await fetchRecommendations();
            const mapped = res.recommendations.map(r => ({
                title: r.title,
                angle: r.contentAngle,
                format: r.suggestedFormat,
                audience: r.targetAudience,
                effort: "medium", // API doesn't return effort yet
                confidence: r.confidence || 0.85,
                seoScore: r.seo?.seoScore || 0,
                geoScore: r.geo?.geoScore || 0,
                keywords: [r.seo?.primaryKeyword].filter(Boolean) as string[],
                platforms: ["twitter", "linkedin"], // default
            }));
            setRecs(mapped);
        } catch (err) {
            console.error("Failed to load recommendations:", err);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadData();
    }, []);

    const handleGenerate = async () => {
        setGenerating(true);
        try {
            await generateRecommendations();
            alert("Recommendations generation triggered! Check back in a few minutes.");
        } catch (err) {
            console.error("Failed to trigger generation:", err);
            alert("Failed to trigger generation");
        } finally {
            setGenerating(false);
        }
    };

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
                    <button
                        className="btn btn-primary"
                        onClick={handleGenerate}
                        disabled={generating}
                    >
                        <Sparkles size={16} /> {generating ? "Generating..." : "Generate New"}
                    </button>
                </div>
            </div>

            <div className="rec-grid">
                {loading && <div style={{ color: "var(--text-muted)" }}>Loading recommendations...</div>}

                {!loading && recs.length === 0 && (
                    <div style={{ color: "var(--text-muted)" }}>No recommendations yet. Click Generate New to start.</div>
                )}

                {recs.map((rec, i) => (
                    <div key={i} className="rec-card">
                        {/* Format badge */}
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                            <span
                                className="rec-format"
                                style={{ borderColor: `${formatColors[rec.format] || formatColors.Blog}30`, color: formatColors[rec.format] || formatColors.Blog }}
                            >
                                {rec.format}
                            </span>
                            <div style={{ display: "flex", gap: 4 }}>
                                {rec.platforms.map((p: string) => (
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
                            {rec.keywords.slice(0, 3).map((kw: string) => (
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
