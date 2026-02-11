"use client";

import AppShell from "@/components/AppShell";
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, BarChart, Bar, Cell,
} from "recharts";
import { TrendingUp, Filter, ArrowUpRight, Zap, ArrowDownRight } from "lucide-react";

const TIMELINE_DATA = Array.from({ length: 30 }, (_, i) => ({
    day: `Jan ${i + 1}`,
    volume: Math.floor(80 + Math.random() * 100 + (i > 20 ? i * 5 : 0)),
    emerging: Math.floor(2 + Math.random() * 5 + (i > 22 ? 3 : 0)),
}));

const ALL_TRENDS = [
    { keyword: "AI code review tools", direction: "viral", momentum7d: 5.2, momentum30d: 3.1, volume: 342, confidence: 0.94, platforms: ["reddit", "twitter", "youtube"] },
    { keyword: "open-source LLM alternatives", direction: "emerging", momentum7d: 1.8, momentum30d: 1.2, volume: 215, confidence: 0.87, platforms: ["reddit", "twitter"] },
    { keyword: "vibe coding workflow", direction: "emerging", momentum7d: 1.45, momentum30d: 0.9, volume: 189, confidence: 0.82, platforms: ["twitter", "youtube"] },
    { keyword: "MCP server integrations", direction: "viral", momentum7d: 3.4, momentum30d: 2.8, volume: 156, confidence: 0.91, platforms: ["reddit", "twitter", "youtube"] },
    { keyword: "AI agent frameworks", direction: "emerging", momentum7d: 0.92, momentum30d: 0.7, volume: 134, confidence: 0.78, platforms: ["reddit", "youtube"] },
    { keyword: "cursor vs windsurf", direction: "stable", momentum7d: 0.12, momentum30d: 0.08, volume: 128, confidence: 0.72, platforms: ["reddit", "twitter"] },
    { keyword: "RAG pipeline optimize", direction: "emerging", momentum7d: 0.78, momentum30d: 0.5, volume: 95, confidence: 0.75, platforms: ["youtube"] },
    { keyword: "browser automation AI", direction: "declining", momentum7d: -0.15, momentum30d: -0.22, volume: 72, confidence: 0.68, platforms: ["twitter"] },
    { keyword: "local model inference", direction: "emerging", momentum7d: 0.65, momentum30d: 0.4, volume: 88, confidence: 0.73, platforms: ["reddit"] },
    { keyword: "prompt engineering dead", direction: "declining", momentum7d: -0.35, momentum30d: -0.18, volume: 64, confidence: 0.66, platforms: ["twitter", "reddit"] },
];

