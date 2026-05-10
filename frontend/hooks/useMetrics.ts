"use client";

import { useCallback, useEffect, useState } from "react";

import { apiClient } from "@/lib/api";
import type { HealthResponse, MetricsResponse } from "@/types";

interface UseMetricsResult {
  metrics: MetricsResponse | null;
  health: HealthResponse | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useMetrics(interval: number = 5000): UseMetricsResult {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);

  const [health, setHealth] = useState<HealthResponse | null>(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);

      const [healthData, metricsData] = await Promise.all([
        apiClient.health(),
        apiClient.metrics(),
      ]);

      setHealth(healthData);
      setMetrics(metricsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();

    const timer = setInterval(fetchData, interval);

    return () => clearInterval(timer);
  }, [fetchData, interval]);

  return {
    metrics,
    health,
    loading,
    error,
    refetch: fetchData,
  };
}
