import { Redis } from "@upstash/redis";

export const redis = new Redis({
    url: process.env.UPSTASH_REDIS_REST_URL!,
    token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

/**
 * Cache helper — get or set with TTL.
 */
export async function cached<T>(
    key: string,
    ttlSeconds: number,
    fetcher: () => Promise<T>
): Promise<T> {
    const existing = await redis.get<T>(key);
    if (existing !== null && existing !== undefined) {
        return existing;
    }
    const fresh = await fetcher();
    await redis.set(key, JSON.stringify(fresh), { ex: ttlSeconds });
    return fresh;
}
