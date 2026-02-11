import { Router, Request, Response } from "express";

export const dashboardRouter = Router();

// GET /api/dashboard/kpis — Dashboard KPI summary
dashboardRouter.get("/kpis", async (_req: Request, res: Response) => {
    try {
        // TODO: Query Neon for aggregated KPIs
        res.json({
            totalContent: 0,
            trendCount: 0,
            avgSentiment: 0,
            activePlatforms: 3,
            lastIngestion: null,
        });
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch KPIs" });
    }
});

// GET /api/dashboard/alerts — Recent alerts/notifications
dashboardRouter.get("/alerts", async (_req: Request, res: Response) => {
    try {
        // TODO: Query recent alerts from Neon
        res.json({ alerts: [] });
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch alerts" });
    }
});