export default function TrendsPage() {
    const viral = ALL_TRENDS.filter(t => t.direction === "viral").length;
    const emerging = ALL_TRENDS.filter(t => t.direction === "emerging").length;

    return (
        <AppShell>
            <div className="page-header">
                <h2 className="page-title">
                    Trend <span className="gradient-text">Explorer</span>
                </h2>
                <p className="page-subtitle">
                    Track keyword momentum across all platforms — {ALL_TRENDS.length} signals detected
                </p>
            </div>

            {/* Summary pills */}
            <div style={{ display: "flex", gap: 12, marginBottom: 24 }}>
                <span className="trend-badge viral" style={{ padding: "8px 16px", fontSize: "0.82rem" }}>
                    <Zap size={14} style={{ marginRight: 4 }} /> {viral} Viral
                </span>
                <span className="trend-badge emerging" style={{ padding: "8px 16px", fontSize: "0.82rem" }}>
                    <TrendingUp size={14} style={{ marginRight: 4 }} /> {emerging} Emerging
                </span>
                <div style={{ marginLeft: "auto" }}>
                    <button className="btn btn-ghost" style={{ fontSize: "0.82rem", padding: "8px 14px" }}>
                        <Filter size={14} /> Filters
                    </button>
                </div>
            </div>

            {/* Timeline chart */}
            <div className="chart-card" style={{ marginBottom: 24 }}>
                <div className="chart-header">
                    <div>
                        <div className="chart-title">Discovery Timeline</div>
                        <div className="chart-subtitle">Content volume and new trend signals over 30 days</div>
                    </div>
                </div>
                <ResponsiveContainer width="100%" height={220}>
                    <AreaChart data={TIMELINE_DATA} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
                        <defs>
                            <linearGradient id="gradVol" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#0ea5e9" stopOpacity={0.2} />
                                <stop offset="100%" stopColor="#0ea5e9" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                        <XAxis dataKey="day" tick={{ fill: "#556275", fontSize: 11 }} axisLine={false} tickLine={false} interval={4} />
                        <YAxis tick={{ fill: "#556275", fontSize: 11, fontFamily: "'JetBrains Mono'" }} axisLine={false} tickLine={false} />
                        <Tooltip
                            contentStyle={{
                                background: "rgba(12,16,23,0.95)", borderRadius: 10,
                                border: "1px solid rgba(255,255,255,0.08)", backdropFilter: "blur(16px)",
                            }}
                        />
                        <Area type="monotone" dataKey="volume" stroke="#0ea5e9" strokeWidth={2} fill="url(#gradVol)" dot={false} />
                        <Area type="monotone" dataKey="emerging" stroke="#00e5c8" strokeWidth={2} fill="transparent" dot={false} strokeDasharray="4 4" />
                    </AreaChart>
                </ResponsiveContainer>
            </div>

            {/* Full trend table */}
            <div className="chart-card">
                <div className="chart-header">
                    <div className="chart-title">All Signals</div>
                </div>

                {/* Table header */}
                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "40px 2fr 100px 100px 100px 80px 150px",
                        padding: "8px 16px",
                        fontSize: "0.72rem",
                        fontWeight: 600,
                        textTransform: "uppercase",
                        letterSpacing: "0.08em",
                        color: "var(--text-muted)",
                        borderBottom: "1px solid var(--glass-border)",
                    }}
                >
                    <span>#</span>
                    <span>Keyword</span>
                    <span>Direction</span>
                    <span style={{ textAlign: "right" }}>7d Mom.</span>
                    <span style={{ textAlign: "right" }}>Volume</span>
                    <span style={{ textAlign: "right" }}>Conf.</span>
                    <span>Platforms</span>
                </div>

                {ALL_TRENDS.map((t, i) => (
                    <div
                        key={t.keyword}
                        className="trend-item"
                        style={{
                            display: "grid",
                            gridTemplateColumns: "40px 2fr 100px 100px 100px 80px 150px",
                            padding: "12px 16px",
                            alignItems: "center",
                        }}
                    >
                        <span className="trend-rank">{i + 1}</span>
                        <span style={{ fontWeight: 500, fontSize: "0.9rem" }}>{t.keyword}</span>
                        <span className={`trend-badge ${t.direction}`}>{t.direction}</span>
                        <span
                            style={{
                                fontFamily: "'JetBrains Mono', monospace",
                                fontSize: "0.82rem",
                                fontWeight: 600,
                                textAlign: "right",
                                color: t.momentum7d > 0 ? "var(--positive)" : "var(--negative)",
                                display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 4,
                            }}
                        >
                            {t.momentum7d > 0 ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                            {t.momentum7d > 0 ? "+" : ""}{(t.momentum7d * 100).toFixed(0)}%
                        </span>
                        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "0.82rem", textAlign: "right" }}>
                            {t.volume}
                        </span>
                        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "0.82rem", textAlign: "right", color: t.confidence > 0.8 ? "var(--positive)" : "var(--text-secondary)" }}>
                            {(t.confidence * 100).toFixed(0)}%
                        </span>
                        <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                            {t.platforms.map((p) => (
                                <span key={p} className={`tag tag-platform ${p}`}>
                                    {p === "twitter" ? "X" : p}
                                </span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </AppShell>
    );
}
