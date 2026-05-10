"use client";

import { Play, RotateCcw, Square } from "lucide-react";

import type { SimulationStatus } from "@/hooks/useSimulation";
import type { SimulationConfig } from "@/types";

interface SimulationControlsProps {
  config: SimulationConfig;
  setConfig: (config: SimulationConfig) => void;
  status: SimulationStatus;
  onRun: () => void;
  onStop: () => void;
  onReset: () => void;
}

const statusColors: Record<SimulationStatus, string> = {
  idle: "bg-zinc-500",
  connecting: "bg-yellow-400",
  running: "bg-cyan-400",
  done: "bg-green-400",
  error: "bg-red-400",
};

export default function SimulationControls({
  config,
  setConfig,
  status,
  onRun,
  onStop,
  onReset,
}: SimulationControlsProps) {
  return (
    <div className="rounded-3xl border border-cyan-500/20 bg-[#020814]/95 p-6 shadow-2xl shadow-cyan-500/10 backdrop-blur-xl">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-cyan-100">
          Simulation Controls
        </h2>

        <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/70">
          <div className={`h-2 w-2 rounded-full ${statusColors[status]}`} />

          {status.toUpperCase()}
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <div className="mb-2 flex items-center justify-between">
            <label className="text-sm text-cyan-100/80">Grid Size</label>

            <span className="text-sm text-cyan-300">{config.grid_size}</span>
          </div>

          <input
            type="range"
            min={5}
            max={15}
            value={config.grid_size}
            onChange={(e) =>
              setConfig({
                ...config,
                grid_size: Number(e.target.value),
              })
            }
            className="w-full"
          />
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <label className="text-sm text-cyan-100/80">Obstacle Count</label>

            <span className="text-sm text-cyan-300">
              {config.obstacle_count}
            </span>
          </div>

          <input
            type="range"
            min={0}
            max={15}
            value={config.obstacle_count}
            onChange={(e) =>
              setConfig({
                ...config,
                obstacle_count: Number(e.target.value),
              })
            }
            className="w-full"
          />
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <label className="text-sm text-cyan-100/80">Delay (ms)</label>

            <span className="text-sm text-cyan-300">{config.delay_ms}</span>
          </div>

          <input
            type="range"
            min={50}
            max={600}
            step={10}
            value={config.delay_ms}
            onChange={(e) =>
              setConfig({
                ...config,
                delay_ms: Number(e.target.value),
              })
            }
            className="w-full"
          />
        </div>

        <div className="flex items-center gap-3 pt-4">
          {status !== "running" ? (
            <button
              onClick={onRun}
              className="flex flex-1 items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-cyan-500 to-cyan-400 px-4 py-3 font-medium text-black transition-all duration-200 hover:scale-[1.02] hover:shadow-lg hover:shadow-cyan-500/40"
            >
              <Play className="h-4 w-4" />
              Run Simulation
            </button>
          ) : (
            <button
              onClick={onStop}
              className="flex flex-1 items-center justify-center gap-2 rounded-2xl border border-red-500/50 bg-red-500/10 px-4 py-3 font-medium text-red-300 transition-all duration-200 hover:bg-red-500/20"
            >
              <Square className="h-4 w-4" />
              Stop
            </button>
          )}

          <button
            onClick={onReset}
            className="rounded-2xl border border-white/10 bg-white/5 p-3 text-cyan-100 transition-all duration-200 hover:bg-white/10"
          >
            <RotateCcw className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
