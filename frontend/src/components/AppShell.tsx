"use client";

import { useState, ReactNode } from "react";
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

const NAV_ITEMS = [
    {
        section: "Overview",
        items: [
            { label: "Dashboard", href: "/", icon: LayoutDashboard },
            { label: "Trends", href: "/trends", icon: TrendingUp, badge: "12" },
            { label: "Recommendations", href: "/recommendations", icon: Lightbulb, badge: "5" },
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
    const pathname = usePathname();

    return (
        <div className="app-layout">
            {/* Sidebar */}
            <nav className={`sidebar ${collapsed ? "collapsed" : ""}`}>
                <div className="sidebar-logo" onClick={() => setCollapsed(!collapsed)}>
                    <div className="sidebar-logo-icon">
                        <Sparkles size={18} color="#06080d" strokeWidth={2.5} />
                    </div>
                    <span className="sidebar-logo-text gradient-text">Nexus AI</span>
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
                                        {item.badge && (
                                            <span className="nav-badge">{item.badge}</span>
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
