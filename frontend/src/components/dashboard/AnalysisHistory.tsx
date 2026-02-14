import { useState, useEffect, useRef } from "react";
import { fetchPipelineHistory, fetchPipelineStatus } from "@/lib/api";
import { Terminal, Loader2, ArrowRight, X, Clock, CheckCircle, AlertCircle, PlayCircle } from "lucide-react";

type LogEntry = {
    timestamp: string;
    step: string;
    status: string;
    message: string;
    duration?: number;
};

type Run = {
    runId: string;
    status: string;
    startedAt: string;
    completedAt?: string;
    duration: string;
    itemsProcessed: number;
    evaluationScore?: number;
    platforms: string[];
};

export default function AnalysisHistory() {
    const [runs, setRuns] = useState<Run[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [loadingLogs, setLoadingLogs] = useState(false);
    const logsEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        loadHistory();
        const interval = setInterval(loadHistory, 10000); // Poll every 10s
        return () => clearInterval(interval);
    }, []);

    // Auto-scroll logs
    useEffect(() => {
        if (selectedRunId && logsEndRef.current) {
            logsEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [logs, selectedRunId]);

    async function loadHistory() {
        try {
            const data = await fetchPipelineHistory(10);
            setRuns(data.runs);
        } catch (error) {
            console.error("Failed to load history:", error);
        } finally {
            setLoading(false);
        }
    }

    async function handleViewLogs(runId: string) {
        setSelectedRunId(runId);
        setLoadingLogs(true);
        setLogs([]);
        try {
            const status = await fetchPipelineStatus(runId);
            setLogs(status.logs || []);
        } catch (error) {
            console.error("Failed to load logs:", error);
        } finally {
            setLoadingLogs(false);
        }
    }

    function formatTimeAgo(dateString: string) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

        if (diffInSeconds < 60) return "just now";
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return date.toLocaleDateString();
    }

    return (
        <div className="chart-card">
            <div className="chart-header">
                <div className="chart-title" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <Clock size={16} color="var(--primary)" />
                    Recent Analysis Runs
                </div>
            </div>

            {loading ? (
                <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>
                    <Loader2 size={24} className="animate-spin" style={{ margin: "0 auto 12px", opacity: 0.5 }} />
                    Loading history...
                </div>
            ) : runs.length === 0 ? (
                <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>
                    No analysis runs found.
                </div>
            ) : (
                <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                        <thead>
                            <tr style={{ borderBottom: "1px solid var(--border-color)", textAlign: "left", color: "var(--text-muted)" }}>
                                <th style={{ padding: "12px 16px", fontWeight: 600 }}>Started</th>
                                <th style={{ padding: "12px 16px", fontWeight: 600 }}>Status</th>
                                <th style={{ padding: "12px 16px", fontWeight: 600 }}>Duration</th>
                                <th style={{ padding: "12px 16px", fontWeight: 600 }}>Items</th>
                                <th style={{ padding: "12px 16px", fontWeight: 600 }}>Score</th>
                                <th style={{ padding: "12px 16px", fontWeight: 600, textAlign: "right" }}>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {runs.map((run) => (
                                <tr key={run.runId} style={{ borderBottom: "1px solid rgba(255,255,255,0.03)" }}>
                                    <td style={{ padding: "12px 16px", fontFamily: "'JetBrains Mono', monospace" }}>
                                        {formatTimeAgo(run.startedAt)}
                                    </td>
                                    <td style={{ padding: "12px 16px" }}>
                                        <span style={{
                                            display: "inline-flex", alignItems: "center", gap: 6,
                                            padding: "4px 8px", borderRadius: 4, fontSize: "0.75rem", fontWeight: 600,
                                            background: run.status === "completed" ? "rgba(16, 185, 129, 0.1)" :
                                                run.status === "running" ? "rgba(59, 130, 246, 0.1)" : "rgba(239, 68, 68, 0.1)",
                                            color: run.status === "completed" ? "#10b981" :
                                                run.status === "running" ? "#3b82f6" : "#ef4444"
                                        }}>
                                            {run.status === "completed" && <CheckCircle size={12} />}
                                            {run.status === "running" && <Loader2 size={12} className="animate-spin" />}
                                            {run.status === "failed" && <AlertCircle size={12} />}
                                            {run.status.toUpperCase()}
                                        </span>
                                    </td>
                                    <td style={{ padding: "12px 16px", fontFamily: "'JetBrains Mono', monospace", color: "var(--text-secondary)" }}>
                                        {run.duration}
                                    </td>
                                    <td style={{ padding: "12px 16px" }}>{run.itemsProcessed}</td>
                                    <td style={{ padding: "12px 16px" }}>
                                        {run.evaluationScore ? Math.round(run.evaluationScore * 100) + "%" : "—"}
                                    </td>
                                    <td style={{ padding: "12px 16px", textAlign: "right" }}>
                                        <button
                                            onClick={() => handleViewLogs(run.runId)}
                                            style={{
                                                background: "none", border: "none", cursor: "pointer",
                                                display: "inline-flex", alignItems: "center", gap: 4,
                                                color: "var(--primary)", fontSize: "0.8rem", fontWeight: 500
                                            }}
                                        >
                                            Logs <ArrowRight size={14} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Logs Modal */}
            {selectedRunId && (
                <div
                    onClick={() => setSelectedRunId(null)}
                    style={{
                        position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
                        background: "rgba(0,0,0,0.9)", backdropFilter: "blur(10px)",
                        zIndex: 2000,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "flex-start", // Start from top to prevent cropping
                        padding: "5vh 24px", // 5% from top
                        cursor: "pointer",
                        overflowY: "auto" // Allow the whole overlay to scroll if needed
                    }}
                >
                    <div
                        onClick={(e) => e.stopPropagation()}
                        style={{
                            background: "#0c1117", border: "1px solid var(--border-color)", borderRadius: 16,
                            width: "100%", maxWidth: 800,
                            maxHeight: "80vh", // Even smaller height to be safe
                            display: "flex", flexDirection: "column",
                            boxShadow: "0 25px 60px -12px rgba(0, 0, 0, 0.9)",
                            cursor: "default",
                            position: "relative",
                            overflow: "hidden",
                            flexShrink: 0 // Modal itself shouldn't shrink
                        }}
                    >
                        {/* Modal Header - Fixed at top */}
                        <div style={{
                            padding: "20px 24px", borderBottom: "1px solid var(--border-color)",
                            display: "flex", alignItems: "center", justifyContent: "space-between",
                            background: "#161b22", flexShrink: 0
                        }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                                <div style={{ background: "rgba(59, 130, 246, 0.15)", padding: 8, borderRadius: 8 }}>
                                    <Terminal size={20} color="var(--primary)" />
                                </div>
                                <div>
                                    <h3 style={{ margin: 0, fontSize: "1rem", fontWeight: 600, color: "#fff" }}>Analysis Run Logs</h3>
                                    <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", fontFamily: "monospace", marginTop: 2 }}>ID: {selectedRunId}</div>
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedRunId(null)}
                                style={{
                                    background: "rgba(255,255,255,0.05)", border: "none", color: "#fff",
                                    cursor: "pointer", width: 32, height: 32, borderRadius: "50%",
                                    display: "flex", alignItems: "center", justifyContent: "center",
                                    transition: "background 0.2s"
                                }}
                            >
                                <X size={18} />
                            </button>
                        </div>

                        {/* Modal Body - Scrollable */}
                        <div style={{
                            flex: 1, overflowY: "auto", padding: 24,
                            fontFamily: "'JetBrains Mono', monospace", fontSize: "0.8rem",
                            display: "flex", flexDirection: "column", gap: 10,
                            background: "#0c1117"
                        }}>
                            {loadingLogs ? (
                                <div style={{ textAlign: "center", padding: 40, color: "var(--text-muted)" }}>
                                    <Loader2 size={24} className="animate-spin" style={{ margin: "0 auto 12px", opacity: 0.5 }} />
                                    Fetching logs...
                                </div>
                            ) : logs.length === 0 ? (
                                <div style={{ textAlign: "center", padding: 40, color: "var(--text-muted)" }}>
                                    No logs available.
                                </div>
                            ) : (
                                logs.map((log, i) => (
                                    <div key={i} style={{ display: "flex", gap: 12, paddingBottom: 8, borderBottom: "1px solid rgba(255,255,255,0.02)" }}>
                                        <div style={{
                                            color: "var(--text-muted)", minWidth: 70, fontSize: "0.75rem", marginTop: 2
                                        }}>
                                            {new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                                        </div>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                                <span style={{
                                                    color: log.status === "error" ? "var(--warning)" :
                                                        log.status === "completed" ? "var(--positive)" : "var(--primary)",
                                                    fontWeight: 600
                                                }}>
                                                    {log.step} {log.duration ? <span style={{ color: "var(--text-secondary)", fontWeight: 400, marginLeft: 6 }}>{log.duration.toFixed(2)}s</span> : ""}
                                                </span>
                                            </div>
                                            {log.message && (
                                                <div style={{ color: "var(--text-primary)", marginTop: 4, lineHeight: 1.4 }}>
                                                    {log.message}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))
                            )}
                            <div ref={logsEndRef} />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
