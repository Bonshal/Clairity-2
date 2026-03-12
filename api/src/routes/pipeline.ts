import { Router, Request, Response } from "express";

export const pipelineRouter = Router();

const ANALYSIS_SERVICE_URL = process.env.ANALYSIS_SERVICE_URL || "http://127.0.0.1:8000";

// POST /api/pipeline/trigger — Manually trigger full pipeline
pipelineRouter.post("/trigger", async (req: Request, res: Response) => {
    try {
        const { niche_id, platforms } = req.body;

        const response = await fetch(`${ANALYSIS_SERVICE_URL}/pipeline/run`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ niche_id, platforms }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Analysis service error: ${response.status} ${errorText}`);
        }

        const data = await response.json() as { run_id: string };
        res.json({ status: "queued", runId: data.run_id });
    } catch (err: unknown) {
        console.error("Pipeline trigger failed:", err);
        res.status(500).json({ error: "Failed to trigger pipeline", details: err instanceof Error ? err.message : String(err) });
    }
});

// GET /api/pipeline/status/:id — Pipeline run status
pipelineRouter.get("/status/:id", async (req: Request, res: Response) => {
    const { id } = req.params;
    try {
        const response = await fetch(`${ANALYSIS_SERVICE_URL}/pipeline/status/${id}`);

        if (!response.ok) {
            if (response.status === 404) {
                res.status(404).json({ error: "Run not found" });
                return;
            }
            throw new Error(`Analysis status fetch failed: ${response.status}`);
        }

        const data = await response.json() as unknown;
        res.json(data);
    } catch (err: unknown) {
        console.error("Pipeline status fetch failed:", err);
        res.status(500).json({ error: "Failed to fetch pipeline status", details: err instanceof Error ? err.message : String(err) });
    }
});

// GET /api/pipeline/history — Past run history
// GET /api/pipeline/history — Past run history
pipelineRouter.get("/history", async (req: Request, res: Response) => {
    try {
        const query = new URLSearchParams(req.query as Record<string, string>).toString();
        const response = await fetch(`${ANALYSIS_SERVICE_URL}/pipeline/history?${query}`);

        if (!response.ok) {
            throw new Error(`Analysis history fetch failed: ${response.status}`);
        }

        const data = await response.json();
        res.json(data);
    } catch (err: unknown) {
        console.error(`Pipeline history fetch failed from ${ANALYSIS_SERVICE_URL}:`, err instanceof Error ? err.message : String(err));
        res.status(500).json({ runs: [] });

    }
});
