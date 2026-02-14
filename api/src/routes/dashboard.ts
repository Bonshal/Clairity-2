import { Router, Request, Response } from "express";
import { prisma } from "../services/neon";
import { Prisma } from "@prisma/client";

export const dashboardRouter = Router();

// GET /api/dashboard/kpis — Dashboard KPI summary
dashboardRouter.get("/kpis", async (_req: Request, res: Response) => {
    try {
        const [
            contentCount,
            trendCount,
            sentimentAgg,
            platformsAgg,
            lastItem,
            sentimentGroups,
            trendGroups,
            topTrends,
        ] = await Promise.all([
            prisma.contentItem.count(),
            prisma.trendSignal.count(),
            prisma.sentimentResult.aggregate({
                _avg: { sentimentScore: true },
            }),
            // Use raw query for platform stats (count + sentiment) as Prisma groupBy doesn't support relations well
            prisma.$queryRaw`
                SELECT 
                    c.platform, 
                    COUNT(c.id) as count, 
                    AVG(s.sentiment_score) as avg_sentiment
                FROM content_items c
                LEFT JOIN sentiment_results s ON c.id = s.content_id
                GROUP BY c.platform
            `,
            prisma.contentItem.findFirst({
                orderBy: { fetchedAt: "desc" },
                select: { fetchedAt: true },
            }),
            prisma.sentimentResult.groupBy({
                by: ["sentiment"],
                _count: true,
            }),
            prisma.trendSignal.groupBy({
                by: ["direction"],
                _count: true,
            }),
            // Fetch top 5 trends for per-topic sentiment
            prisma.trendSignal.findMany({
                take: 5,
                orderBy: { momentum7d: "desc" },
                where: { direction: { in: ["emerging", "viral"] } },
            }),
        ]);

        const avgSentiment = sentimentAgg._avg.sentimentScore || 0;
        const lastIngestion = lastItem?.fetchedAt || null;

        // Process sentiment distribution
        const sentimentCounts = { positive: 0, neutral: 0, negative: 0 };
        (sentimentGroups as any[]).forEach((item: any) => {
            if (item.sentiment === "positive") sentimentCounts.positive = item._count;
            else if (item.sentiment === "neutral") sentimentCounts.neutral = item._count;
            else if (item.sentiment === "negative") sentimentCounts.negative = item._count;
        });

        // Process trend counts by direction
        let emergingTrendsCount = 0;
        let viralSignalsCount = 0;
        (trendGroups as any[]).forEach((item: any) => {
            if (item.direction === "emerging") emergingTrendsCount += item._count;
            if (item.direction === "viral") viralSignalsCount += item._count;
        });

        // Process platform distribution
        const platformStats = platformsAgg as any[];
        const activePlatforms = platformStats.length;

        const platformCounts = platformStats.map((p: any) => ({
            platform: p.platform,
            count: Number(p.count),
            sentiment: p.avg_sentiment || 0,
        }));

        // Per-topic sentiment: for the top trending keyword, compute sentiment
        // of content that mentions it. This replaces the useless global average.
        let topTrendSentiment = null;
        if (topTrends.length > 0) {
            const topKeyword = topTrends[0].keyword;
            try {
                const topicSentiment = await prisma.$queryRaw`
                    SELECT 
                        s.sentiment,
                        COUNT(*) as count,
                        AVG(s.sentiment_score) as avg_score
                    FROM content_items c
                    JOIN sentiment_results s ON c.id = s.content_id
                    WHERE LOWER(c.title || ' ' || COALESCE(c.body, '')) LIKE ${'%' + topKeyword.toLowerCase() + '%'}
                    GROUP BY s.sentiment
                ` as any[];

                topTrendSentiment = {
                    keyword: topKeyword,
                    positive: 0,
                    negative: 0,
                    neutral: 0,
                    avgScore: 0,
                    totalMentions: 0,
                };
                for (const row of topicSentiment) {
                    topTrendSentiment[row.sentiment as 'positive' | 'negative' | 'neutral'] = Number(row.count);
                    topTrendSentiment.totalMentions += Number(row.count);
                    topTrendSentiment.avgScore += Number(row.avg_score || 0) * Number(row.count);
                }
                if (topTrendSentiment.totalMentions > 0) {
                    topTrendSentiment.avgScore /= topTrendSentiment.totalMentions;
                }
            } catch (err) {
                // Non-critical — fall back to null
                console.warn("Failed to compute per-topic sentiment:", err);
            }
        }

        // Content Gap Score: ratio of trending keywords that have fewer
        // than 10 matching content items (= underserved topics)
        let contentGapScore = 0;
        if (topTrends.length > 0) {
            let underserved = 0;
            for (const trend of topTrends) {
                const matchCount = await prisma.contentItem.count({
                    where: {
                        OR: [
                            { title: { contains: trend.keyword, mode: "insensitive" } },
                            { body: { contains: trend.keyword, mode: "insensitive" } },
                        ],
                    },
                });
                if (matchCount < 10) underserved++;
            }
            contentGapScore = Math.round((underserved / topTrends.length) * 100);
        }

        res.json({
            totalContent: contentCount,
            trendCount,
            emergingTrends: emergingTrendsCount,
            viralSignals: viralSignalsCount,
            avgSentiment,
            activePlatforms,
            lastIngestion,
            sentimentCounts,
            platformCounts,
            topTrendSentiment,
            contentGapScore,
        });
    } catch (err: any) {
        console.error("Failed to fetch KPIs:", err);
        res.status(500).json({ error: "Failed to fetch KPIs", details: err.message });
    }
});

