"use client";

import { TrendingUp, ArrowUpRight } from "lucide-react";

const TRENDS = [
    { rank: 1, keyword: "AI code review tools", direction: "viral", momentum: "+520%", volume: 342 },
    { rank: 2, keyword: "open-source LLM alternatives", direction: "emerging", momentum: "+180%", volume: 215 },
    { rank: 3, keyword: "vibe coding workflow", direction: "emerging", momentum: "+145%", volume: 189 },
    { rank: 4, keyword: "MCP server integrations", direction: "viral", momentum: "+340%", volume: 156 },
    { rank: 5, keyword: "AI agent frameworks", direction: "emerging", momentum: "+92%", volume: 134 },
    { rank: 6, keyword: "cursor vs windsurf", direction: "stable", momentum: "+12%", volume: 128 },
    { rank: 7, keyword: "RAG pipeline optimize", direction: "emerging", momentum: "+78%", volume: 95 },
    { rank: 8, keyword: "browser automation AI", direction: "declining", momentum: "-15%", volume: 72 },
];

export default function TopTrends() {
    return (
        <div className="chart-card">
            <div className="chart-header">
                <div>
                    <div className="chart-title" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <TrendingUp size={16} color="#00e5c8" />
                        Top Trending Keywords
                    </div>
                    <div className="chart-subtitle">Ranked by 7-day momentum score</div>
                </div>
                <button className="btn btn-ghost" style={{ fontSize: "0.78rem", padding: "6px 12px" }}>
                    View All <ArrowUpRight size={12} />
                </button>
            </div>

            <div className="trend-list">
                {TRENDS.map((t) => (
                    <div key={t.rank} className="trend-item">
                        <span className="trend-rank">{t.rank}</span>
                        <span className="trend-keyword">{t.keyword}</span>
                        <span className={`trend-badge ${t.direction}`}>{t.direction}</span>
                        <span
                            className="trend-momentum"
                            style={{
                                color:
                                    t.direction === "declining"
                                        ? "var(--negative)"
                                        : t.direction === "viral"
                                            ? "var(--viral)"
                                            : "var(--positive)",
                            }}
                        >
                            {t.momentum}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
