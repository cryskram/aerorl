from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.env.drone_env import DroneEnv


@dataclass
class MockAppState:

    env: DroneEnv
    total_predictions: int = 0
    total_simulations: int = 0
    total_goal_reached: int = 0


def create_test_app() -> FastAPI:

    app = FastAPI()

    env = DroneEnv(
        grid_size=10,
        obstacle_count=5,
        max_steps=50,
    )

    env.reset(seed=42)

    app.state.state = MockAppState(env=env)

    @app.get("/health")
    async def health() -> dict:
        return {
            "status": "healthy",
            "model_loaded": False,
        }

    @app.get("/metrics")
    async def metrics() -> dict:
        state = app.state.state

        return {
            "total_predictions": state.total_predictions,
            "total_simulations": state.total_simulations,
            "total_goal_reached": state.total_goal_reached,
        }

    @app.get("/env/state")
    async def env_state() -> dict:
        return app.state.state.env.get_state_dict()

    @app.post("/env/reset")
    async def env_reset() -> dict:
        obs, _ = app.state.state.env.reset(seed=123)

        return {
            "observation": obs.tolist(),
            "state": app.state.state.env.get_state_dict(),
        }

    return app


class TestDroneEnv:

    @pytest.fixture()
    def env(self) -> DroneEnv:

        environment = DroneEnv(
            grid_size=10,
            obstacle_count=5,
            max_steps=20,
        )

        environment.reset(seed=42)

        return environment

    def test_reset_returns_correct_shape(
        self,
        env: DroneEnv,
    ) -> None:

        observation, _ = env.reset(seed=42)

        assert observation.shape == (11,)

    def test_reset_drone_at_origin(
        self,
        env: DroneEnv,
    ) -> None:

        env.reset(seed=42)

        assert np.array_equal(
            env.drone_pos,
            np.array([0, 0]),
        )

    def test_reset_goal_at_corner(
        self,
        env: DroneEnv,
    ) -> None:

        env.reset(seed=42)

        assert np.array_equal(
            env.goal_pos,
            np.array([9, 9]),
        )

    def test_step_returns_correct_types(
        self,
        env: DroneEnv,
    ) -> None:

        observation, reward, terminated, truncated, info = env.step(3)

        assert isinstance(observation, np.ndarray)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)

    def test_drone_clipped_at_boundary(
        self,
        env: DroneEnv,
    ) -> None:

        env.drone_pos = np.array([0, 0])

        env.step(0)
        env.step(2)

        assert np.array_equal(
            env.drone_pos,
            np.array([0, 0]),
        )

    def test_goal_reward(
        self,
        env: DroneEnv,
    ) -> None:

        env.drone_pos = np.array([8, 9])
        env.goal_pos = np.array([9, 9])

        observation, reward, terminated, truncated, _ = env.step(1)

        assert terminated is True
        assert reward >= 150
        assert truncated is False

    def test_obstacle_collision_penalty(
        self,
        env: DroneEnv,
    ) -> None:

        env.drone_pos = np.array([0, 0])

        env.obstacles = [(1, 0)]

        observation, reward, terminated, truncated, _ = env.step(1)

        assert terminated is True
        assert reward <= -150

    def test_max_steps_truncation(
        self,
        env: DroneEnv,
    ) -> None:

        env.current_step = env.max_steps - 1

        observation, reward, terminated, truncated, _ = env.step(3)

        assert truncated is True

    def test_no_obstacle_at_start_or_goal(
        self,
        env: DroneEnv,
    ) -> None:

        for seed in range(10):
            env.reset(seed=seed)

            forbidden = {
                (0, 0),
                (9, 9),
            }

            for obstacle in env.obstacles:
                assert tuple(obstacle) not in forbidden

    def test_get_state_dict_structure(
        self,
        env: DroneEnv,
    ) -> None:

        state = env.get_state_dict()

        expected_keys = {
            "grid_size",
            "obstacle_count",
            "max_steps",
            "drone_pos",
            "goal_pos",
            "obstacles",
            "current_step",
        }

        assert set(state.keys()) == expected_keys

    def test_observation_bounds(
        self,
        env: DroneEnv,
    ) -> None:

        observation, _ = env.reset(seed=42)

        assert env.observation_space.contains(observation)


class TestAPI:

    @pytest.fixture()
    def client(self) -> TestClient:

        app = create_test_app()

        return TestClient(app)

    def test_health_endpoint(
        self,
        client: TestClient,
    ) -> None:

        response = client.get("/health")

        assert response.status_code == 200

        payload = response.json()

        assert payload["status"] == "healthy"

    def test_metrics_endpoint(
        self,
        client: TestClient,
    ) -> None:

        response = client.get("/metrics")

        assert response.status_code == 200

        payload = response.json()

        assert "total_predictions" in payload
        assert "total_simulations" in payload
        assert "total_goal_reached" in payload

    def test_env_state_endpoint(
        self,
        client: TestClient,
    ) -> None:

        response = client.get("/env/state")

        assert response.status_code == 200

        payload = response.json()

        assert "drone_pos" in payload
        assert "goal_pos" in payload
        assert "obstacles" in payload

    def test_env_reset_endpoint(
        self,
        client: TestClient,
    ) -> None:

        response = client.post("/env/reset")

        assert response.status_code == 200

        payload = response.json()

        assert "observation" in payload
        assert "state" in payload

        assert len(payload["observation"]) == 11
