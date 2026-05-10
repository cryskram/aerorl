"use client";

import { motion } from "framer-motion";

import type { EnvState } from "@/types";

interface DroneGridProps {
  envState: EnvState;
  path: [number, number][];
  animating: boolean;
}

function positionKey(row: number, col: number): string {
  return `${row}-${col}`;
}

export default function DroneGrid({
  envState,
  path,
  animating,
}: DroneGridProps) {
  const { grid_size, drone_pos, goal_pos, obstacles } = envState;

  const obstacleSet = new Set(obstacles.map(([r, c]) => positionKey(r, c)));

  const pathSet = new Set(path.map(([r, c]) => positionKey(r, c)));

  return (
    <div className="relative overflow-hidden rounded-3xl border border-cyan-500/20 bg-[#020814] p-6 shadow-2xl shadow-cyan-500/10">
      <div className="pointer-events-none absolute inset-0 opacity-10">
        <div
          className="h-full w-full"
          style={{
            backgroundImage:
              "repeating-linear-gradient(to bottom, transparent 0px, rgba(255,255,255,0.04) 1px, transparent 2px, transparent 6px)",
          }}
        />
      </div>

      <div
        className="grid gap-1 rounded-2xl border border-cyan-500/10 bg-black/30 p-3"
        style={{
          gridTemplateColumns: `repeat(${grid_size}, minmax(0, 1fr))`,
        }}
      >
        {Array.from({
          length: grid_size,
        }).map((_, row) =>
          Array.from({
            length: grid_size,
          }).map((_, col) => {
            const key = positionKey(row, col);

            const isDrone = drone_pos[0] === row && drone_pos[1] === col;

            const isGoal = goal_pos[0] === row && goal_pos[1] === col;

            const isObstacle = obstacleSet.has(key);

            const isPath = pathSet.has(key);

            return (
              <div
                key={key}
                className="relative flex aspect-square items-center justify-center overflow-hidden rounded-md border border-white/5 bg-[#07111f]"
              >
                {!isDrone && !isGoal && !isObstacle && !isPath && (
                  <div className="h-full w-full bg-transparent" />
                )}

                {isPath && !isDrone && !isGoal && (
                  <div className="h-2 w-2 rounded-full bg-cyan-400/80 shadow-lg shadow-cyan-400/50" />
                )}

                {isObstacle && (
                  <div className="h-full w-full bg-red-950 shadow-inner shadow-red-500/30" />
                )}

                {isGoal && (
                  <motion.div
                    animate={{
                      scale: [1, 1.08, 1],
                    }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                    }}
                    className="absolute flex h-5 w-5 items-center justify-center rounded-full border-2 border-green-400 shadow-lg shadow-green-500/50"
                  >
                    <div className="h-2 w-2 rounded-full bg-green-400" />
                  </motion.div>
                )}

                {isDrone && (
                  <motion.div
                    animate={
                      animating
                        ? {
                            scale: [1, 1.1, 1],
                            boxShadow: [
                              "0 0 10px rgba(34,211,238,0.4)",
                              "0 0 20px rgba(34,211,238,0.9)",
                              "0 0 10px rgba(34,211,238,0.4)",
                            ],
                          }
                        : {}
                    }
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                    }}
                    className="relative z-10 flex h-8 w-8 items-center justify-center rounded-lg border border-cyan-300 bg-cyan-400/20 backdrop-blur-sm"
                  >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <circle cx="5" cy="5" r="2" fill="#22d3ee" />
                      <circle cx="19" cy="5" r="2" fill="#22d3ee" />
                      <circle cx="5" cy="19" r="2" fill="#22d3ee" />
                      <circle cx="19" cy="19" r="2" fill="#22d3ee" />

                      <line
                        x1="7"
                        y1="7"
                        x2="10"
                        y2="10"
                        stroke="#67e8f9"
                        strokeWidth="1.5"
                      />
                      <line
                        x1="17"
                        y1="7"
                        x2="14"
                        y2="10"
                        stroke="#67e8f9"
                        strokeWidth="1.5"
                      />
                      <line
                        x1="7"
                        y1="17"
                        x2="10"
                        y2="14"
                        stroke="#67e8f9"
                        strokeWidth="1.5"
                      />
                      <line
                        x1="17"
                        y1="17"
                        x2="14"
                        y2="14"
                        stroke="#67e8f9"
                        strokeWidth="1.5"
                      />

                      <rect
                        x="9"
                        y="9"
                        width="6"
                        height="6"
                        rx="1.5"
                        fill="#22d3ee"
                      />
                    </svg>
                  </motion.div>
                )}
              </div>
            );
          }),
        )}
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-4 text-xs text-cyan-100/70">
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded bg-cyan-400" />
          Drone
        </div>

        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded bg-green-400" />
          Goal
        </div>

        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded bg-red-900" />
          Obstacle
        </div>

        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-cyan-300" />
          Path
        </div>
      </div>
    </div>
  );
}
