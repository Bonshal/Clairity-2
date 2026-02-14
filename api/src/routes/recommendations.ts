import { Router, Request, Response } from "express";
import { prisma } from "../services/neon";

export const recommendationsRouter = Router();

const ANALYSIS_SERVICE_URL = process.env.ANALYSIS_SERVICE_URL || "http://127.0.0.1:8000";

// GET /api/recommendations — List recommendations (paginated)
recommendationsRouter.get("/", async (req: Request, res: Response) => {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 10;
    const skip = (page - 1) * limit;

    try {
        const [recommendations, total] = await Promise.all([
            prisma.recommendation.findMany({
                skip,
                take: limit,
                orderBy: { createdAt: "desc" },
            }),
            prisma.recommendation.count(),
        ]);

        res.json({ recommendations, page, limit, total });
    } catch (err: any) {
        console.error("Failed to fetch recommendations:", err);
        res.status(500).json({ error: "Failed to fetch recommendations", details: err.message });
    }
});

// GET /api/recommendations/:id — Recommendation detail
recommendationsRouter.get("/:id", async (req: Request, res: Response) => {
    const id = req.params.id as string;
    try {
        const recommendation = await prisma.recommendation.findUnique({
            where: { id },
        });

        if (!recommendation) {
            res.status(404).json({ error: "Recommendation not found" });
            return; // Explicit return to avoid execution continue
        }

        res.json({ recommendation, id });
    } catch (err: any) {
        console.error("Failed to fetch recommendation:", err);
        res.status(500).json({ error: "Failed to fetch recommendation", details: err.message });
    }
});

// POST /api/recommendations/generate — Trigger new recommendation run
recommendationsRouter.post("/generate", async (req: Request, res: Response) => {
    try {
        // Trigger full pipeline via Python service
        // Assume default niche/platforms if not provided, or take from body
        const { niche_id = "default", platforms = ["twitter", "youtube"] } = req.body;

        const response = await fetch(`${ANALYSIS_SERVICE_URL}/pipeline/run`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ niche_id, platforms }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Analysis service error: ${response.status} ${errorText}`);
        }

        const data = await response.json() as any;
        res.json({ status: "queued", runId: data.run_id });
    } catch (err: any) {
        console.error("Failed to trigger generation:", err);
        res.status(500).json({ error: "Failed to trigger generation", details: err.message });
    }
});
