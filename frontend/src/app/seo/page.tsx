"use client";

import AppShell from "@/components/AppShell";
import { Target, ArrowUpRight, BarChart3, TrendingUp, Search as SearchIcon } from "lucide-react";
import { useState, useEffect } from "react";
import { fetchTopTrends } from "@/lib/api";

const intentColors: Record<string, string> = {
    informational: "#0ea5e9",
    commercial: "#c084fc",
    transactional: "#34d399",
    navigational: "#fbbf24",
};

export default function SEOPage() {
    const [keywords, setKeywords] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadData() {
            setLoading(true);
            try {
                const data = await fetchTopTrends(100);
                // Filter for high volume/high momentum trends suitable for SEO
                const mapped = data.trends
                    .filter(t => t.volumeCurrent > 50)
                    .map(t => ({
                        keyword: t.keyword,
                        volume: t.volumeCurrent * 50, // rough estimate multiplier for total search vol
                        difficulty: Math.round(Math.random() * 60 + 20), // Mock difficulty for now
                        opportunity: t.confidence,
                        intent: t.keyword.includes("how") || t.keyword.includes("guide") ? "informational" : "commercial",
                        trend: t.momentum7d > 0.1 ? "up" : t.momentum7d < -0.1 ? "down" : "stable",
                    }));
                setKeywords(mapped);
            } catch (err) {
                console.error("Failed to load SEO keywords:", err);
            } finally {
                setLoading(false);
            }
        }
        loadData();
    }, []);

    return (
        <AppShell>
            <div className="page-header">
                <h2 className="page-title">
                    SEO <span className="gradient-text">Analysis</span>
                </h2>
                <p className="page-subtitle">
                    Keyword opportunities discovered from trend signals — optimized for search engines
                </p>
            </div>

            {/* Summary stats */}
            <div className="kpi-grid" style={{ marginBottom: 24 }}>
                <div className="glass-card" style={{ padding: "16px 20px" }}>
                    <div className="kpi-label">Keywords Found</div>
                    <div className="kpi-value" style={{ fontSize: "1.6rem" }}>{keywords.length}</div>
                </div>
                <div className="glass-card" style={{ padding: "16px 20px" }}>
                    <div className="kpi-label">Avg. Difficulty</div>
                    <div className="kpi-value" style={{ fontSize: "1.6rem", color: "var(--positive)" }}>
                        {keywords.length > 0 ? Math.round(keywords.reduce((a, k) => a + k.difficulty, 0) / keywords.length) : 0}
                    </div>
                </div>
                <div className="glass-card" style={{ padding: "16px 20px" }}>
                    <div className="kpi-label">High Opportunity</div>
                    <div className="kpi-value" style={{ fontSize: "1.6rem", color: "var(--accent-1)" }}>
                        {keywords.filter(k => k.opportunity > 0.85).length}
                    </div>
                </div>
                <div className="glass-card" style={{ padding: "16px 20px" }}>
                    <div className="kpi-label">Total Monthly Volume</div>
                    <div className="kpi-value" style={{ fontSize: "1.6rem" }}>
                        {(keywords.reduce((a, k) => a + k.volume, 0) / 1000).toFixed(1)}K
                    </div>
                </div>
            </div>

            {/* Keyword table */}
            <div className="chart-card">
                <div className="chart-header">
                    <div className="chart-title" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <Target size={16} color="#00e5c8" />
                        Keyword Opportunities
                    </div>
                </div>

                {/* Table header */}
                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "2.5fr 100px 100px 120px 120px 80px",
                        padding: "10px 16px",
                        fontSize: "0.72rem",
                        fontWeight: 600,
                        textTransform: "uppercase",
                        letterSpacing: "0.08em",
                        color: "var(--text-muted)",
                        borderBottom: "1px solid var(--glass-border)",
                    }}
                >
                    <span>Keyword</span>
                    <span style={{ textAlign: "right" }}>Volume</span>
                    <span style={{ textAlign: "right" }}>Difficulty</span>
                    <span style={{ textAlign: "center" }}>Intent</span>
                    <span style={{ textAlign: "right" }}>Opportunity</span>
                    <span style={{ textAlign: "center" }}>Trend</span>
                </div>

                {loading && <div style={{ padding: 20, textAlign: "center", color: "var(--text-muted)" }}>Loading content...</div>}

                {!loading && keywords.length === 0 && (
                    <div style={{ padding: 30, textAlign: "center", color: "var(--text-muted)" }}>No high-opportunity keywords found yet.</div>
                )}

                {keywords.map((kw, i) => (
                    <div
                        key={`${kw.keyword}-${i}`}
                        className="trend-item"
                        style={{
                            display: "grid",
                            gridTemplateColumns: "2.5fr 100px 100px 120px 120px 80px",
                            padding: "14px 16px",
                            alignItems: "center",
                        }}
                    >
                        <span style={{ fontWeight: 500, fontSize: "0.9rem" }}>{kw.keyword}</span>
                        <span style={{ fontFamily: "'JetBrains Mono'", fontSize: "0.82rem", textAlign: "right" }}>
                            {kw.volume.toLocaleString()}
                        </span>
                        <div style={{ textAlign: "right", display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 8 }}>
                            <div style={{ width: 40, height: 4, background: "rgba(255,255,255,0.04)", borderRadius: 2, overflow: "hidden" }}>
                                <div style={{ width: `${kw.difficulty}%`, height: "100%", background: kw.difficulty < 30 ? "var(--positive)" : kw.difficulty < 50 ? "var(--warning)" : "var(--negative)", borderRadius: 2 }} />
                            </div>
                            <span style={{ fontFamily: "'JetBrains Mono'", fontSize: "0.82rem", color: kw.difficulty < 30 ? "var(--positive)" : kw.difficulty < 50 ? "var(--warning)" : "var(--negative)" }}>
                                {kw.difficulty}
                            </span>
                        </div>
                        <div style={{ textAlign: "center" }}>
                            <span style={{ padding: "3px 10px", borderRadius: 6, fontSize: "0.72rem", fontWeight: 600, background: `${intentColors[kw.intent]}15`, color: intentColors[kw.intent], textTransform: "capitalize" }}>
                                {kw.intent}
                            </span>
                        </div>
                        <div style={{ textAlign: "right" }}>
                            <span style={{ fontFamily: "'JetBrains Mono'", fontSize: "0.85rem", fontWeight: 700, color: kw.opportunity > 0.85 ? "var(--accent-1)" : "var(--text-secondary)" }}>
                                {Math.round(kw.opportunity * 100)}
                            </span>
                            <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}> / 100</span>
                        </div>
                        <div style={{ textAlign: "center" }}>
                            {kw.trend === "up" && <TrendingUp size={14} color="var(--positive)" />}
                            {kw.trend === "stable" && <span style={{ color: "var(--text-muted)", fontSize: "0.82rem" }}>—</span>}
                            {kw.trend === "down" && <TrendingUp size={14} color="var(--negative)" style={{ transform: "rotate(180deg)" }} />}
                        </div>
                    </div>
                ))}
            </div>
        </AppShell>
    );
}
