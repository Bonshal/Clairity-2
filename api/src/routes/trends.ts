import { Router, Request, Response } from "express";
import { prisma, withRetry } from "../services/neon";

export const trendsRouter = Router();

// DELETE /api/trends/flush — Clear all old trend data (use before re-running pipeline)
trendsRouter.delete("/flush", async (_req: Request, res: Response) => {
    try {
        const result = await prisma.trendSignal.deleteMany();
        console.log(`Flushed ${result.count} stale trend signals`);
        res.json({ message: `Cleared ${result.count} old trend signals`, count: result.count });
    } catch (err: any) {
        console.error("Failed to flush trends:", err);
        res.status(500).json({ error: "Failed to flush trends", details: err.message });
    }
});
// GET /api/trends/top — Top trending keywords
trendsRouter.get("/top", async (req: Request, res: Response) => {
    const limit = parseInt(req.query.limit as string) || 10;
    try {
        const trends = await withRetry(() => prisma.trendSignal.findMany({
            orderBy: { momentum7d: "desc" },
            take: limit,
            include: { topicCluster: true }, // Include topic info if needed
        }));
        res.json({ trends, limit });
    } catch (err: any) {
        console.error("Failed to fetch top trends:", err);
        res.status(500).json({ error: "Failed to fetch top trends", details: err.message });
    }
});

// GET /api/trends/timeline — Trend timeline data
trendsRouter.get("/timeline", async (req: Request, res: Response) => {
    const days = parseInt(req.query.days as string) || 30;
    try {
        // Aggregate daily trend discoveries
        const result = await prisma.$queryRaw`
            SELECT 
                DATE_TRUNC('day', detected_at) as date, 
                COUNT(*) as count,
                AVG(confidence) as avg_confidence
            FROM trend_signals
            WHERE detected_at >= NOW() - (${days} || ' days')::INTERVAL
            GROUP BY 1
            ORDER BY 1 ASC
        `;

        // Convert BigInt counts to number if necessary (Prisma returns BigInt for count in raw)
        const timeline = (result as any[]).map(row => ({
            date: row.date,
            count: Number(row.count),
            avgConfidence: row.avg_confidence
        }));

        res.json({ timeline, days });
    } catch (err: any) {
        console.error("Failed to fetch timeline:", err);
        res.status(500).json({ error: "Failed to fetch timeline", details: err.message });
    }
});

// GET /api/trends/:keyword — Keyword trend detail
trendsRouter.get("/:keyword", async (req: Request, res: Response) => {
    const keyword = req.params.keyword as string;
    try {
        const trend = await prisma.trendSignal.findFirst({
            where: { keyword: { equals: keyword, mode: "insensitive" } },
            orderBy: { detectedAt: "desc" },
            include: { topicCluster: true },
        });

        if (!trend) {
            res.status(404).json({ error: "Trend not found for keyword" });
            return;
        }

        // Also fetch related content samples
        const relatedContent = await prisma.contentItem.findMany({
            where: {
                OR: [
                    { body: { contains: keyword, mode: "insensitive" } },
                    { title: { contains: keyword, mode: "insensitive" } }
                ]
            },
            take: 5,
            orderBy: { fetchedAt: "desc" },
            select: { id: true, title: true, platform: true, url: true }
        });

        res.json({ keyword, trend, relatedContent });
    } catch (err: any) {
        console.error("Failed to fetch trend detail:", err);
        res.status(500).json({ error: "Failed to fetch trend detail", details: err.message });
    }
});
