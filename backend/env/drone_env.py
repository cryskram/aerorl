from __future__ import annotations

import random
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class DroneEnv(gym.Env):

    metadata = {"render_modes": ["human"]}

    ACTION_NAMES = {
        0: "UP",
        1: "DOWN",
        2: "LEFT",
        3: "RIGHT",
    }

    def __init__(
        self,
        grid_size: int = 10,
        obstacle_count: int = 3,
        max_steps: int = 200,
    ) -> None:
        super().__init__()

        self.grid_size = grid_size
        self.obstacle_count = obstacle_count
        self.max_steps = max_steps

        self.action_space = spaces.Discrete(4)

        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(11,),
            dtype=np.float32,
        )

        self.drone_pos: np.ndarray | None = None
        self.goal_pos: np.ndarray | None = None

        self.obstacles: list[np.ndarray] = []

        self.current_step = 0

        self.previous_distance = 0.0

        self.visited_positions = set()

        self.last_positions: list[tuple[int, int]] = []

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ):
        super().reset(seed=seed)

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.current_step = 0

        self.visited_positions = set()
        self.last_positions = []
        self.drone_pos = np.array(
            [0, 0],
            dtype=np.int32,
        )

        self.goal_pos = np.array(
            [
                self.grid_size - 1,
                self.grid_size - 1,
            ],
            dtype=np.int32,
        )

        self.obstacles = []

        forbidden_positions = {
            tuple(self.drone_pos),
            tuple(self.goal_pos),
        }

        while len(self.obstacles) < self.obstacle_count:
            obstacle = np.array(
                [
                    np.random.randint(
                        0,
                        self.grid_size,
                    ),
                    np.random.randint(
                        0,
                        self.grid_size,
                    ),
                ],
                dtype=np.int32,
            )

            obstacle_tuple = tuple(obstacle)

            if obstacle_tuple not in forbidden_positions:
                self.obstacles.append(obstacle)

                forbidden_positions.add(obstacle_tuple)

        self.previous_distance = self._distance_to_goal()

        observation = self._get_obs()

        info = {"distance_to_goal": (self.previous_distance)}

        return observation, info

    def step(self, action: int):
        self.current_step += 1

        previous_position = self.drone_pos.copy()

        if action == 0:  # UP
            self.drone_pos[0] -= 1

        elif action == 1:  # DOWN
            self.drone_pos[0] += 1

        elif action == 2:  # LEFT
            self.drone_pos[1] -= 1

        elif action == 3:  # RIGHT
            self.drone_pos[1] += 1

        self.drone_pos = np.clip(
            self.drone_pos,
            0,
            self.grid_size - 1,
        )

        reward = -0.05

        terminated = False
        truncated = False

        current_distance = self._distance_to_goal()

        distance_shaping = (self.previous_distance - current_distance) * 6

        reward += distance_shaping

        reward += 2 / (current_distance + 1)

        self.previous_distance = current_distance

        current_pos_tuple = tuple(self.drone_pos)

        if current_pos_tuple in self.visited_positions:
            reward -= 5

        self.visited_positions.add(current_pos_tuple)

        self.last_positions.append(current_pos_tuple)

        if len(self.last_positions) > 8:
            self.last_positions.pop(0)

        if len(self.last_positions) >= 6 and len(set(self.last_positions)) <= 2:
            reward -= 20

        obstacle_up = self._obstacle_in_direction(
            dx=-1,
            dy=0,
        )

        obstacle_down = self._obstacle_in_direction(
            dx=1,
            dy=0,
        )

        obstacle_left = self._obstacle_in_direction(
            dx=0,
            dy=-1,
        )

        obstacle_right = self._obstacle_in_direction(
            dx=0,
            dy=1,
        )

        if action == 0 and obstacle_up:
            reward -= 15

        elif action == 1 and obstacle_down:
            reward -= 15

        elif action == 2 and obstacle_left:
            reward -= 15

        elif action == 3 and obstacle_right:
            reward -= 15

        min_obstacle_distance = self._min_obstacle_distance()

        if min_obstacle_distance < 1.5:
            reward -= 8

        collision = any(
            np.array_equal(
                self.drone_pos,
                obstacle,
            )
            for obstacle in self.obstacles
        )

        if collision:
            reward -= 200
            terminated = True

        if np.array_equal(
            self.drone_pos,
            self.goal_pos,
        ):
            reward += 150
            terminated = True

        if self.current_step >= self.max_steps:
            truncated = True

        observation = self._get_obs()

        info = {
            "distance_to_goal": (current_distance),
            "min_obstacle_distance": (min_obstacle_distance),
        }

        return (
            observation,
            reward,
            terminated,
            truncated,
            info,
        )

    def _get_obs(self) -> np.ndarray:
        relative_vector = self.goal_pos - self.drone_pos

        distance_to_goal = self._distance_to_goal()

        observation = np.array(
            [
                self.drone_pos[0] / self.grid_size,
                self.drone_pos[1] / self.grid_size,
                self.goal_pos[0] / self.grid_size,
                self.goal_pos[1] / self.grid_size,
                relative_vector[0] / self.grid_size,
                relative_vector[1] / self.grid_size,
                float(
                    self._obstacle_in_direction(
                        -1,
                        0,
                    )
                ),
                float(
                    self._obstacle_in_direction(
                        1,
                        0,
                    )
                ),
                float(
                    self._obstacle_in_direction(
                        0,
                        -1,
                    )
                ),
                float(
                    self._obstacle_in_direction(
                        0,
                        1,
                    )
                ),
                distance_to_goal / (np.sqrt(2) * self.grid_size),
            ],
            dtype=np.float32,
        )

        return observation

    def _obstacle_in_direction(
        self,
        dx: int,
        dy: int,
    ) -> bool:
        check_pos = self.drone_pos + np.array([dx, dy])

        if (
            check_pos[0] < 0
            or check_pos[0] >= self.grid_size
            or check_pos[1] < 0
            or check_pos[1] >= self.grid_size
        ):
            return True

        return any(
            np.array_equal(
                check_pos,
                obstacle,
            )
            for obstacle in self.obstacles
        )

    def _distance_to_goal(
        self,
    ) -> float:
        return float(np.linalg.norm(self.goal_pos - self.drone_pos))

    def _min_obstacle_distance(
        self,
    ) -> float:
        if not self.obstacles:
            return float(self.grid_size)

        distances = [
            np.linalg.norm(obstacle - self.drone_pos) for obstacle in self.obstacles
        ]

        return float(min(distances))

    def get_state_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "grid_size": self.grid_size,
            "obstacle_count": (self.obstacle_count),
            "max_steps": self.max_steps,
            "drone_pos": self.drone_pos.tolist(),
            "goal_pos": self.goal_pos.tolist(),
            "obstacles": [obstacle.tolist() for obstacle in self.obstacles],
            "current_step": (self.current_step),
        }

    def set_state_dict(
        self,
        state: dict[str, Any],
    ) -> None:
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

        self.obstacles = [
            np.array(
                obstacle,
                dtype=np.int32,
            )
            for obstacle in state["obstacles"]
        ]

        self.current_step = state["current_step"]

    def render(self):
        grid = np.full(
            (
                self.grid_size,
                self.grid_size,
            ),
            ".",
            dtype=object,
        )

        for obstacle in self.obstacles:
            grid[
                obstacle[0],
                obstacle[1],
            ] = "X"

        grid[
            self.goal_pos[0],
            self.goal_pos[1],
        ] = "G"

        grid[
            self.drone_pos[0],
            self.drone_pos[1],
        ] = "D"

        print("\n".join(" ".join(row) for row in grid))

        print()
