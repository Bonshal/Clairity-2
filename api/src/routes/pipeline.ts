import { Router, Request, Response } from "express";

export const pipelineRouter = Router();

// POST /api/pipeline/trigger — Manually trigger full pipeline
pipelineRouter.post("/trigger", async (_req: Request, res: Response) => {
    try {
        // TODO: Push full-pipeline job to BullMQ
        const runId = `run_${Date.now()}`;
        res.json({ status: "queued", runId });
    } catch (err) {
        res.status(500).json({ error: "Failed to trigger pipeline" });
    }
});

// GET /api/pipeline/status/:id — Pipeline run status
pipelineRouter.get("/status/:id", async (req: Request, res: Response) => {
    const { id } = req.params;
    try {
        // TODO: Query analysis_runs table in Neon
        res.json({ runId: id, status: "unknown" });
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch pipeline status" });
    }
});

// GET /api/pipeline/history — Past run history
pipelineRouter.get("/history", async (req: Request, res: Response) => {
    const limit = parseInt(req.query.limit as string) || 20;
    try {
        res.json({ runs: [], limit });
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch pipeline history" });
    }
});
