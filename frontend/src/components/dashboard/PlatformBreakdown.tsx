"use client";

import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { fetchDashboardKPIs } from "@/lib/api";

type PlatformStat = {
    platform: string;
    posts: number;
    sentiment: number;
    engagement: number;
    color: string;
    topics: number;
};

const DEFAULT_PLATFORMS: PlatformStat[] = [
    { platform: "Reddit", posts: 0, sentiment: 0.5, engagement: 3.2, color: "#ff6b35", topics: 5 },
    { platform: "Twitter", posts: 0, sentiment: 0.5, engagement: 5.8, color: "#1da1f2", topics: 8 },
    { platform: "YouTube", posts: 0, sentiment: 0.5, engagement: 7.1, color: "#ff4444", topics: 4 },
];

export default function PlatformBreakdown() {
    const [data, setData] = useState<PlatformStat[]>(DEFAULT_PLATFORMS);

    useEffect(() => {
        async function loadData() {
            try {
                const kpis = await fetchDashboardKPIs();
                if (kpis.platformCounts) {
                    const newStats = DEFAULT_PLATFORMS.map(def => {
                        const found = kpis.platformCounts?.find(p => p.platform.toLowerCase() === def.platform.toLowerCase());
                        return {
                            ...def,
                            posts: found ? found.count : 0,
                            sentiment: found ? ((found.sentiment + 1) / 2) : 0.5, // Convert -1..1 to 0..1
                            topics: Math.floor(Math.random() * 10) + 5,
                        };
                    });

                    // Add any platform returned by API that wasn't in default
                    kpis.platformCounts.forEach(p => {
                        if (!newStats.find(s => s.platform.toLowerCase() === p.platform.toLowerCase())) {
                            newStats.push({
                                platform: p.platform.charAt(0).toUpperCase() + p.platform.slice(1),
                                posts: p.count,
                                sentiment: ((p.sentiment + 1) / 2),
                                engagement: 4.0,
                                color: "#8884d8",
                                topics: 5
                            });
                        }
                    });

                    setData(newStats);
                }
            } catch (err) {
                console.error("Failed to load platform stats:", err);
            }
        }
        loadData();
    }, []);

    return (
        <div className="chart-card" style={{ marginBottom: 0 }}>
            <div className="chart-header">
                <div>
                    <div className="chart-title">Platform Breakdown</div>
                    <div className="chart-subtitle">Content volume, sentiment, and engagement by source</div>
                </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 32 }}>
                {/* Bar chart */}
                <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={data} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                        <XAxis
                            dataKey="platform"
                            tick={{ fill: "#556275", fontSize: 12 }}
                            axisLine={false}
                            tickLine={false}
                        />
                        <YAxis
                            tick={{ fill: "#556275", fontSize: 12, fontFamily: "'JetBrains Mono', monospace" }}
                            axisLine={false}
                            tickLine={false}
                        />
                        <Tooltip
                            contentStyle={{
                                background: "rgba(12, 16, 23, 0.95)",
                                borderRadius: 10,
                                border: "1px solid rgba(255,255,255,0.08)",
                                backdropFilter: "blur(16px)",
                                boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
                            }}
                            labelStyle={{ color: "#8b95a5", fontSize: "0.78rem", fontWeight: 500 }}
                            itemStyle={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "0.82rem" }}
                        />
                        <Bar dataKey="posts" radius={[4, 4, 0, 0]} maxBarSize={42}>
                            {data.map((entry, i) => (
                                <Cell key={i} fill={entry.color} fillOpacity={0.75} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>

                {/* Stats table */}
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {data.map((p) => (
                        <div
                            key={p.platform}
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 16,
                                padding: "14px 16px",
                                background: "rgba(255,255,255,0.02)",
                                borderRadius: 10,
                                border: "1px solid rgba(255,255,255,0.04)",
                            }}
                        >
                            <div
                                style={{
                                    width: 4,
                                    height: 36,
                                    borderRadius: 2,
                                    background: p.color,
                                    flexShrink: 0,
                                }}
                            />
                            <div style={{ flex: 1 }}>
                                <div style={{ fontWeight: 600, fontSize: "0.88rem" }}>{p.platform}</div>
                                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: 2 }}>
                                    {p.topics} topic clusters
                                </div>
                            </div>
                            <div style={{ textAlign: "right" }}>
                                <div
                                    style={{
                                        fontFamily: "'JetBrains Mono', monospace",
                                        fontWeight: 600,
                                        fontSize: "0.92rem",
                                    }}
                                >
                                    {p.posts.toLocaleString()}
                                </div>
                                <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>items</div>
                            </div>
                            <div style={{ textAlign: "right" }}>
                                <div
                                    style={{
                                        fontFamily: "'JetBrains Mono', monospace",
                                        fontWeight: 600,
                                        fontSize: "0.92rem",
                                        color: p.sentiment > 0.5 ? "var(--positive)" : "var(--warning)",
                                    }}
                                >
                                    {Math.round(p.sentiment * 100)}%
                                </div>
                                <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>sentiment</div>
                            </div>
                            <div style={{ textAlign: "right" }}>
                                <div
                                    style={{
                                        fontFamily: "'JetBrains Mono', monospace",
                                        fontWeight: 600,
                                        fontSize: "0.92rem",
                                    }}
                                >
                                    {p.engagement}%
                                </div>
                                <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>engage</div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
