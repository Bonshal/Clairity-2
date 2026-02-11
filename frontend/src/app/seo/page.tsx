"use client";

import AppShell from "@/components/AppShell";
import { Target, ArrowUpRight, BarChart3, TrendingUp, Search as SearchIcon } from "lucide-react";

const SEO_KEYWORDS = [
    { keyword: "AI code review tools", volume: 8100, difficulty: 34, opportunity: 0.92, intent: "commercial", trend: "up" },
    { keyword: "best open source LLM", volume: 14500, difficulty: 52, opportunity: 0.78, intent: "informational", trend: "up" },
    { keyword: "MCP server tutorial", volume: 2400, difficulty: 18, opportunity: 0.95, intent: "informational", trend: "up" },
    { keyword: "vibe coding explained", volume: 5600, difficulty: 22, opportunity: 0.88, intent: "informational", trend: "up" },
    { keyword: "RAG pipeline optimization", volume: 3200, difficulty: 41, opportunity: 0.81, intent: "commercial", trend: "stable" },
    { keyword: "AI agent framework comparison", volume: 4800, difficulty: 38, opportunity: 0.84, intent: "commercial", trend: "up" },
    { keyword: "local LLM inference setup", volume: 1900, difficulty: 25, opportunity: 0.87, intent: "navigational", trend: "stable" },
    { keyword: "automated code review benefits", volume: 6700, difficulty: 45, opportunity: 0.72, intent: "informational", trend: "down" },
];

const intentColors: Record<string, string> = {
    informational: "#0ea5e9",
    commercial: "#c084fc",
    transactional: "#34d399",
    navigational: "#fbbf24",
};

export default function SEOPage() {
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
                    <div className="kpi-value" style={{ fontSize: "1.6rem" }}>{SEO_KEYWORDS.length}</div>
                </div>
                <div className="glass-card" style={{ padding: "16px 20px" }}>
                    <div className="kpi-label">Avg. Difficulty</div>
                    <div className="kpi-value" style={{ fontSize: "1.6rem", color: "var(--positive)" }}>
                        {Math.round(SEO_KEYWORDS.reduce((a, k) => a + k.difficulty, 0) / SEO_KEYWORDS.length)}
                    </div>
                </div>
                <div className="glass-card" style={{ padding: "16px 20px" }}>
                    <div className="kpi-label">High Opportunity</div>
                    <div className="kpi-value" style={{ fontSize: "1.6rem", color: "var(--accent-1)" }}>
                        {SEO_KEYWORDS.filter(k => k.opportunity > 0.85).length}
                    </div>
                </div>
                <div className="glass-card" style={{ padding: "16px 20px" }}>
                    <div className="kpi-label">Total Monthly Volume</div>
                    <div className="kpi-value" style={{ fontSize: "1.6rem" }}>
                        {(SEO_KEYWORDS.reduce((a, k) => a + k.volume, 0) / 1000).toFixed(1)}K
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

                {SEO_KEYWORDS.map((kw) => (
                    <div
                        key={kw.keyword}
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
