"use client";

import { Activity, Cpu, ExternalLink } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import DroneGrid from "@/components/drone/DroneGrid";
import MetricsPanel from "@/components/drone/MetricsPanel";
import SimulationControls from "@/components/drone/SimulationControls";
import { useMetrics } from "@/hooks/useMetrics";
import { useSimulation } from "@/hooks/useSimulation";
import type { SimulationConfig } from "@/types";

export default function HomePage() {
  const { sim, start, stop, reset } = useSimulation();

  const { metrics, health, error: metricsError } = useMetrics();

  const [config, setConfig] = useState<SimulationConfig>({
    grid_size: 10,
    obstacle_count: 8,
    delay_ms: 200,
  });

  // Toasts
  useEffect(() => {
    if (sim.status === "done" && sim.reachedGoal) {
      toast.success("Drone successfully reached the goal.");
    }

    if (sim.status === "done" && !sim.reachedGoal) {
      toast.error("Simulation ended without reaching the goal.");
    }
  }, [sim.status, sim.reachedGoal]);

  return (
    <main className="relative min-h-screen overflow-hidden px-6 py-6 text-white">
      {/* Background Glows */}
      <div className="pointer-events-none absolute left-[-200px] top-[-200px] h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-3xl" />

      <div className="pointer-events-none absolute bottom-[-250px] right-[-250px] h-[500px] w-[500px] rounded-full bg-purple-500/10 blur-3xl" />

      {/* Header */}
      <header className="mb-6 flex flex-col gap-4 rounded-3xl border border-cyan-500/15 bg-[#07111f]/80 p-6 shadow-2xl shadow-cyan-500/5 backdrop-blur-xl lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/10">
            <Cpu className="h-7 w-7 text-cyan-300" />
          </div>

          <div>
            <h1 className="text-3xl font-bold tracking-tight text-cyan-100">
              AeroRL
            </h1>

            <p className="mt-1 text-sm text-cyan-100/60">
              Autonomous Drone Path Finder
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4">
          <a
            href="http://localhost:5000"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-4 py-2 text-sm text-cyan-200 transition-all duration-200 hover:bg-cyan-500/20"
          >
            MLflow UI
            <ExternalLink className="h-4 w-4" />
          </a>

          <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/70">
            <Activity className="h-4 w-4 text-cyan-300" />
            <div
              className={`h-2 w-2 rounded-full ${
                health?.status === "healthy" ? "bg-green-400" : "bg-red-400"
              }`}
            />
            Backend
          </div>
        </div>
      </header>

      {/* Layout */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[340px_1fr_320px]">
        {/* Left Sidebar */}
        <div className="space-y-6">
          <SimulationControls
            config={config}
            setConfig={setConfig}
            status={sim.status}
            onRun={() => start(config)}
            onStop={stop}
            onReset={reset}
          />

          <MetricsPanel
            metrics={metrics}
            health={health}
            currentStep={sim.currentStep}
            totalReward={sim.totalReward}
            reachedGoal={sim.reachedGoal}
            error={sim.error ?? metricsError}
          />
        </div>

        {/* Center */}
        <div className="flex min-h-[700px] items-center justify-center">
          <AnimatePresence mode="wait">
            {sim.envState ? (
              <motion.div
                key="grid"
                initial={{
                  opacity: 0,
                  scale: 0.96,
                }}
                animate={{
                  opacity: 1,
                  scale: 1,
                }}
                exit={{
                  opacity: 0,
                  scale: 0.96,
                }}
                transition={{
                  duration: 0.3,
                }}
                className="w-full max-w-4xl"
              >
                <DroneGrid
                  envState={sim.envState}
                  path={sim.path}
                  animating={sim.status === "running"}
                />
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{
                  opacity: 0,
                }}
                animate={{
                  opacity: 1,
                }}
                exit={{
                  opacity: 0,
                }}
                className="flex h-[500px] w-full max-w-3xl flex-col items-center justify-center rounded-3xl border border-dashed border-cyan-500/20 bg-[#07111f]/40 text-center"
              >
                <div className="mb-4 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-5">
                  <Cpu className="h-10 w-10 text-cyan-300" />
                </div>

                <h2 className="text-2xl font-semibold text-cyan-100">
                  Ready for Simulation
                </h2>

                <p className="mt-3 max-w-md text-sm leading-relaxed text-cyan-100/60">
                  Configure the environment parameters and launch the PPO drone
                  agent to visualise autonomous navigation in real-time.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Right Sidebar */}
        <div className="rounded-3xl border border-cyan-500/15 bg-[#07111f]/80 p-6 shadow-2xl shadow-cyan-500/5 backdrop-blur-xl">
          <div className="mb-5 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-cyan-100">Episode Log</h2>

            <span className="rounded-full border border-cyan-500/20 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-200">
              {sim.path.length} steps
            </span>
          </div>

          <div className="h-[700px] overflow-y-auto pr-2">
            <div className="space-y-2">
              {sim.path.length === 0 && (
                <div className="rounded-2xl border border-dashed border-white/10 p-6 text-center text-sm text-white/40">
                  No simulation data yet.
                </div>
              )}

              {sim.path.map(([row, col], index) => (
                <motion.div
                  key={`${row}-${col}-${index}`}
                  initial={{
                    opacity: 0,
                    x: 10,
                  }}
                  animate={{
                    opacity: 1,
                    x: 0,
                  }}
                  transition={{
                    duration: 0.2,
                  }}
                  className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/5 px-4 py-3"
                >
                  <div>
                    <p className="text-sm font-medium text-cyan-100">
                      Step #{index}
                    </p>

                    <p className="mt-1 text-xs text-white/50">Position</p>
                  </div>

                  <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/10 px-3 py-2 text-sm text-cyan-200">
                    [{row}, {col}]
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
