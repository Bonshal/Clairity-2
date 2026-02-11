"use client";

import AppShell from "@/components/AppShell";
import { Settings as SettingsIcon, Plus, Trash2, Save, KeyRound, Database, Bot, Globe } from "lucide-react";
import { useState } from "react";

const INITIAL_NICHES = [
    { id: 1, name: "AI Developer Tools", keywords: ["AI code review", "AI pair programming", "developer tools AI"], active: true },
    { id: 2, name: "Open Source AI", keywords: ["open source LLM", "local inference", "self-hosted AI"], active: true },
    { id: 3, name: "AI Content Creation", keywords: ["AI writing tools", "AI video generation", "content automation"], active: false },
];

export default function SettingsPage() {
    const [niches, setNiches] = useState(INITIAL_NICHES);

    return (
        <AppShell>
            <div className="page-header">
                <h2 className="page-title">
                    <span className="gradient-text">Settings</span>
                </h2>
                <p className="page-subtitle">
                    Configure niches, API keys, and pipeline preferences
                </p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr", gap: 24 }}>
                {/* Niche config */}
                <div className="chart-card">
                    <div className="chart-header">
                        <div className="chart-title" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                            <Bot size={16} color="#00e5c8" />
                            Niche Configuration
                        </div>
                        <button className="btn btn-primary" style={{ fontSize: "0.82rem", padding: "6px 14px" }}>
                            <Plus size={14} /> Add Niche
                        </button>
                    </div>

                    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                        {niches.map((niche) => (
                            <div
                                key={niche.id}
                                style={{
                                    padding: "16px 20px",
                                    borderRadius: 10,
                                    background: "rgba(255,255,255,0.02)",
                                    border: `1px solid ${niche.active ? "rgba(0,229,200,0.15)" : "rgba(255,255,255,0.04)"}`,
                                    display: "flex",
                                    flexDirection: "column",
                                    gap: 10,
                                }}
                            >
                                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                                    {/* Active toggle */}
                                    <div
                                        style={{
                                            width: 36,
                                            height: 20,
                                            borderRadius: 10,
                                            background: niche.active ? "rgba(0,229,200,0.3)" : "rgba(255,255,255,0.06)",
                                            position: "relative",
                                            cursor: "pointer",
                                            transition: "background 0.2s",
                                        }}
                                        onClick={() => {
                                            setNiches(niches.map(n => n.id === niche.id ? { ...n, active: !n.active } : n));
                                        }}
                                    >
                                        <div
                                            style={{
                                                width: 16,
                                                height: 16,
                                                borderRadius: "50%",
                                                background: niche.active ? "var(--accent-1)" : "var(--text-muted)",
                                                position: "absolute",
                                                top: 2,
                                                left: niche.active ? 18 : 2,
                                                transition: "left 0.2s, background 0.2s",
                                            }}
                                        />
                                    </div>
                                    <span style={{ fontWeight: 600, fontSize: "0.92rem" }}>{niche.name}</span>
                                    <button
                                        style={{
                                            marginLeft: "auto",
                                            background: "transparent",
                                            border: "none",
                                            color: "var(--text-muted)",
                                            cursor: "pointer",
                                            padding: 4,
                                        }}
                                    >
                                        <Trash2 size={14} />
                                    </button>
                                </div>
                                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                                    {niche.keywords.map((kw) => (
                                        <span key={kw} className="tag">{kw}</span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* API & System Config */}
                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                    <div className="chart-card">
                        <div className="chart-title" style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
                            <KeyRound size={16} color="#fbbf24" />
                            API Keys
                        </div>
                        {[
                            { label: "Google / Gemini", connected: true },
                            { label: "GetXAPI (Twitter)", connected: true },
                            { label: "YouTube Data API", connected: true },
                            { label: "Apify (Reddit)", connected: false },
                        ].map((api) => (
                            <div
                                key={api.label}
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "space-between",
                                    padding: "10px 0",
                                    borderBottom: "1px solid rgba(255,255,255,0.04)",
                                    fontSize: "0.88rem",
                                }}
                            >
                                <span>{api.label}</span>
                                <span
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 6,
                                        fontSize: "0.78rem",
                                        color: api.connected ? "var(--positive)" : "var(--text-muted)",
                                    }}
                                >
                                    <span
                                        style={{
                                            width: 6,
                                            height: 6,
                                            borderRadius: "50%",
                                            background: api.connected ? "var(--positive)" : "var(--text-muted)",
                                            display: "inline-block",
                                        }}
                                    />
                                    {api.connected ? "Connected" : "Not configured"}
                                </span>
                            </div>
                        ))}
                    </div>

                    <div className="chart-card">
                        <div className="chart-title" style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
                            <Database size={16} color="#0ea5e9" />
                            Databases
                        </div>
                        {[
                            { label: "Neon PostgreSQL", status: "Connected", ping: "24ms" },
                            { label: "MongoDB Atlas", status: "Connected", ping: "45ms" },
                            { label: "Upstash Redis", status: "Connected", ping: "12ms" },
                        ].map((db) => (
                            <div
                                key={db.label}
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "space-between",
                                    padding: "10px 0",
                                    borderBottom: "1px solid rgba(255,255,255,0.04)",
                                    fontSize: "0.88rem",
                                }}
                            >
                                <span>{db.label}</span>
                                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                                    <span style={{ fontFamily: "'JetBrains Mono'", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                                        {db.ping}
                                    </span>
                                    <span style={{ display: "flex", alignItems: "center", gap: 4, fontSize: "0.78rem", color: "var(--positive)" }}>
                                        <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--positive)", display: "inline-block" }} />
                                        {db.status}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="chart-card">
                        <div className="chart-title" style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
                            <Globe size={16} color="#c084fc" />
                            Pipeline Schedule
                        </div>
                        <div style={{ fontSize: "0.88rem", color: "var(--text-secondary)", marginBottom: 12 }}>
                            The pipeline runs automatically to keep your intelligence fresh.
                        </div>
                        {[
                            { label: "Full Pipeline", schedule: "Every 6 hours" },
                            { label: "Trend Update", schedule: "Every 2 hours" },
                            { label: "Quick Ingest", schedule: "Every 30 minutes" },
                        ].map((item) => (
                            <div
                                key={item.label}
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "space-between",
                                    padding: "10px 0",
                                    borderBottom: "1px solid rgba(255,255,255,0.04)",
                                    fontSize: "0.88rem",
                                }}
                            >
                                <span>{item.label}</span>
                                <span style={{ fontFamily: "'JetBrains Mono'", fontSize: "0.82rem", color: "var(--accent-1)" }}>
                                    {item.schedule}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </AppShell>
    );
}
