"use client";

import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

const DATA = [
    { name: "Positive", value: 42, color: "#34d399" },
    { name: "Neutral", value: 38, color: "#556275" },
    { name: "Negative", value: 20, color: "#f87171" },
];

const EMOTIONS = [
    { label: "Curiosity", value: 0.34, color: "#0ea5e9" },
    { label: "Excitement", value: 0.28, color: "#c084fc" },
    { label: "Approval", value: 0.19, color: "#34d399" },
    { label: "Surprise", value: 0.11, color: "#fbbf24" },
    { label: "Annoyance", value: 0.08, color: "#f87171" },
];

export default function SentimentDonut() {
    return (
        <div className="chart-card">
            <div className="chart-header">
                <div>
                    <div className="chart-title">Sentiment & Emotions</div>
                    <div className="chart-subtitle">Across all platforms this week</div>
                </div>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                {/* Donut */}
                <div style={{ width: 130, height: 130, position: "relative" }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={DATA}
                                cx="50%"
                                cy="50%"
                                innerRadius={38}
                                outerRadius={58}
                                paddingAngle={3}
                                dataKey="value"
                                startAngle={90}
                                endAngle={-270}
                                strokeWidth={0}
                            >
                                {DATA.map((entry, i) => (
                                    <Cell key={i} fill={entry.color} />
                                ))}
                            </Pie>
                        </PieChart>
                    </ResponsiveContainer>
                    <div
                        style={{
                            position: "absolute",
                            top: "50%",
                            left: "50%",
                            transform: "translate(-50%, -50%)",
                            textAlign: "center",
                        }}
                    >
                        <div
                            style={{
                                fontFamily: "'JetBrains Mono', monospace",
                                fontSize: "1.3rem",
                                fontWeight: 700,
                                color: "#34d399",
                            }}
                        >
                            42%
                        </div>
                        <div style={{ fontSize: "0.6rem", color: "#8b95a5", fontWeight: 500 }}>Positive</div>
                    </div>
                </div>

                {/* Legend + Emotions */}
                <div style={{ flex: 1 }}>
                    {/* Sentiment legend */}
                    <div style={{ display: "flex", gap: 14, marginBottom: 16 }}>
                        {DATA.map((d) => (
                            <div key={d.name} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                                <span
                                    style={{
                                        width: 8,
                                        height: 8,
                                        borderRadius: "50%",
                                        background: d.color,
                                        display: "inline-block",
                                    }}
                                />
                                <span style={{ fontSize: "0.75rem", color: "#8b95a5" }}>
                                    {d.name}
                                </span>
                                <span
                                    style={{
                                        fontFamily: "'JetBrains Mono', monospace",
                                        fontSize: "0.75rem",
                                        fontWeight: 600,
                                        color: "#f0f4f8",
                                    }}
                                >
                                    {d.value}%
                                </span>
                            </div>
                        ))}
                    </div>

                    {/* Top emotions bar */}
                    <div style={{ fontSize: "0.7rem", color: "#556275", marginBottom: 8, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                        Dominant Emotions
                    </div>
                    {EMOTIONS.map((e) => (
                        <div
                            key={e.label}
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 8,
                                marginBottom: 5,
                            }}
                        >
                            <span style={{ fontSize: "0.78rem", color: "#8b95a5", width: 70 }}>
                                {e.label}
                            </span>
                            <div
                                style={{
                                    flex: 1,
                                    height: 4,
                                    background: "rgba(255,255,255,0.04)",
                                    borderRadius: 2,
                                    overflow: "hidden",
                                }}
                            >
                                <div
                                    style={{
                                        width: `${e.value * 100}%`,
                                        height: "100%",
                                        background: e.color,
                                        borderRadius: 2,
                                        transition: "width 0.6s cubic-bezier(0.16, 1, 0.3, 1)",
                                    }}
                                />
                            </div>
                            <span
                                style={{
                                    fontFamily: "'JetBrains Mono', monospace",
                                    fontSize: "0.72rem",
                                    color: "#8b95a5",
                                    width: 32,
                                    textAlign: "right",
                                }}
                            >
                                {Math.round(e.value * 100)}%
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
