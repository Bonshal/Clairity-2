"use client";

import { useState, useEffect } from "react";
import { AlertTriangle, TrendingUp, Zap, MessageCircle } from "lucide-react";
import { fetchDashboardAlerts } from "@/lib/api";

type Alert = {
    type: string;
    icon: any;
    title: string;
    desc: string;
    time: string;
    color: string;
};

const DEFAULT_ALERTS: Alert[] = [];

function timeAgo(dateString: string) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return `${diffInSeconds}s ago`;
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${Math.floor(diffInHours / 24)}d ago`;
}

export default function RecentAlerts() {
    const [alerts, setAlerts] = useState<Alert[]>(DEFAULT_ALERTS);

    useEffect(() => {
        async function loadData() {
            try {
                const data = await fetchDashboardAlerts();

                const mapped: Alert[] = (data.alerts || []).map((a) => {
                    let icon = TrendingUp;
                    let color = "#0ea5e9";
                    if (a.direction === "viral") { icon = Zap; color = "#c084fc"; }
                    else if (a.direction === "declining") { icon = AlertTriangle; color = "#f87171"; }
                    else if (a.direction === "stable") { icon = MessageCircle; color = "#fbbf24"; }

                    return {
                        type: a.direction,
                        icon,
                        title: `Trend: "${a.keyword}"`,
                        desc: `${a.direction} on ${a.platform}`,
                        time: timeAgo(a.detectedAt),
                        color
                    };
                });
                setAlerts(mapped);
            } catch (err) {
                console.error("Failed to load alerts:", err);
            }
        }
        loadData();
    }, []);

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
                    {alerts.length} new
                </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                {alerts.length === 0 && (
                    <div style={{ padding: 20, textAlign: "center", color: "var(--text-secondary)" }}>
                        No recent alerts.
                    </div>
                )}
                {alerts.map((alert, i) => (
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
