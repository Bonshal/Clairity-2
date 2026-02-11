import { Router, Request, Response } from "express";

export const trendsRouter = Router();

// GET /api/trends/top — Top trending keywords
trendsRouter.get("/top", async (req: Request, res: Response) => {
    const limit = parseInt(req.query.limit as string) || 10;
    try {
        // TODO: Query trend_signals from Neon, ordered by momentum
        res.json({ trends: [], limit });
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch trends" });
    }
});

// GET /api/trends/timeline — Trend timeline data
trendsRouter.get("/timeline", async (req: Request, res: Response) => {
    const days = parseInt(req.query.days as string) || 30;
    try {
        // TODO: Query time-series trend data
        res.json({ timeline: [], days });
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch timeline" });
    }
});

// GET /api/trends/:keyword — Keyword trend detail
trendsRouter.get("/:keyword", async (req: Request, res: Response) => {
    const { keyword } = req.params;
    try {
        // TODO: Query specific keyword trend data
        res.json({ keyword, trend: null });
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch trend detail" });
    }
});
