"use client";

import { useState, useEffect } from "react";
import { TrendingUp, TrendingDown, Zap, FileText, Eye, BarChart3 } from "lucide-react";
import { fetchDashboardKPIs } from "@/lib/api";

type KPI = {
    label: string;
    value: string;
    change: string;
    changePercent: string;
    direction: "up" | "down";
    icon: any;
    sparkData: number[];
    color: string;
};

const DEFAULT_KPIS: KPI[] = [
    {
        label: "Content Analyzed",
        value: "...",
        change: "--",
        changePercent: "0%",
        direction: "up",
        icon: FileText,
        sparkData: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        color: "#00e5c8",
    },
    {
        label: "Emerging Trends",
        value: "...",
        change: "--",
        changePercent: "0%",
        direction: "up",
        icon: TrendingUp,
        sparkData: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        color: "#0ea5e9",
    },
    {
        label: "Viral Signals",
        value: "...",
        change: "--",
        changePercent: "0%",
        direction: "up",
        icon: Zap,
        sparkData: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        color: "#c084fc",
    },
    {
        label: "Topic Sentiment",
        value: "...",
        change: "Top trend",
        changePercent: "0%",
        direction: "up",
        icon: Eye,
        sparkData: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        color: "#fbbf24",
    },
    {
        label: "Content Gap",
        value: "...",
        change: "--",
        changePercent: "0%",
        direction: "up",
        icon: BarChart3,
        sparkData: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
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
    const [kpis, setKpis] = useState<KPI[]>(DEFAULT_KPIS);

    useEffect(() => {
        async function loadData() {
            try {
                const data = await fetchDashboardKPIs() as any;

                // Topic Sentiment: sentiment of the top trending keyword
                let topicLabel = "No trends";
                let topicValue = "--";
                let topicDir: "up" | "down" = "up";
                let topicColor = "#fbbf24";

                if (data.topTrendSentiment) {
                    const ts = data.topTrendSentiment;
                    const posRatio = ts.totalMentions > 0
                        ? Math.round((ts.positive / ts.totalMentions) * 100)
                        : 0;
                    topicValue = `${posRatio}% pos`;
                    topicLabel = `"${ts.keyword}"`;
                    topicDir = posRatio >= 50 ? "up" : "down";
                    topicColor = posRatio >= 50 ? "#34d399" : "#f87171";
                }

                // Content Gap Score: percentage of trending topics that are underserved
                const gapScore = data.contentGapScore ?? 0;
                const gapLabel = gapScore > 60 ? "High opportunity" : gapScore > 30 ? "Moderate" : "Well covered";

                const newKpis: KPI[] = [
                    {
                        ...DEFAULT_KPIS[0],
                        value: data.totalContent.toLocaleString(),
                        sparkData: [5, 10, 15, 20, 25, 30, 40, 50, 60, data.totalContent > 100 ? 100 : 70],
                    },
                    {
                        ...DEFAULT_KPIS[1],
                        value: data.emergingTrends.toString(),
                        sparkData: [0, 1, 2, 3, 4, 3, 5, 8, 12, 15],
                    },
                    {
                        ...DEFAULT_KPIS[2],
                        value: data.viralSignals.toString(),
                        sparkData: [0, 0, 0, 1, 0, 1, 2, 1, 4, 5],
                    },
                    {
                        label: "Topic Sentiment",
                        value: topicValue,
                        change: topicLabel,
                        changePercent: "",
                        direction: topicDir,
                        icon: Eye,
                        sparkData: [50, 55, 60, 58, 62, 65, 70, 72, 75, 80],
                        color: topicColor,
                    },
                    {
                        label: "Content Gap",
                        value: `${gapScore}%`,
                        change: gapLabel,
                        changePercent: "",
                        direction: gapScore > 40 ? "up" : "down",
                        icon: BarChart3,
                        sparkData: [20, 30, 40, 50, 45, 55, 60, 65, 70, gapScore],
                        color: "#34d399",
                    },
                ];
                setKpis(newKpis);
            } catch (err) {
                console.error("Failed to load KPIs:", err);
            }
        }
        loadData();
    }, []);

    return (
        <div className="kpi-grid">
            {kpis.map((kpi) => (
                <div key={kpi.label} className="glass-card" style={{ padding: "20px 24px" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                        <span className="kpi-label">{kpi.label}</span>
                        <kpi.icon size={16} color={kpi.color} strokeWidth={2} />
                    </div>
                    <div className="kpi-value" style={{ color: kpi.direction === "down" && (kpi.label === "Topic Sentiment") ? "#f87171" : undefined }}>
                        {kpi.value}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: "auto" }}>
                        {kpi.label === "Topic Sentiment" || kpi.label === "Content Gap" ? (
                            <span style={{ fontSize: "0.72rem", color: "var(--text-muted)", maxWidth: 120, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                {kpi.change}
                            </span>
                        ) : (
                            <span className={`kpi-change ${kpi.direction === "up" ? "positive" : "negative"}`}>
                                {kpi.direction === "up" ? (
                                    <TrendingUp size={12} />
                                ) : (
                                    <TrendingDown size={12} />
                                )}
                                {kpi.changePercent}
                            </span>
                        )}
                        <MiniSparkline data={kpi.sparkData} color={kpi.color} />
                    </div>
                </div>
            ))}
        </div>
    );
}
