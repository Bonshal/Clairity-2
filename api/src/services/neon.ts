import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as {
    prisma: PrismaClient | undefined;
};

export const prisma =
    globalForPrisma.prisma ??
    new PrismaClient({
        log:
            process.env.NODE_ENV === "development"
                ? ["warn", "error"]
                : ["error"],
    });

if (process.env.NODE_ENV !== "production") {
    globalForPrisma.prisma = prisma;
}

/**
 * Retry wrapper for Prisma queries that handles Neon cold-start errors.
 * Neon serverless suspends compute after inactivity; first connection
 * after wake-up can fail with P1001 (unreachable) or P2024 (pool timeout).
 */
export async function withRetry<T>(
    fn: () => Promise<T>,
    maxRetries = 3,
    baseDelayMs = 2000,
): Promise<T> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error: unknown) {
            const err = error as { code?: string; message?: string };
            const retryable =
                err?.code === "P1001" ||
                err?.code === "P2024" ||
                err?.message?.includes("Can't reach database server");

            if (retryable && attempt < maxRetries) {
                const delay = baseDelayMs * attempt;
                console.warn(
                    `[Prisma] Neon cold-start retry ${attempt}/${maxRetries}, waiting ${delay}ms...`
                );
                await new Promise((r) => setTimeout(r, delay));
            } else {
                throw error;
            }
        }
    }
    throw new Error("withRetry: unreachable");
}
