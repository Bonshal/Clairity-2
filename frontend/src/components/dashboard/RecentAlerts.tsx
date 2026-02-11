"use client";

import { AlertTriangle, TrendingUp, Zap, MessageCircle } from "lucide-react";

const ALERTS = [
    {
        type: "viral",
        icon: Zap,
        title: '"AI code review tools" hit viral threshold',
        desc: "+520% momentum, Z-score 4.2",
        time: "12 min ago",
        color: "#c084fc",
    },
    {
        type: "emerging",
        icon: TrendingUp,
        title: 'New cluster: "MCP server integrations"',
        desc: "Detected across Reddit + Twitter, 156 mentions",
        time: "38 min ago",
        color: "#00e5c8",
    },
    {
        type: "sentiment",
        icon: MessageCircle,
        title: "Sentiment shift on AI agents topic",
        desc: "Positive sentiment dropped 12% in 24h",
        time: "1h ago",
        color: "#fbbf24",
    },
    {
        type: "anomaly",
        icon: AlertTriangle,
        title: "Engagement outlier detected",
        desc: 'YouTube video "Build MCP from scratch" — 12x avg views',
        time: "2h ago",
        color: "#f87171",
    },
];

export default function RecentAlerts() {
    return (
        <div className="chart-card">
            <div className="chart-header">
                <div>
                    <div className="chart-title">Recent Alerts</div>
                    <div className="chart-subtitle">Pipeline notifications and anomalies</div>
                </div>
                <span
                    style={{
                        background: "rgba(192, 132, 252, 0.12)",
                        color: "#c084fc",
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: "0.72rem",
                        fontWeight: 600,
                        padding: "3px 10px",
                        borderRadius: 8,
                    }}
                >
                    4 new
                </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                {ALERTS.map((alert, i) => (
                    <div
                        key={i}
                        style={{
                            display: "flex",
                            alignItems: "flex-start",
                            gap: 12,
                            padding: "12px 14px",
                            borderRadius: 8,
                            cursor: "pointer",
                            transition: "background 150ms",
                        }}
                        className="trend-item"
                    >
                        <div
                            style={{
                                width: 32,
                                height: 32,
                                borderRadius: 8,
                                background: `${alert.color}15`,
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                flexShrink: 0,
                            }}
                        >
                            <alert.icon size={15} color={alert.color} />
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                            <div
                                style={{
                                    fontSize: "0.88rem",
                                    fontWeight: 500,
                                    marginBottom: 2,
                                    overflow: "hidden",
                                    textOverflow: "ellipsis",
                                    whiteSpace: "nowrap",
                                }}
                            >
                                {alert.title}
                            </div>
                            <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                                {alert.desc}
                            </div>
                        </div>
                        <span
                            style={{
                                fontSize: "0.72rem",
                                color: "var(--text-muted)",
                                whiteSpace: "nowrap",
                                flexShrink: 0,
                            }}
                        >
                            {alert.time}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
