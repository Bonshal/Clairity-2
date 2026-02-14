"use client";

import { useState, useEffect, ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    TrendingUp,
    Lightbulb,
    Search,
    Target,
    Globe,
    Workflow,
    Settings,
    PanelLeftClose,
    PanelLeftOpen,
    Zap,
    Bell,
    Sparkles,
} from "lucide-react";
import { fetchDashboardKPIs, fetchRecommendations, fetchContent } from "@/lib/api";

const NAV_ITEMS = [
    {
        section: "Overview",
        items: [
            { label: "Dashboard", href: "/", icon: LayoutDashboard },
            { label: "Trends", href: "/trends", icon: TrendingUp, badge: "0" },
            { label: "Recommendations", href: "/recommendations", icon: Lightbulb, badge: "0" },
        ],
    },
    {
        section: "Intelligence",
        items: [
            { label: "Content Explorer", href: "/content", icon: Search },
            { label: "SEO Analysis", href: "/seo", icon: Target },
            { label: "GEO Optimization", href: "/geo", icon: Globe },
        ],
    },
    {
        section: "System",
        items: [
            { label: "Pipeline", href: "/pipeline", icon: Workflow },
            { label: "Settings", href: "/settings", icon: Settings },
        ],
    },
];

export default function AppShell({ children }: { children: ReactNode }) {
    const [collapsed, setCollapsed] = useState(false);
    const [counts, setCounts] = useState({ trends: 0, recs: 0, content: 0 });
    const pathname = usePathname();

    useEffect(() => {
        async function loadCounts() {
            try {
                const [kpis, recs, content] = await Promise.all([
                    fetchDashboardKPIs(),
                    fetchRecommendations(1, 1),
                    fetchContent(1, 1)
                ]);
                setCounts({
                    trends: kpis.trendCount || 0,
                    recs: recs.total || 0,
                    content: content.total || 0
                });
            } catch (err) {
                console.error("Failed to load sidebar counts:", err);
            }
        }
        loadCounts();
    }, []);

    const getBadge = (href: string) => {
        if (href === "/trends" && counts.trends > 0) return counts.trends > 99 ? "99+" : counts.trends.toString();
        if (href === "/recommendations" && counts.recs > 0) return counts.recs > 99 ? "99+" : counts.recs.toString();
        if (href === "/content" && counts.content > 0) return counts.content > 999 ? "1k+" : counts.content.toString();
        return null;
    };

    return (
        <div className="app-layout">
            {/* Sidebar */}
            <nav className={`sidebar ${collapsed ? "collapsed" : ""}`}>
                <div className="sidebar-logo" onClick={() => setCollapsed(!collapsed)}>
                    <div className="sidebar-logo-icon">
                        <Sparkles size={18} color="#06080d" strokeWidth={2.5} />
                    </div>
                    <span className="sidebar-logo-text gradient-text">Clairity</span>
                </div>

                <div className="sidebar-nav">
                    {NAV_ITEMS.map((section) => (
                        <div key={section.section}>
                            <div className="sidebar-section-label">{section.section}</div>
                            {section.items.map((item) => {
                                const isActive =
                                    item.href === "/"
                                        ? pathname === "/"
                                        : pathname.startsWith(item.href);

                                const badge = getBadge(item.href);

                                return (
                                    <Link
                                        key={item.href}
                                        href={item.href}
                                        className={`nav-item ${isActive ? "active" : ""}`}
                                    >
                                        <span className="nav-item-icon">
                                            <item.icon size={18} />
                                        </span>
                                        <span className="nav-item-label">{item.label}</span>
                                        {badge && (
                                            <span className="nav-badge">{badge}</span>
                                        )}
                                    </Link>
                                );
                            })}
                        </div>
                    ))}
                </div>

                <div className="sidebar-footer">
                    <button
                        className="sidebar-toggle"
                        onClick={() => setCollapsed(!collapsed)}
                    >
                        {collapsed ? (
                            <PanelLeftOpen size={16} />
                        ) : (
                            <>
                                <PanelLeftClose size={16} />
                                <span className="nav-item-label">Collapse</span>
                            </>
                        )}
                    </button>
                </div>
            </nav>

            {/* Header */}
            <header className={`top-header ${collapsed ? "collapsed" : ""}`}>
                <h1 className="header-title">
                    {NAV_ITEMS.flatMap((s) => s.items).find(
                        (i) =>
                            i.href === "/"
                                ? pathname === "/"
                                : pathname.startsWith(i.href)
                    )?.label || "Dashboard"}
                </h1>
                <div className="header-right">
                    <div className="header-status">
                        <span className="status-dot" />
                        <span>Pipeline Active</span>
                    </div>
                    <button className="header-btn" title="Notifications">
                        <Bell size={16} />
                    </button>
                    <button className="header-btn" title="Quick Run">
                        <Zap size={16} />
                    </button>
                </div>
            </header>

            {/* Content */}
            <main className={`main-content ${collapsed ? "collapsed" : ""}`}>
                {children}
            </main>
        </div>
    );
}
