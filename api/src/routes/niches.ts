import { Router, Request, Response } from "express";

export const nichesRouter = Router();

// GET /api/niches — List user niches
nichesRouter.get("/", async (_req: Request, res: Response) => {
    try {
        res.json({ niches: [] });
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch niches" });
    }
});

// POST /api/niches — Create niche config
nichesRouter.post("/", async (req: Request, res: Response) => {
    const { name, keywords, subreddits, twitterQueries, youtubeQueries } = req.body;
    try {
        // TODO: Insert niche into Neon
        res.status(201).json({ niche: { name, keywords, subreddits, twitterQueries, youtubeQueries } });
    } catch (err) {
        res.status(500).json({ error: "Failed to create niche" });
    }
});

// PUT /api/niches/:id — Update niche config
nichesRouter.put("/:id", async (req: Request, res: Response) => {
    const { id } = req.params;
    try {
        res.json({ niche: null, id });
    } catch (err) {
        res.status(500).json({ error: "Failed to update niche" });
    }
});