// GET /api/dashboard/alerts — Recent alerts/notifications (Viral trends)
dashboardRouter.get("/alerts", async (_req: Request, res: Response) => {
    try {
        // Fetch viral or emerging trends from the last 24 hours as alerts
        const alerts = await prisma.trendSignal.findMany({
            where: {
                direction: { in: ["viral", "emerging"] },
                detectedAt: { gte: new Date(Date.now() - 24 * 60 * 60 * 1000) },
            },
            take: 5,
            orderBy: { momentum7d: "desc" },
            select: {
                id: true,
                keyword: true,
                direction: true,
                platform: true,
                detectedAt: true,
            },
        });

        res.json({ alerts });
    } catch (err: any) {
        console.error("Failed to fetch alerts:", err);
        res.status(500).json({ error: "Failed to fetch alerts", details: err.message });
    }
});

// GET /api/dashboard/history — 7-day volume history by platform
dashboardRouter.get("/history", async (_req: Request, res: Response) => {
    try {
        const days = 7;
        const result = await prisma.$queryRaw`
            SELECT 
                DATE_TRUNC('day', fetched_at) as date, 
                platform,
                COUNT(*) as count
            FROM content_items
            WHERE fetched_at >= NOW() - (${days} || ' days')::INTERVAL
            GROUP BY 1, 2
            ORDER BY 1 ASC
        `;

        // Process into format expected by Recharts: [{ date: 'Mon', reddit: 10, twitter: 5 }, ...]
        const map = new Map<string, any>();

        (result as any[]).forEach((row: any) => {
            const dateKey = new Date(row.date).toLocaleDateString("en-US", { weekday: "short" }); // "Mon", "Tue"

            if (!map.has(dateKey)) {
                map.set(dateKey, { day: dateKey, reddit: 0, twitter: 0, youtube: 0 });
            }

            const entry = map.get(dateKey);
            const platform = row.platform.toLowerCase();
            if (platform === "reddit") entry.reddit = Number(row.count);
            else if (platform === "twitter" || platform === "x") entry.twitter = Number(row.count);
            else if (platform === "youtube") entry.youtube = Number(row.count);
        });

        const timeline = Array.from(map.values());
        res.json({ timeline });
    } catch (err: any) {
        console.error("Failed to fetch history:", err);
        res.status(500).json({ error: "Failed to fetch history", details: err.message });
    }
});
