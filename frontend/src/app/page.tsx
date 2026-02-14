"use client";

import AppShell from "@/components/AppShell";
import KPICards from "@/components/dashboard/KPICards";
import TrendChart from "@/components/dashboard/TrendChart";
import SentimentDonut from "@/components/dashboard/SentimentDonut";
import TopTrends from "@/components/dashboard/TopTrends";
import RecentAlerts from "@/components/dashboard/RecentAlerts";
import PlatformBreakdown from "@/components/dashboard/PlatformBreakdown";
import PipelineTrigger from "@/components/dashboard/PipelineTrigger";
import AnalysisHistory from "@/components/dashboard/AnalysisHistory";

export default function DashboardPage() {
  return (
    <AppShell>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div>
          <h2 className="page-title">
            Market <span className="gradient-text">Intelligence</span>
          </h2>
          <p className="page-subtitle">
            Real-time insights across Reddit, X, and YouTube — updated just now
          </p>
        </div>
        <PipelineTrigger />
      </div>

      <KPICards />

      <div className="chart-grid-3">
        <TrendChart />
        <SentimentDonut />
      </div>

      <div className="chart-grid">
        <TopTrends />
        <RecentAlerts />
      </div>

      <PlatformBreakdown />

      <div className="mt-6">
        <AnalysisHistory />
      </div>
    </AppShell>
  );
}
