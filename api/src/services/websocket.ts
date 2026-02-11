import { Server as HttpServer } from "http";
import { Server, Socket } from "socket.io";

let io: Server | null = null;

/**
 * Initialize Socket.io WebSocket server.
 * Attaches to the existing Express HTTP server.
 */
export function initWebSocket(httpServer: HttpServer): Server {
    io = new Server(httpServer, {
        cors: {
            origin: process.env.CORS_ORIGIN || "http://localhost:3000",
            methods: ["GET", "POST"],
        },
        transports: ["websocket", "polling"],
        pingInterval: 25000,
        pingTimeout: 20000,
    });

    io.on("connection", (socket: Socket) => {
        console.log(`[WS] Client connected: ${socket.id}`);

        // Join niche-specific rooms
        socket.on("subscribe:niche", (nicheId: string) => {
            socket.join(`niche:${nicheId}`);
            console.log(`[WS] ${socket.id} joined niche:${nicheId}`);
        });

        socket.on("unsubscribe:niche", (nicheId: string) => {
            socket.leave(`niche:${nicheId}`);
        });

        // Join pipeline room for real-time updates
        socket.on("subscribe:pipeline", (runId: string) => {
            socket.join(`pipeline:${runId}`);
            console.log(`[WS] ${socket.id} joined pipeline:${runId}`);
        });

        socket.on("disconnect", (reason) => {
            console.log(`[WS] Client disconnected: ${socket.id} (${reason})`);
        });
    });

    console.log("[WS] WebSocket server initialized");
    return io;
}

/**
 * Get the active Socket.io instance.
 */
export function getIO(): Server {
    if (!io) throw new Error("WebSocket server not initialized");
    return io;
}

// ─── Event Emitters ─────────────────────────────────────────

/** Broadcast a new viral/emerging trend alert */
export function emitTrendAlert(alert: {
    keyword: string;
    direction: string;
    momentum: number;
    platform: string;
}) {
    io?.emit("alert:trend", {
        type: "trend",
        ...alert,
        timestamp: new Date().toISOString(),
    });
}

/** Broadcast pipeline status update */
export function emitPipelineUpdate(
    runId: string,
    update: {
        agent: string;
        status: "started" | "completed" | "failed";
        duration?: number;
        message?: string;
    }
) {
    io?.to(`pipeline:${runId}`).emit("pipeline:update", {
        runId,
        ...update,
        timestamp: new Date().toISOString(),
    });
}

/** Broadcast pipeline completion */
export function emitPipelineComplete(
    runId: string,
    summary: {
        itemsProcessed: number;
        trendsDetected: number;
        recommendationsGenerated: number;
        evaluationScore: number;
        duration: string;
    }
) {
    io?.emit("pipeline:complete", {
        runId,
        ...summary,
        timestamp: new Date().toISOString(),
    });
}

/** Broadcast anomaly detection alert */
export function emitAnomalyAlert(alert: {
    contentId: string;
    title: string;
    platform: string;
    metric: string;
    score: number;
}) {
    io?.emit("alert:anomaly", {
        type: "anomaly",
        ...alert,
        timestamp: new Date().toISOString(),
    });
}

/** Broadcast new recommendation generated */
export function emitNewRecommendation(rec: {
    id: string;
    title: string;
    format: string;
    seoScore: number;
    geoScore: number;
}) {
    io?.emit("recommendation:new", {
        ...rec,
        timestamp: new Date().toISOString(),
    });
}
