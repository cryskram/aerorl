"use client";

import { motion } from "framer-motion";

import type { HealthResponse, MetricsResponse } from "@/types";

interface MetricsPanelProps {
  metrics: MetricsResponse | null;
  health: HealthResponse | null;
  currentStep: number;
  totalReward: number;
  reachedGoal: boolean;
  error: string | null;
}

export default function MetricsPanel({
  metrics,
  health,
  currentStep,
  totalReward,
  reachedGoal,
  error,
}: MetricsPanelProps) {
  const online = health?.status === "healthy";

  return (
    <div className="rounded-3xl border border-cyan-500/20 bg-[#020814]/95 p-6 shadow-2xl shadow-cyan-500/10 backdrop-blur-xl">
      <div className="mb-6 flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
        <div>
          <p className="text-sm font-medium text-cyan-100">Backend Status</p>

          <p className="text-xs text-white/50">
            {online ? "Connected" : "Offline"}
          </p>
        </div>

        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.7, 1, 0.7],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
          }}
          className={`h-3 w-3 rounded-full ${
            online ? "bg-green-400" : "bg-red-400"
          }`}
        />
      </div>

      <div className="mb-6">
        <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-cyan-300">
          Current Episode
        </h3>

        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-xl bg-white/5 px-3 py-2">
            <span className="text-sm text-white/60">Step Count</span>

            <span className="font-medium text-cyan-100">{currentStep}</span>
          </div>

          <div className="flex items-center justify-between rounded-xl bg-white/5 px-3 py-2">
            <span className="text-sm text-white/60">Reward</span>

            <span
              className={`font-medium ${
                totalReward >= 0 ? "text-green-400" : "text-red-400"
              }`}
            >
              {totalReward.toFixed(2)}
            </span>
          </div>

          <div className="flex items-center justify-between rounded-xl bg-white/5 px-3 py-2">
            <span className="text-sm text-white/60">Outcome</span>

            <span
              className={`font-medium ${
                reachedGoal ? "text-green-400" : "text-yellow-300"
              }`}
            >
              {reachedGoal ? "Goal Reached" : "In Progress"}
            </span>
          </div>
        </div>
      </div>

      <div>
        <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-cyan-300">
          Lifetime Stats
        </h3>

        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-xl bg-white/5 px-3 py-2">
            <span className="text-sm text-white/60">Simulations</span>

            <span className="font-medium text-cyan-100">
              {metrics?.total_simulations ?? 0}
            </span>
          </div>

          <div className="flex items-center justify-between rounded-xl bg-white/5 px-3 py-2">
            <span className="text-sm text-white/60">Success Rate</span>

            <span className="font-medium text-cyan-100">
              {metrics?.success_rate ?? 0}%
            </span>
          </div>

          <div className="flex items-center justify-between rounded-xl bg-white/5 px-3 py-2">
            <span className="text-sm text-white/60">Predictions</span>

            <span className="font-medium text-cyan-100">
              {metrics?.total_predictions ?? 0}
            </span>
          </div>

          <div className="flex items-center justify-between rounded-xl bg-white/5 px-3 py-2">
            <span className="text-sm text-white/60">Uptime</span>

            <span className="font-medium text-cyan-100">
              {online ? "Online" : "Offline"}
            </span>
          </div>
        </div>
      </div>

      {error && (
        <div className="mt-6 rounded-2xl border border-red-500/30 bg-red-500/10 p-4">
          <p className="text-sm font-medium text-red-300">Error</p>

          <p className="mt-1 text-xs text-red-200/80">{error}</p>
        </div>
      )}
    </div>
  );
}
