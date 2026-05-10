from __future__ import annotations

import math
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class DroneEnv(gym.Env):

    metadata = {"render_modes": ["ansi"]}

    ACTIONS = {
        0: (-1, 0),  # UP
        1: (1, 0),  # DOWN
        2: (0, -1),  # LEFT
        3: (0, 1),  # RIGHT
    }

    ACTION_NAMES = {
        0: "UP",
        1: "DOWN",
        2: "LEFT",
        3: "RIGHT",
    }

    def __init__(
        self,
        grid_size: int = 10,
        obstacle_count: int = 10,
        max_steps: int = 200,
        render_mode: str | None = "ansi",
    ) -> None:
        super().__init__()

        self.grid_size = grid_size
        self.obstacle_count = obstacle_count
        self.max_steps = max_steps
        self.render_mode = render_mode

        self.action_space = spaces.Discrete(4)

        obs_low = np.array(
            [0, 0, 0, 0, -grid_size, -grid_size, 0, 0],
            dtype=np.float32,
        )

        obs_high = np.array(
            [
                grid_size - 1,
                grid_size - 1,
                grid_size - 1,
                grid_size - 1,
                grid_size,
                grid_size,
                np.sqrt(2 * (grid_size**2)),
                np.sqrt(2 * (grid_size**2)),
            ],
            dtype=np.float32,
        )

        self.observation_space = spaces.Box(
            low=obs_low,
            high=obs_high,
            dtype=np.float32,
        )

        self.drone_pos = np.array([0, 0], dtype=np.int32)
        self.goal_pos = np.array(
            [grid_size - 1, grid_size - 1],
            dtype=np.int32,
        )

        self.obstacles: list[tuple[int, int]] = []
        self.current_step = 0
        self.previous_distance = 0.0

    def _generate_obstacles(self) -> list[tuple[int, int]]:

        forbidden_positions = {
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
            (self.grid_size - 1, self.grid_size - 1),
            (self.grid_size - 2, self.grid_size - 1),
            (self.grid_size - 1, self.grid_size - 2),
            (self.grid_size - 2, self.grid_size - 2),
        }

        obstacles = set()

        while len(obstacles) < self.obstacle_count:
            x = self.np_random.integers(0, self.grid_size)
            y = self.np_random.integers(0, self.grid_size)

            position = (int(x), int(y))

            if position not in forbidden_positions:
                obstacles.add(position)

        return list(obstacles)

    def _distance_to_goal(self) -> float:

        return float(np.linalg.norm(self.goal_pos - self.drone_pos))

    def _min_obstacle_distance(self) -> float:

        if not self.obstacles:
            return float(self.grid_size)

        distances = [math.dist(self.drone_pos, obstacle) for obstacle in self.obstacles]

        return float(min(distances))

    def _get_obs(self) -> np.ndarray:

        relative = self.goal_pos - self.drone_pos

        observation = np.array(
            [
                self.drone_pos[0],
                self.drone_pos[1],
                self.goal_pos[0],
                self.goal_pos[1],
                relative[0],
                relative[1],
                self._distance_to_goal(),
                self._min_obstacle_distance(),
            ],
            dtype=np.float32,
        )

        return observation

    def _get_info(self) -> dict[str, Any]:

        return {
            "current_step": self.current_step,
            "distance_to_goal": self._distance_to_goal(),
            "min_obstacle_distance": self._min_obstacle_distance(),
        }

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:

        super().reset(seed=seed)

        self.drone_pos = np.array([0, 0], dtype=np.int32)

        self.goal_pos = np.array(
            [self.grid_size - 1, self.grid_size - 1],
            dtype=np.int32,
        )

        self.obstacles = self._generate_obstacles()

        self.current_step = 0
        self.previous_distance = self._distance_to_goal()

        observation = self._get_obs()
        info = self._get_info()

        return observation, info

    def step(
        self,
        action: int,
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:

        self.current_step += 1

        move = self.ACTIONS[action]

        new_position = self.drone_pos + np.array(move)

        new_position[0] = np.clip(
            new_position[0],
            0,
            self.grid_size - 1,
        )

        new_position[1] = np.clip(
            new_position[1],
            0,
            self.grid_size - 1,
        )

        self.drone_pos = new_position

        terminated = False
        truncated = False

        current_distance = self._distance_to_goal()

        reward = -0.5

        distance_shaping = (self.previous_distance - current_distance) * 2

        reward += distance_shaping

        min_obstacle_distance = self._min_obstacle_distance()

        if min_obstacle_distance < 1.5:
            reward -= 2

        drone_tuple = tuple(self.drone_pos.tolist())

        if drone_tuple in self.obstacles:
            reward = -100
            terminated = True

        elif np.array_equal(self.drone_pos, self.goal_pos):
            reward = 100
            terminated = True

        if self.current_step >= self.max_steps:
            truncated = True

        self.previous_distance = current_distance

        observation = self._get_obs()
        info = self._get_info()

        return (
            observation,
            float(reward),
            terminated,
            truncated,
            info,
        )

    def render(self) -> str:

        grid = [["." for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        for obstacle in self.obstacles:
            grid[obstacle[0]][obstacle[1]] = "X"

        grid[self.goal_pos[0]][self.goal_pos[1]] = "G"

        grid[self.drone_pos[0]][self.drone_pos[1]] = "D"

        rendered = "\n".join([" ".join(row) for row in grid])

        if self.render_mode == "ansi":
            return rendered

        print(rendered)
        return rendered

    def get_state_dict(self) -> dict[str, Any]:

        return {
            "grid_size": self.grid_size,
            "obstacle_count": self.obstacle_count,
            "max_steps": self.max_steps,
            "drone_pos": self.drone_pos.tolist(),
            "goal_pos": self.goal_pos.tolist(),
            "obstacles": [list(obs) for obs in self.obstacles],
            "current_step": self.current_step,
        }

    def set_state(self, state: dict[str, Any]) -> None:

        self.grid_size = state["grid_size"]
        self.obstacle_count = state["obstacle_count"]
        self.max_steps = state["max_steps"]

        self.drone_pos = np.array(
            state["drone_pos"],
            dtype=np.int32,
        )

        self.goal_pos = np.array(
            state["goal_pos"],
            dtype=np.int32,
        )

        self.obstacles = [tuple(obstacle) for obstacle in state["obstacles"]]

        self.current_step = state["current_step"]

        self.previous_distance = self._distance_to_goal()
