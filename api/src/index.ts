import express from "express";
import cors from "cors";
import helmet from "helmet";
import { createServer } from "http";
import dotenv from "dotenv";

import { dashboardRouter } from "./routes/dashboard";
import { trendsRouter } from "./routes/trends";
import { recommendationsRouter } from "./routes/recommendations";
import { seoRouter } from "./routes/seo";
import { geoRouter } from "./routes/geo";
import { contentRouter } from "./routes/content";
import { nichesRouter } from "./routes/niches";
import { pipelineRouter } from "./routes/pipeline";
import { initWebSocket, getIO } from "./services/websocket";

dotenv.config();

const app = express();
const httpServer = createServer(app);

// ─── WebSocket ────────────────────────────────────────────
const io = initWebSocket(httpServer);
app.set("io", io);

// ─── Middleware ────────────────────────────────────────────
app.use(helmet());
app.use(
    cors({
        origin: process.env.CORS_ORIGIN || "http://localhost:3000",
        credentials: true,
    })
);
app.use(express.json({ limit: "10mb" }));

// ─── Health Check ─────────────────────────────────────────
app.get("/api/health", (_req, res) => {
    res.json({
        status: "ok",
        service: "market-research-api",
        timestamp: new Date().toISOString(),
        ws: io.engine?.clientsCount ?? 0,
    });
});

// ─── Routes ───────────────────────────────────────────────
app.use("/api/dashboard", dashboardRouter);
app.use("/api/trends", trendsRouter);
app.use("/api/recommendations", recommendationsRouter);
app.use("/api/seo", seoRouter);
app.use("/api/geo", geoRouter);
app.use("/api/content", contentRouter);
app.use("/api/niches", nichesRouter);
app.use("/api/pipeline", pipelineRouter);

// ─── Global Error Handler ─────────────────────────────────
app.use(
    (
        err: Error,
        _req: express.Request,
        res: express.Response,
        _next: express.NextFunction
    ) => {
        console.error("[API Error]", err.message);
        res.status(500).json({
            error: "Internal server error",
            message:
                process.env.NODE_ENV === "development" ? err.message : undefined,
        });
    }
);

// ─── Start Server ─────────────────────────────────────────
const PORT = parseInt(process.env.API_PORT || "3001", 10);

httpServer.listen(PORT, () => {
    console.log(`🚀 Market Research API running on port ${PORT}`);
    console.log(`📡 WebSocket server ready`);
    console.log(`🔗 Health: http://localhost:${PORT}/api/health`);
});

export { app, io, httpServer };
