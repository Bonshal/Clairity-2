import { Router, Request, Response } from "express";
import { prisma, withRetry } from "../services/neon";
import { Prisma } from "@prisma/client";

export const contentRouter = Router();

const ANALYSIS_SERVICE_URL = process.env.ANALYSIS_SERVICE_URL || "http://127.0.0.1:8000";

// GET /api/content — Browse platform content
contentRouter.get("/", async (req: Request, res: Response) => {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 20;
    const platform = req.query.platform as string | undefined;
    const skip = (page - 1) * limit;

    const where: Prisma.ContentItemWhereInput = {};
    if (platform && platform !== "all") {
        where.platform = platform;
    }

    try {
        const [items, total] = await withRetry(() => Promise.all([
            prisma.contentItem.findMany({
                where,
                skip,
                take: limit,
                orderBy: { fetchedAt: "desc" },
                include: { sentimentResults: true },
            }),
            prisma.contentItem.count({ where }),
        ]));

        // Convert BigInt to string for JSON serialization
        const safeItems = items.map(item => ({
            ...item,
            views: item.views.toString(),
        }));

        res.json({ items: safeItems, page, limit, total, platform: platform || "all" });
    } catch (err: any) {
        console.error("Failed to fetch content:", err);
        res.status(500).json({ error: "Failed to fetch content", details: err.message });
    }
});

// GET /api/content/search — Semantic search via pgvector (Forward to Python)
contentRouter.get("/search", async (req: Request, res: Response) => {
    const query = req.query.q as string;
    const limit = parseInt(req.query.limit as string) || 10;
    if (!query) {
        res.status(400).json({ error: "Query parameter 'q' is required" });
        return;
    }
    try {
        // Forward to Python service which has the embedding model
        const response = await fetch(`${ANALYSIS_SERVICE_URL}/search/semantic?q=${encodeURIComponent(query)}&limit=${limit}`);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Search service error: ${response.status} ${errorText}`);
        }

        const data = await response.json() as any;
        res.json(data);
    } catch (err: any) {
        console.error("Failed to search content:", err);
        res.status(500).json({ error: "Failed to search content", details: err.message });
    }
});

// GET /api/content/outliers — Viral outliers (High engagement)
contentRouter.get("/outliers", async (_req: Request, res: Response) => {
    try {
        // Simple heuristic: Top items by views + likes
        const outliers = await prisma.contentItem.findMany({
            orderBy: [
                { views: "desc" },
                { likes: "desc" }
            ],
            take: 10,
        });

        const safeOutliers = outliers.map(item => ({
            ...item,
            views: item.views.toString(),
        }));

        res.json({ outliers: safeOutliers });
    } catch (err: any) {
        console.error("Failed to fetch outliers:", err);
        res.status(500).json({ error: "Failed to fetch outliers", details: err.message });
    }
});
