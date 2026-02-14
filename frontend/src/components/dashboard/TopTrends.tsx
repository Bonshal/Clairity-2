"use client";

import { useState, useEffect } from "react";
import { TrendingUp, ArrowUpRight } from "lucide-react";
import { fetchTopTrends } from "@/lib/api";

type Trend = {
    rank: number;
    keyword: string;
    direction: string;
    momentum: string;
    volume: number;
};

export default function TopTrends() {
    const [trends, setTrends] = useState<Trend[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadData() {
            try {
                const data = await fetchTopTrends(8);
                const mapped = data.trends.map((t, i) => ({
                    rank: i + 1,
                    keyword: t.keyword,
                    direction: t.direction,
                    momentum: `+${t.momentum7d.toFixed(0)}%`, // simplified formatting
                    volume: t.volumeCurrent,
                }));
                setTrends(mapped);
            } catch (err) {
                console.error("Failed to fetch top trends:", err);
            } finally {
                setLoading(false);
            }
        }
        loadData();
    }, []);

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
                {trends.length === 0 && !loading && (
                    <div style={{ padding: 20, textAlign: "center", color: "var(--text-secondary)" }}>
                        No trends detected yet. Run the pipeline to populate data.
                    </div>
                )}
                {trends.map((t) => (
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
