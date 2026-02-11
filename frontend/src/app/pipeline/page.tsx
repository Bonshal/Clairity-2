"use client";

import AppShell from "@/components/AppShell";
import { Workflow, CheckCircle2, Clock, AlertCircle, Play, RotateCw } from "lucide-react";

const PIPELINE_RUNS = [
    {
        id: "run_a8f2c3e1",
        startedAt: "2026-02-11T01:45:00Z",
        completedAt: "2026-02-11T01:52:34Z",
        status: "completed",
        platforms: ["reddit", "twitter", "youtube"],
        itemsProcessed: 847,
        evaluationScore: 0.88,
        duration: "7m 34s",
    },
    {
        id: "run_b4d1e7f9",
        startedAt: "2026-02-10T19:30:00Z",
        completedAt: "2026-02-10T19:38:12Z",
        status: "completed",
        platforms: ["twitter", "youtube"],
        itemsProcessed: 523,
        evaluationScore: 0.82,
        duration: "8m 12s",
    },
    {
        id: "run_c9e3a2b5",
        startedAt: "2026-02-10T13:15:00Z",
        completedAt: "2026-02-10T13:19:45Z",
        status: "completed",
        platforms: ["reddit", "twitter", "youtube"],
        itemsProcessed: 1024,
        evaluationScore: 0.91,
        duration: "4m 45s",
    },
    {
        id: "run_d2f8c4a7",
        startedAt: "2026-02-10T07:00:00Z",
        completedAt: null,
        status: "failed",
        platforms: ["reddit"],
        itemsProcessed: 0,
        evaluationScore: null,
        duration: "—",
    },
];

const AGENTS = [
    { name: "Ingestion", status: "completed", time: "1m 12s" },
    { name: "Preprocessing", status: "completed", time: "2m 04s" },
    { name: "Trend Detection", status: "completed", time: "0m 45s" },
    { name: "Sentiment Analysis", status: "completed", time: "1m 22s" },
    { name: "Topic Modeling", status: "completed", time: "0m 58s" },
    { name: "Insight Synthesis", status: "completed", time: "0m 32s" },
    { name: "Recommendation", status: "completed", time: "0m 28s" },
    { name: "Evaluator", status: "completed", time: "0m 13s" },
];

function StatusIcon({ status }: { status: string }) {
    if (status === "completed") return <CheckCircle2 size={16} color="#34d399" />;
    if (status === "running") return <Clock size={16} color="#fbbf24" />;
    if (status === "failed") return <AlertCircle size={16} color="#f87171" />;
    return <Clock size={16} color="#556275" />;
}

export default function PipelinePage() {
    return (
        <AppShell>
            <div className="page-header">
                <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
                    <div>
                        <h2 className="page-title">
                            Pipeline <span className="gradient-text">Monitor</span>
                        </h2>
                        <p className="page-subtitle">
                            Track agent execution, pipeline runs, and system health
                        </p>
                    </div>
                    <button className="btn btn-primary">
                        <Play size={16} /> Trigger Run
                    </button>
                </div>
            </div>

            <div className="chart-grid">
                {/* Agent status */}
                <div className="chart-card">
                    <div className="chart-header">
                        <div>
                            <div className="chart-title" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <Workflow size={16} color="#00e5c8" />
                                Agent Pipeline — Latest Run
                            </div>
                            <div className="chart-subtitle">run_a8f2c3e1 — completed 42 min ago</div>
                        </div>
                    </div>

                    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                        {AGENTS.map((agent, i) => (
                            <div
                                key={agent.name}
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 12,
                                    padding: "10px 14px",
                                    borderRadius: 8,
                                    background: "rgba(255,255,255,0.02)",
                                    border: "1px solid rgba(255,255,255,0.04)",
                                    position: "relative",
                                }}
                            >
                                {/* Step number */}
                                <div
                                    style={{
                                        width: 24,
                                        height: 24,
                                        borderRadius: "50%",
                                        background: agent.status === "completed" ? "rgba(52,211,153,0.12)" : "rgba(255,255,255,0.04)",
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        fontSize: "0.72rem",
                                        fontFamily: "'JetBrains Mono', monospace",
                                        fontWeight: 600,
                                        color: agent.status === "completed" ? "#34d399" : "var(--text-muted)",
                                        flexShrink: 0,
                                    }}
                                >
                                    {i + 1}
                                </div>

                                <span style={{ flex: 1, fontWeight: 500, fontSize: "0.88rem" }}>{agent.name}</span>

                                <StatusIcon status={agent.status} />

                                <span
                                    style={{
                                        fontFamily: "'JetBrains Mono', monospace",
                                        fontSize: "0.78rem",
                                        color: "var(--text-muted)",
                                        width: 60,
                                        textAlign: "right",
                                    }}
                                >
                                    {agent.time}
                                </span>

                                {/* Connector line */}
                                {i < AGENTS.length - 1 && (
                                    <div
                                        style={{
                                            position: "absolute",
                                            left: 25,
                                            bottom: -6,
                                            width: 2,
                                            height: 8,
                                            background: agent.status === "completed" ? "rgba(52,211,153,0.2)" : "rgba(255,255,255,0.04)",
                                            zIndex: 1,
                                        }}
                                    />
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Run history */}
                <div className="chart-card">
                    <div className="chart-header">
                        <div>
                            <div className="chart-title">Run History</div>
                            <div className="chart-subtitle">Last 4 pipeline executions</div>
                        </div>
                        <button className="btn btn-ghost" style={{ fontSize: "0.78rem", padding: "6px 12px" }}>
                            <RotateCw size={12} /> Refresh
                        </button>
                    </div>

                    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                        {PIPELINE_RUNS.map((run) => (
                            <div
                                key={run.id}
                                className="trend-item"
                                style={{
                                    padding: "14px 16px",
                                    borderRadius: 10,
                                    background: "rgba(255,255,255,0.02)",
                                    border: "1px solid rgba(255,255,255,0.04)",
                                    display: "flex",
                                    flexDirection: "column",
                                    gap: 8,
                                }}
                            >
                                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                                    <StatusIcon status={run.status} />
                                    <span
                                        style={{
                                            fontFamily: "'JetBrains Mono', monospace",
                                            fontSize: "0.82rem",
                                            fontWeight: 600,
                                        }}
                                    >
                                        {run.id}
                                    </span>
                                    <span
                                        className={`trend-badge ${run.status === "completed" ? "emerging" : "declining"}`}
                                        style={{ marginLeft: "auto" }}
                                    >
                                        {run.status}
                                    </span>
                                </div>

                                <div style={{ display: "flex", gap: 20, fontSize: "0.78rem", color: "var(--text-muted)" }}>
                                    <span>⏱ {run.duration}</span>
                                    <span>📊 {run.itemsProcessed.toLocaleString()} items</span>
                                    {run.evaluationScore && (
                                        <span>
                                            ✅ Score:{" "}
                                            <span
                                                style={{
                                                    fontFamily: "'JetBrains Mono', monospace",
                                                    color: run.evaluationScore > 0.85 ? "var(--positive)" : "var(--warning)",
                                                    fontWeight: 600,
                                                }}
                                            >
                                                {(run.evaluationScore * 100).toFixed(0)}%
                                            </span>
                                        </span>
                                    )}
                                </div>

                                <div style={{ display: "flex", gap: 4 }}>
                                    {run.platforms.map((p) => (
                                        <span key={p} className={`tag tag-platform ${p}`} style={{ fontSize: "0.65rem", padding: "2px 6px" }}>
                                            {p === "twitter" ? "X" : p}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </AppShell>
    );
}
