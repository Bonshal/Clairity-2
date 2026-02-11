"use client";

import AppShell from "@/components/AppShell";
import { Globe, FileText, HelpCircle, Code, CheckCircle2 } from "lucide-react";

const GEO_ITEMS = [
    {
        title: "Complete Guide to AI Code Review Tools in 2026",
        geoScore: 82,
        entities: ["GPT-4", "CodeRabbit", "GitHub Copilot", "SonarQube", "DeepCode"],
        citationClaims: 6,
        faqs: 4,
        schema: ["HowTo", "FAQPage", "SoftwareApplication"],
        structureNotes: "Use definition lists for each tool. Add benchmark tables with concrete numbers. Include FAQ section at the bottom.",
    },
    {
        title: "How to Build MCP Server Integrations from Scratch",
        geoScore: 88,
        entities: ["Model Context Protocol", "Claude", "JSON-RPC", "stdio", "SSE"],
        citationClaims: 8,
        faqs: 5,
        schema: ["HowTo", "FAQPage", "TechArticle"],
        structureNotes: "Break into numbered steps. Each step should be a standalone citeable block. Include code examples with language annotations.",
    },
    {
        title: "Open-Source LLM Alternatives: The Definitive Comparison",
        geoScore: 79,
        entities: ["Llama 4", "Mistral", "Qwen", "DeepSeek R2", "Gemma"],
        citationClaims: 12,
        faqs: 6,
        schema: ["FAQPage", "Table", "Review"],
        structureNotes: "Use comparison tables with clear column headers. Each model should have a structured pros/cons section. Define evaluation criteria upfront.",
    },
];

export default function GEOPage() {
    return (
        <AppShell>
            <div className="page-header">
                <h2 className="page-title">
                    GEO <span className="gradient-text">Optimization</span>
                </h2>
                <p className="page-subtitle">
                    Generative Engine Optimization — structure content for AI citation and visibility
                </p>
            </div>

            {/* Explanation card */}
            <div className="glass-card no-hover" style={{ marginBottom: 24, background: "var(--accent-gradient-subtle)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
                    <Globe size={20} color="var(--accent-1)" />
                    <span style={{ fontWeight: 600, fontSize: "0.95rem" }}>What is GEO?</span>
                </div>
                <p style={{ fontSize: "0.88rem", color: "var(--text-secondary)", lineHeight: 1.6, maxWidth: 700 }}>
                    Generative Engine Optimization ensures your content is structured to be cited by AI models like ChatGPT, Gemini, and Perplexity.
                    The GEO score measures how likely your content is to be referenced in AI-generated answers based on entity coverage,
                    structured data, and citation-worthy claims.
                </p>
            </div>

            {/* GEO Cards */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                {GEO_ITEMS.map((item, i) => (
                    <div key={i} className="glass-card" style={{ padding: "24px 28px" }}>
                        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 20 }}>
                            <div>
                                <div style={{ fontSize: "1.05rem", fontWeight: 600, marginBottom: 6 }}>{item.title}</div>
                                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                                    {item.schema.map((s) => (
                                        <span key={s} className="tag" style={{ background: "rgba(14,165,233,0.1)", color: "#0ea5e9", borderColor: "rgba(14,165,233,0.2)" }}>
                                            <Code size={10} /> {s}
                                        </span>
                                    ))}
                                </div>
                            </div>
                            {/* GEO Score gauge */}
                            <div style={{ textAlign: "center" }}>
                                <div
                                    style={{
                                        width: 64,
                                        height: 64,
                                        borderRadius: "50%",
                                        background: `conic-gradient(${item.geoScore > 80 ? "#00e5c8" : "#fbbf24"} ${item.geoScore * 3.6}deg, rgba(255,255,255,0.04) 0deg)`,
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                    }}
                                >
                                    <div
                                        style={{
                                            width: 52,
                                            height: 52,
                                            borderRadius: "50%",
                                            background: "var(--surface-2)",
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            fontFamily: "'JetBrains Mono', monospace",
                                            fontWeight: 700,
                                            fontSize: "1.1rem",
                                            color: item.geoScore > 80 ? "var(--accent-1)" : "var(--warning)",
                                        }}
                                    >
                                        {item.geoScore}
                                    </div>
                                </div>
                                <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", marginTop: 4, fontWeight: 500 }}>GEO SCORE</div>
                            </div>
                        </div>

                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 20 }}>
                            {/* Entities */}
                            <div>
                                <div style={{ fontSize: "0.72rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-muted)", marginBottom: 8 }}>
                                    Key Entities
                                </div>
                                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                                    {item.entities.map((e) => (
                                        <span key={e} className="tag">{e}</span>
                                    ))}
                                </div>
                            </div>

                            {/* Stats */}
                            <div>
                                <div style={{ fontSize: "0.72rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-muted)", marginBottom: 8 }}>
                                    Citation Metrics
                                </div>
                                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.85rem" }}>
                                        <FileText size={14} color="var(--accent-1)" />
                                        <span style={{ fontFamily: "'JetBrains Mono'", fontWeight: 600 }}>{item.citationClaims}</span>
                                        <span style={{ color: "var(--text-muted)" }}>citation-worthy claims</span>
                                    </div>
                                    <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.85rem" }}>
                                        <HelpCircle size={14} color="var(--info)" />
                                        <span style={{ fontFamily: "'JetBrains Mono'", fontWeight: 600 }}>{item.faqs}</span>
                                        <span style={{ color: "var(--text-muted)" }}>FAQ suggestions</span>
                                    </div>
                                </div>
                            </div>

                            {/* Structure notes */}
                            <div>
                                <div style={{ fontSize: "0.72rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-muted)", marginBottom: 8 }}>
                                    Structure Guidance
                                </div>
                                <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                                    {item.structureNotes}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </AppShell>
    );
}
