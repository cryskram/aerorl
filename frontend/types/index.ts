export interface EnvState {
  grid_size: number;
  obstacle_count: number;
  max_steps: number;
  drone_pos: [number, number];
  goal_pos: [number, number];
  obstacles: [number, number][];
  current_step: number;
}

export interface SimulateResponse {
  total_reward: number;
  steps: number;
  reached_goal: boolean;
  final_state: EnvState;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  model_loaded_at: string | null;
}

export interface MetricsResponse {
  total_predictions: number;
  total_simulations: number;
  total_goal_reached: number;
  success_rate: number;
}

export interface SimulationConfig {
  seed?: number;
  grid_size: number;
  obstacle_count: number;
  delay_ms: number;
}

export type CellType = "empty" | "drone" | "goal" | "obstacle" | "path";

export interface WSInitMessage {
  type: "init";
  state: EnvState;
}

export interface WSStepMessage {
  type: "step";
  state: EnvState;
  action: number;
  action_name: string;
  reward: number;
  total_reward: number;
  done: boolean;
  reached_goal: boolean;
}

export interface WSDoneMessage {
  type: "done";
  state: EnvState;
  total_reward: number;
  reached_goal: boolean;
}

export interface WSErrorMessage {
  type: "error";
  message: string;
}

export type WSMessage =
  | WSInitMessage
  | WSStepMessage
  | WSDoneMessage
  | WSErrorMessage;
