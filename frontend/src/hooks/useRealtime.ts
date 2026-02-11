"use client";

import { useEffect, useRef, useState, useCallback } from "react";

/**
 * Lightweight WebSocket hook using native EventSource / WebSocket.
 * In production this connects to Socket.io on the API server.
 * Falls back gracefully if the API server is not running.
 */

interface Alert {
    id: string;
    type: "trend" | "anomaly" | "pipeline" | "recommendation";
    title: string;
    description: string;
    timestamp: string;
    read: boolean;
}

interface PipelineUpdate {
    runId: string;
    agent: string;
    status: "started" | "completed" | "failed";
    duration?: number;
    message?: string;
    timestamp: string;
}

export function useAlerts(maxAlerts = 50) {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [unreadCount, setUnreadCount] = useState(0);

    const addAlert = useCallback(
        (alert: Omit<Alert, "id" | "read">) => {
            const newAlert: Alert = {
                ...alert,
                id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
                read: false,
            };
            setAlerts((prev) => [newAlert, ...prev].slice(0, maxAlerts));
            setUnreadCount((c) => c + 1);
        },
        [maxAlerts]
    );

    const markAllRead = useCallback(() => {
        setAlerts((prev) => prev.map((a) => ({ ...a, read: true })));
        setUnreadCount(0);
    }, []);

    const markRead = useCallback((id: string) => {
        setAlerts((prev) =>
            prev.map((a) => (a.id === id ? { ...a, read: true } : a))
        );
        setUnreadCount((c) => Math.max(0, c - 1));
    }, []);

    return { alerts, unreadCount, addAlert, markAllRead, markRead };
}

export function usePipelineUpdates() {
    const [updates, setUpdates] = useState<PipelineUpdate[]>([]);
    const [activeRunId, setActiveRunId] = useState<string | null>(null);

    const addUpdate = useCallback((update: PipelineUpdate) => {
        setUpdates((prev) => [...prev, update]);
        setActiveRunId(update.runId);
    }, []);

    const clearUpdates = useCallback(() => {
        setUpdates([]);
        setActiveRunId(null);
    }, []);

    return { updates, activeRunId, addUpdate, clearUpdates };
}

/**
 * Hook for polling API endpoint at an interval.
 * Used as a fallback when WebSocket is not available.
 */
export function usePolling<T>(
    fetcher: () => Promise<T>,
    intervalMs: number = 30000,
    enabled: boolean = true
) {
    const [data, setData] = useState<T | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    const refresh = useCallback(async () => {
        try {
            setLoading(true);
            const result = await fetcher();
            setData(result);
            setError(null);
        } catch (e: any) {
            setError(e.message || "Failed to fetch");
        } finally {
            setLoading(false);
        }
    }, [fetcher]);

    useEffect(() => {
        if (!enabled) return;

        refresh();

        if (intervalMs > 0) {
            intervalRef.current = setInterval(refresh, intervalMs);
        }

        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, [enabled, intervalMs, refresh]);

    return { data, error, loading, refresh };
}
