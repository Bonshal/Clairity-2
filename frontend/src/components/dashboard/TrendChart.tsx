"use client";

import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend,
} from "recharts";

const DATA = [
    { day: "Mon", reddit: 120, twitter: 85, youtube: 45 },
    { day: "Tue", reddit: 145, twitter: 110, youtube: 52 },
    { day: "Wed", reddit: 138, twitter: 95, youtube: 68 },
    { day: "Thu", reddit: 180, twitter: 140, youtube: 55 },
    { day: "Fri", reddit: 165, twitter: 125, youtube: 72 },
    { day: "Sat", reddit: 210, twitter: 155, youtube: 85 },
    { day: "Sun", reddit: 195, twitter: 168, youtube: 90 },
];

const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload) return null;
    return (
        <div
            style={{
                background: "rgba(12, 16, 23, 0.95)",
                borderRadius: "10px",
                border: "1px solid rgba(255,255,255,0.08)",
                padding: "12px 16px",
                backdropFilter: "blur(16px)",
                boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
            }}
        >
            <div style={{ color: "#8b95a5", fontSize: "0.78rem", marginBottom: 8, fontWeight: 500 }}>
                {label}
            </div>
            {payload.map((p: any) => (
                <div
                    key={p.name}
                    style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        fontSize: "0.85rem",
                        marginBottom: 4,
                    }}
                >
                    <span
                        style={{
                            width: 8,
                            height: 8,
                            borderRadius: "50%",
                            background: p.color,
                            display: "inline-block",
                        }}
                    />
                    <span style={{ color: "#8b95a5", textTransform: "capitalize" }}>
                        {p.name}
                    </span>
                    <span
                        style={{
                            fontFamily: "'JetBrains Mono', monospace",
                            fontWeight: 600,
                            marginLeft: "auto",
                            color: "#f0f4f8",
                        }}
                    >
                        {p.value}
                    </span>
                </div>
            ))}
        </div>
    );
};

export default function TrendChart() {
    return (
        <div className="chart-card">
            <div className="chart-header">
                <div>
                    <div className="chart-title">Content Volume by Platform</div>
                    <div className="chart-subtitle">Last 7 days — items discovered per day</div>
                </div>
            </div>
            <ResponsiveContainer width="100%" height={260}>
                <AreaChart data={DATA} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
                    <defs>
                        <linearGradient id="gradReddit" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#ff6b35" stopOpacity={0.25} />
                            <stop offset="100%" stopColor="#ff6b35" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="gradTwitter" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#1da1f2" stopOpacity={0.25} />
                            <stop offset="100%" stopColor="#1da1f2" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="gradYoutube" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#ff4444" stopOpacity={0.25} />
                            <stop offset="100%" stopColor="#ff4444" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="rgba(255,255,255,0.04)"
                        vertical={false}
                    />
                    <XAxis
                        dataKey="day"
                        tick={{ fill: "#556275", fontSize: 12 }}
                        axisLine={false}
                        tickLine={false}
                    />
                    <YAxis
                        tick={{ fill: "#556275", fontSize: 12, fontFamily: "'JetBrains Mono', monospace" }}
                        axisLine={false}
                        tickLine={false}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Area
                        type="monotone"
                        dataKey="reddit"
                        stroke="#ff6b35"
                        strokeWidth={2}
                        fill="url(#gradReddit)"
                        dot={false}
                        activeDot={{ r: 4, strokeWidth: 2 }}
                    />
                    <Area
                        type="monotone"
                        dataKey="twitter"
                        stroke="#1da1f2"
                        strokeWidth={2}
                        fill="url(#gradTwitter)"
                        dot={false}
                        activeDot={{ r: 4, strokeWidth: 2 }}
                    />
                    <Area
                        type="monotone"
                        dataKey="youtube"
                        stroke="#ff4444"
                        strokeWidth={2}
                        fill="url(#gradYoutube)"
                        dot={false}
                        activeDot={{ r: 4, strokeWidth: 2 }}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
