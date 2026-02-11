import { Router, Request, Response } from "express";

export const contentRouter = Router();

// GET /api/content — Browse platform content
contentRouter.get("/", async (req: Request, res: Response) => {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 20;
    const platform = req.query.platform as string | undefined;
    try {
        res.json({ items: [], page, limit, platform: platform || "all" });
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch content" });
    }
});

// GET /api/content/search — Semantic search via pgvector
contentRouter.get("/search", async (req: Request, res: Response) => {
    const query = req.query.q as string;
    const limit = parseInt(req.query.limit as string) || 10;
    if (!query) {
        return res.status(400).json({ error: "Query parameter 'q' is required" });
    }
    try {
        // TODO: Generate embedding for query, search pgvector
        res.json({ results: [], query, limit });
    } catch (err) {
        res.status(500).json({ error: "Failed to search content" });
    }
});

// GET /api/content/outliers — Viral outliers
contentRouter.get("/outliers", async (_req: Request, res: Response) => {
    try {
        res.json({ outliers: [] });
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch outliers" });
    }
});
