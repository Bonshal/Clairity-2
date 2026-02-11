"use client";

import { TrendingUp, TrendingDown, Zap, FileText, Eye, BarChart3 } from "lucide-react";

const KPIS = [
    {
        label: "Content Analyzed",
        value: "2,847",
        change: "+312",
        changePercent: "+12.3%",
        direction: "up" as const,
        icon: FileText,
        sparkData: [20, 25, 22, 35, 28, 42, 38, 55, 48, 62],
        color: "#00e5c8",
    },
    {
        label: "Emerging Trends",
        value: "24",
        change: "+7",
        changePercent: "+41.2%",
        direction: "up" as const,
        icon: TrendingUp,
        sparkData: [5, 8, 12, 10, 15, 14, 18, 20, 17, 24],
        color: "#0ea5e9",
    },
    {
        label: "Viral Signals",
        value: "3",
        change: "+2",
        changePercent: "+200%",
        direction: "up" as const,
        icon: Zap,
        sparkData: [0, 0, 1, 0, 1, 0, 2, 1, 1, 3],
        color: "#c084fc",
    },
    {
        label: "Avg Engagement",
        value: "4.7%",
        change: "-0.3%",
        changePercent: "-6.0%",
        direction: "down" as const,
        icon: Eye,
        sparkData: [5.2, 5.0, 4.8, 5.1, 4.9, 5.3, 4.6, 4.8, 5.0, 4.7],
        color: "#fbbf24",
    },
    {
        label: "Opportunity Score",
        value: "8.4",
        change: "+0.6",
        changePercent: "+7.7%",
        direction: "up" as const,
        icon: BarChart3,
        sparkData: [6.5, 7.0, 7.2, 7.8, 7.5, 8.0, 7.8, 8.1, 8.2, 8.4],
        color: "#34d399",
    },
];

function MiniSparkline({ data, color }: { data: number[]; color: string }) {
    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;
    const h = 36;
    const w = 120;
    const step = w / (data.length - 1);

    const points = data
        .map((v, i) => `${i * step},${h - ((v - min) / range) * h}`)
        .join(" ");

    const areaPoints = `0,${h} ${points} ${w},${h}`;

    return (
        <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} className="kpi-sparkline">
            <defs>
                <linearGradient id={`spark-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={color} stopOpacity="0.3" />
                    <stop offset="100%" stopColor={color} stopOpacity="0" />
                </linearGradient>
            </defs>
            <polygon
                points={areaPoints}
                fill={`url(#spark-${color.replace('#', '')})`}
            />
            <polyline
                points={points}
                fill="none"
                stroke={color}
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
            {/* Glow dot on last point */}
            <circle
                cx={w}
                cy={h - ((data[data.length - 1] - min) / range) * h}
                r="3"
                fill={color}
            >
                <animate
                    attributeName="opacity"
                    values="1;0.4;1"
                    dur="2s"
                    repeatCount="indefinite"
                />
            </circle>
        </svg>
    );
}

export default function KPICards() {
    return (
        <div className="kpi-grid">
            {KPIS.map((kpi) => (
                <div key={kpi.label} className="glass-card" style={{ padding: "20px 24px" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                        <span className="kpi-label">{kpi.label}</span>
                        <kpi.icon size={16} color={kpi.color} strokeWidth={2} />
                    </div>
                    <div className="kpi-value" style={{ color: kpi.color === "#fbbf24" && kpi.direction === "down" ? "var(--text-primary)" : undefined }}>
                        {kpi.value}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: "auto" }}>
                        <span className={`kpi-change ${kpi.direction === "up" ? "positive" : "negative"}`}>
                            {kpi.direction === "up" ? (
                                <TrendingUp size={12} />
                            ) : (
                                <TrendingDown size={12} />
                            )}
                            {kpi.changePercent}
                        </span>
                        <MiniSparkline data={kpi.sparkData} color={kpi.color} />
                    </div>
                </div>
            ))}
        </div>
    );
}
