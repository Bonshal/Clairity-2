"use client";

import { useState, useRef, useEffect } from "react";
import { Play, Loader2, CheckCircle, AlertCircle, X, Terminal, ChevronRight } from "lucide-react";
import { triggerPipeline, fetchPipelineStatus } from "@/lib/api";

type LogEntry = {
    timestamp: string;
    step: string;
    status: string;
    message: string;
    duration?: number;
};

export default function PipelineTrigger() {
    const [status, setStatus] = useState<"idle" | "running" | "completed" | "error">("idle");
    const [runId, setRunId] = useState<string | null>(null);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const logsEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom of logs
    useEffect(() => {
        if (logsEndRef.current) {
            logsEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [logs]);

    async function handleRun() {
        if (status === "running") {
            setIsOpen(true);
            return;
        }

        setStatus("running");
        setLogs([]);
        setIsOpen(true);

        try {
            const data = await triggerPipeline();
            setRunId(data.runId);

            // Poll for status
            const interval = setInterval(async () => {
                try {
                    const statusData = await fetchPipelineStatus(data.runId);

                    if (statusData.logs) {
                        setLogs(statusData.logs);
                    }

                    if (statusData.status === "completed") {
                        setStatus("completed");
                        clearInterval(interval);
                        setTimeout(() => {
                            window.location.reload(); // Refresh to show new data
                        }, 2000);
                    } else if (statusData.status === "failed") {
                        setStatus("error");
                        clearInterval(interval);
                    }
                } catch (e) {
                    console.error("Poll failed", e);
                    clearInterval(interval);
                    setStatus("error");
                }
            }, 1000);
        } catch (e) {
            console.error("Trigger failed", e);
            setStatus("error");
            setLogs(prev => [...prev, {
                timestamp: new Date().toISOString(),
                step: "Trigger",
                status: "error",
                message: "Failed to start pipeline: " + String(e)
            }]);
        }
    }

    return (
        <>
            <button
                className={`btn ${status === "running" ? "btn-secondary" : "btn-primary"}`}
                onClick={handleRun}
                style={{ display: "flex", alignItems: "center", gap: 8 }}
            >
                {status === "idle" && <Play size={16} />}
                {status === "running" && <Loader2 size={16} className="animate-spin" />}
                {status === "completed" && <CheckCircle size={16} />}
                {status === "error" && <AlertCircle size={16} />}

                {status === "idle" && "Run Analysis"}
                {status === "running" && "Analyzing..."}
                {status === "completed" && "Done"}
                {status === "error" && "Failed"}
            </button>

            {isOpen && (
                <div style={{
                    position: "fixed",
                    top: 0, left: 0, right: 0, bottom: 0,
                    background: "rgba(0,0,0,0.6)",
                    backdropFilter: "blur(4px)",
                    zIndex: 1000,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    padding: 24
                }}>
                    <div style={{
                        background: "#0d1117",
                        border: "1px solid var(--border-color)",
                        borderRadius: 12,
                        width: "100%",
                        maxWidth: 600,
                        maxHeight: "80vh",
                        display: "flex",
                        flexDirection: "column",
                        boxShadow: "0 20px 50px rgba(0,0,0,0.5)"
                    }}>
                        <div style={{
                            padding: "16px 20px",
                            borderBottom: "1px solid var(--border-color)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between"
                        }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                                <Terminal size={18} color="var(--primary)" />
                                <h3 style={{ margin: 0, fontSize: "1rem", fontWeight: 600 }}>Analysis Logs</h3>
                            </div>
                            <button
                                onClick={() => setIsOpen(false)}
                                style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
                            >
                                <X size={20} />
                            </button>
                        </div>

                        <div style={{
                            flex: 1,
                            overflowY: "auto",
                            padding: 20,
                            fontFamily: "'JetBrains Mono', monospace",
                            fontSize: "0.85rem",
                            display: "flex",
                            flexDirection: "column",
                            gap: 12
                        }}>
                            {logs.length === 0 && (
                                <div style={{ color: "var(--text-muted)", textAlign: "center", padding: 20 }}>
                                    <Loader2 size={24} className="animate-spin" style={{ margin: "0 auto 12px", opacity: 0.5 }} />
                                    Initializing pipeline...
                                </div>
                            )}

                            {logs.map((log, i) => (
                                <div key={i} style={{ display: "flex", gap: 12, opacity: 0, animation: "fadeIn 0.3s forwards" }}>
                                    <div style={{
                                        color: "var(--text-muted)",
                                        minWidth: 70,
                                        fontSize: "0.75rem",
                                        marginTop: 2
                                    }}>
                                        {new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                                    </div>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
                                            <span style={{
                                                color: log.status === "error" ? "var(--warning)" :
                                                    log.status === "completed" ? "var(--positive)" : "var(--primary)",
                                                fontWeight: 600
                                            }}>
                                                {log.step} {log.duration ? <span style={{ color: "var(--text-secondary)", fontWeight: 400, marginLeft: 6 }}>{log.duration.toFixed(2)}s</span> : ""}
                                            </span>
                                            {log.status === "running" && <Loader2 size={10} className="animate-spin" />}
                                        </div>
                                        <div style={{ color: "var(--text-primary)", lineHeight: 1.5 }}>
                                            {log.message}
                                        </div>
                                    </div>
                                </div>
                            ))}
                            <div ref={logsEndRef} />
                        </div>
                    </div>
                </div>
            )}
            <style jsx>{`
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(4px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            `}</style>
        </>
    );
}
