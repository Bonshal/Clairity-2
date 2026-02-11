import { Router, Request, Response } from "express";

export const recommendationsRouter = Router();

// GET /api/recommendations — List recommendations (paginated)
recommendationsRouter.get("/", async (req: Request, res: Response) => {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 10;
    try {
        // TODO: Query recommendations from Neon
        res.json({ recommendations: [], page, limit, total: 0 });
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch recommendations" });
    }
});

// GET /api/recommendations/:id — Recommendation detail
recommendationsRouter.get("/:id", async (req: Request, res: Response) => {
    const { id } = req.params;
    try {
        // TODO: Query recommendation by ID with SEO + GEO data
        res.json({ recommendation: null, id });
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch recommendation" });
    }
});

// POST /api/recommendations/generate — Trigger new recommendation run
recommendationsRouter.post("/generate", async (_req: Request, res: Response) => {
    try {
        // TODO: Push job to BullMQ → Python pipeline
        res.json({ status: "queued", jobId: null });
    } catch (err) {
        res.status(500).json({ error: "Failed to trigger generation" });
    }
});
