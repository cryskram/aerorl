"use client";

import { useCallback, useRef, useState } from "react";

import { WS_URL } from "@/lib/api";
import type { EnvState, SimulationConfig, WSMessage } from "@/types";

export type SimulationStatus =
  | "idle"
  | "connecting"
  | "running"
  | "done"
  | "error";

export interface SimState {
  status: SimulationStatus;
  envState: EnvState | null;
  path: [number, number][];
  currentStep: number;
  totalReward: number;
  reachedGoal: boolean;
  lastAction: string | null;
  error: string | null;
}

const initialState: SimState = {
  status: "idle",
  envState: null,
  path: [],
  currentStep: 0,
  totalReward: 0,
  reachedGoal: false,
  lastAction: null,
  error: null,
};

export function useSimulation() {
  const [sim, setSim] = useState<SimState>(initialState);

  const socketRef = useRef<WebSocket | null>(null);

  const reset = useCallback(() => {
    setSim(initialState);
  }, []);

  const stop = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }

    setSim((prev) => ({
      ...prev,
      status: "idle",
    }));
  }, []);

  const start = useCallback(
    (config: SimulationConfig) => {
      stop();

      setSim((prev) => ({
        ...prev,
        status: "connecting",
        error: null,
      }));

      const socket = new WebSocket(WS_URL);

      socketRef.current = socket;

      socket.onopen = () => {
        setSim((prev) => ({
          ...prev,
          status: "running",
        }));

        socket.send(JSON.stringify(config));
      };

      socket.onmessage = (event: MessageEvent<string>) => {
        const message: WSMessage = JSON.parse(event.data);

        if (message.type === "error") {
          setSim((prev) => ({
            ...prev,
            status: "error",
            error: message.message,
          }));

          return;
        }

        if (message.type === "init") {
          const dronePos = message.state.drone_pos;

          setSim((prev) => ({
            ...prev,
            envState: message.state,
            path: [dronePos],
            currentStep: 0,
            totalReward: 0,
          }));

          return;
        }

        if (message.type === "step") {
          const dronePos = message.state.drone_pos;

          setSim((prev) => ({
            ...prev,
            envState: message.state,
            path: [...prev.path, dronePos],
            currentStep: message.state.current_step,
            totalReward: message.total_reward,
            reachedGoal: message.reached_goal,
            lastAction: message.action_name,
          }));

          return;
        }

        if (message.type === "done") {
          setSim((prev) => ({
            ...prev,
            status: "done",
            envState: message.state,
            totalReward: message.total_reward,
            reachedGoal: message.reached_goal,
          }));

          socket.close();
        }
      };

      socket.onerror = () => {
        setSim((prev) => ({
          ...prev,
          status: "error",
          error: "WebSocket connection failed",
        }));
      };

      socket.onclose = () => {
        socketRef.current = null;
      };
    },
    [stop],
  );

  return {
    sim,
    start,
    stop,
    reset,
  };
}
