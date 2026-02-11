import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET || "dev-secret-change-me";

export interface AuthRequest extends Request {
    userId?: string;
}

/**
 * JWT authentication middleware.
 * Verifies Bearer token and attaches userId to request.
 */
export function authMiddleware(
    req: AuthRequest,
    res: Response,
    next: NextFunction
): void {
    // Skip auth in development if no token provided
    if (process.env.NODE_ENV === "development") {
        req.userId = "dev-user";
        return next();
    }

    const authHeader = req.headers.authorization;
    if (!authHeader?.startsWith("Bearer ")) {
        res.status(401).json({ error: "Missing or invalid authorization header" });
        return;
    }

    const token = authHeader.split(" ")[1];
    try {
        const decoded = jwt.verify(token, JWT_SECRET) as { userId: string };
        req.userId = decoded.userId;
        next();
    } catch (err) {
        res.status(401).json({ error: "Invalid or expired token" });
    }
}

/**
 * Internal API key auth for Python service → Node.js calls.
 */
export function internalAuthMiddleware(
    req: Request,
    res: Response,
    next: NextFunction
): void {
    const apiKey = req.headers["x-internal-api-key"];
    if (apiKey !== process.env.JWT_SECRET) {
        res.status(403).json({ error: "Forbidden" });
        return;
    }
    next();
}
