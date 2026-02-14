"use client";

import AppShell from "@/components/AppShell";
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer,
} from "recharts";
import { TrendingUp, Filter, ArrowUpRight, Zap, ArrowDownRight } from "lucide-react";
import { useState, useEffect } from "react";
import { fetchTopTrends, fetchTrendTimeline } from "@/lib/api";

export default function TrendsPage() {
    const [trends, setTrends] = useState<any[]>([]);
    const [timeline, setTimeline] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadData() {
            try {
                const [trendsData, timelineData] = await Promise.all([
                    fetchTopTrends(50),
                    fetchTrendTimeline()
                ]);

                // Map trends
                setTrends(trendsData.trends.map(t => ({
                    keyword: t.keyword,
                    direction: t.direction,
                    momentum7d: t.momentum7d,
                    volume: t.volumeCurrent,
                    confidence: t.confidence,
                    platforms: t.platforms || ["twitter"] // fallback
                })));

                // Map timeline
                setTimeline(timelineData.timeline.map(t => ({
                    day: new Date(t.date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
                    volume: t.volume,
                    emerging: t.emerging
                })));

            } catch (err) {
                console.error("Failed to load trends:", err);
            } finally {
                setLoading(false);
            }
        }
        loadData();
    }, []);

    const viral = trends.filter(t => t.direction === "viral").length;
    const emerging = trends.filter(t => t.direction === "emerging").length;

    return (
        <AppShell>
            <div className="page-header">
                <h2 className="page-title">
                    Trend <span className="gradient-text">Explorer</span>
                </h2>
                <p className="page-subtitle">
                    Track keyword momentum across all platforms — {trends.length} signals detected
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
                    <AreaChart data={timeline} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
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

                {loading && <div style={{ padding: 20, textAlign: "center", color: "var(--text-muted)" }}>Loading trends...</div>}

                {!loading && trends.length === 0 && (
                    <div style={{ padding: 30, textAlign: "center", color: "var(--text-muted)" }}>
                        No trends detected yet. Run the pipeline to populate data.
                    </div>
                )}

                {trends.map((t, i) => (
                    <div
                        key={`${t.keyword}-${i}`}
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
                            {t.platforms.map((p: string) => (
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
