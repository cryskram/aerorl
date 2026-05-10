import axios from "axios";

import type {
  EnvState,
  HealthResponse,
  MetricsResponse,
  SimulateResponse,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws/simulate";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

export const apiClient = {
  async health(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>("/health");

    return response.data;
  },

  async metrics(): Promise<MetricsResponse> {
    const response = await api.get<MetricsResponse>("/metrics");

    return response.data;
  },

  async envState(): Promise<EnvState> {
    const response = await api.get<EnvState>("/env/state");

    return response.data;
  },

  async envReset(seed?: number): Promise<{
    observation: number[];
    state: EnvState;
  }> {
    const response = await api.post("/env/reset", {
      seed,
    });

    return response.data;
  },

  async simulate(
    seed?: number,
    maxSteps: number = 100,
  ): Promise<SimulateResponse> {
    const response = await api.post<SimulateResponse>("/simulate", {
      seed,
      max_steps: maxSteps,
    });

    return response.data;
  },

  async predict(
    x: number,
    y: number,
  ): Promise<{
    action: number;
    action_name: string;
    observation: number[];
  }> {
    const response = await api.get(`/predict?x=${x}&y=${y}`);

    return response.data;
  },
};

export default api;
