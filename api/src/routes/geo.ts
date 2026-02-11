import { Router, Request, Response } from "express";

export const geoRouter = Router();

// GET /api/geo/analysis/:id — GEO analysis for a recommendation
geoRouter.get("/analysis/:id", async (req: Request, res: Response) => {
    const { id } = req.params;
    try {
        res.json({ analysis: null, id });
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch GEO analysis" });
    }
});
