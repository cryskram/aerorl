from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from fastapi import FastAPI, HTTPException, Query, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from stable_baselines3 import PPO

from backend.configs.settings import settings
from backend.env.drone_env import DroneEnv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aerorl")


@dataclass
class AppState:
    """Global application state."""

    model: PPO | None
    env: DroneEnv
    model_loaded_at: datetime | None
    total_predictions: int
    total_simulations: int
    total_goal_reached: int


class HealthResponse(BaseModel):
    """Health response model."""

    status: str
    model_loaded: bool
    model_loaded_at: datetime | None


class PredictResponse(BaseModel):
    """Prediction response model."""

    action: int
    action_name: str
    observation: list[float]


class SimulateRequest(BaseModel):
    """Simulation request."""

    seed: int | None = None
    max_steps: int = Field(default=100, ge=1)


class SimulateResponse(BaseModel):
    """Simulation response."""

    total_reward: float
    steps: int
    reached_goal: bool
    final_state: dict[str, Any]


class ResetRequest(BaseModel):
    """Reset environment request."""

    seed: int | None = None


class MetricsResponse(BaseModel):
    """Metrics response."""

    total_predictions: int
    total_simulations: int
    total_goal_reached: int
    success_rate: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""

    logger.info("Starting AeroRL backend...")

    env = DroneEnv(
        grid_size=settings.grid_size,
        obstacle_count=settings.obstacle_count,
        max_steps=settings.max_steps,
    )

    env.reset(seed=42)

    model = None
    model_loaded_at = None

    model_path = Path(settings.model_dir) / settings.model_name

    if model_path.exists():
        try:
            model = PPO.load(str(model_path))

            model_loaded_at = datetime.utcnow()

            logger.info(
                "Model loaded successfully from %s",
                model_path,
            )

        except Exception as exc:
            logger.warning(
                "Failed to load model: %s",
                exc,
            )

    else:
        logger.warning(
            "No trained model found at %s",
            model_path,
        )

    app.state.state = AppState(
        model=model,
        env=env,
        model_loaded_at=model_loaded_at,
        total_predictions=0,
        total_simulations=0,
        total_goal_reached=0,
    )

    yield

    logger.info("Shutting down AeroRL backend...")


app = FastAPI(
    title="AeroRL API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_state() -> AppState:
    """Get app state."""

    return app.state.state


def ensure_model_loaded(state: AppState) -> PPO:
    """Ensure PPO model is available."""

    if state.model is None:
        raise HTTPException(
            status_code=503,
            detail=("Model not loaded. " "Train the PPO agent first."),
        )

    return state.model


@app.get(
    "/health",
    response_model=HealthResponse,
)
async def health() -> HealthResponse:
    """Health check endpoint."""

    state = get_state()

    return HealthResponse(
        status="healthy",
        model_loaded=state.model is not None,
        model_loaded_at=state.model_loaded_at,
    )


@app.get(
    "/predict",
    response_model=PredictResponse,
)
async def predict(
    x: int = Query(..., ge=0),
    y: int = Query(..., ge=0),
) -> PredictResponse:
    """Predict next action."""

    state = get_state()

    model = ensure_model_loaded(state)

    env = state.env

    env.drone_pos = np.array([x, y])

    observation = env._get_obs()

    action, _ = model.predict(
        observation,
        deterministic=True,
    )

    state.total_predictions += 1

    return PredictResponse(
        action=int(action),
        action_name=env.ACTION_NAMES[int(action)],
        observation=observation.tolist(),
    )


@app.post(
    "/simulate",
    response_model=SimulateResponse,
)
async def simulate(
    request: SimulateRequest,
) -> SimulateResponse:
    """Run simulation episode."""

    state = get_state()

    model = ensure_model_loaded(state)

    env = state.env

    observation, _ = env.reset(seed=request.seed)

    total_reward = 0.0
    reached_goal = False

    for _ in range(request.max_steps):

        action, _ = model.predict(
            observation,
            deterministic=True,
        )

        observation, reward, terminated, truncated, _ = env.step(int(action))

        total_reward += reward

        if terminated or truncated:

            reached_goal = bool(
                np.array_equal(
                    env.drone_pos,
                    env.goal_pos,
                )
            )

            break

    state.total_simulations += 1

    if reached_goal:
        state.total_goal_reached += 1

    return SimulateResponse(
        total_reward=total_reward,
        steps=env.current_step,
        reached_goal=reached_goal,
        final_state=env.get_state_dict(),
    )


@app.get("/env/state")
async def env_state() -> dict[str, Any]:
    """Return current environment state."""

    state = get_state()

    return state.env.get_state_dict()


@app.post("/env/reset")
async def env_reset(
    request: ResetRequest,
) -> dict[str, Any]:
    """Reset environment."""

    state = get_state()

    observation, info = state.env.reset(
        seed=request.seed,
    )

    return {
        "observation": observation.tolist(),
        "info": info,
        "state": state.env.get_state_dict(),
    }


@app.get(
    "/metrics",
    response_model=MetricsResponse,
)
async def metrics() -> MetricsResponse:
    """Return application metrics."""

    state = get_state()

    success_rate = 0.0

    if state.total_simulations > 0:
        success_rate = (state.total_goal_reached / state.total_simulations) * 100

    return MetricsResponse(
        total_predictions=state.total_predictions,
        total_simulations=state.total_simulations,
        total_goal_reached=state.total_goal_reached,
        success_rate=round(success_rate, 2),
    )


@app.websocket("/ws/simulate")
async def websocket_simulate(
    websocket: WebSocket,
) -> None:
    """Live simulation websocket."""

    await websocket.accept()

    state = get_state()

    if state.model is None:
        await websocket.send_json(
            {
                "type": "error",
                "message": ("Model not loaded. " "Train the agent first."),
            }
        )

        await websocket.close()

        return

    model = state.model

    try:
        while True:

            config = await websocket.receive_json()

            seed = config.get("seed")
            grid_size = config.get(
                "grid_size",
                settings.grid_size,
            )

            obstacle_count = config.get(
                "obstacle_count",
                settings.obstacle_count,
            )

            delay_ms = config.get(
                "delay_ms",
                200,
            )

            env = DroneEnv(
                grid_size=grid_size,
                obstacle_count=obstacle_count,
                max_steps=settings.max_steps,
            )

            observation, _ = env.reset(seed=seed)

            total_reward = 0.0

            await websocket.send_json(
                {
                    "type": "init",
                    "state": env.get_state_dict(),
                }
            )

            done = False

            while not done:

                action, _ = model.predict(
                    observation,
                    deterministic=True,
                )

                (
                    observation,
                    reward,
                    terminated,
                    truncated,
                    _,
                ) = env.step(int(action))

                done = terminated or truncated

                total_reward += reward

                reached_goal = bool(
                    np.array_equal(
                        env.drone_pos,
                        env.goal_pos,
                    )
                )

                await websocket.send_json(
                    {
                        "type": "step",
                        "state": env.get_state_dict(),
                        "action": int(action),
                        "action_name": env.ACTION_NAMES[int(action)],
                        "reward": reward,
                        "total_reward": total_reward,
                        "done": done,
                        "reached_goal": reached_goal,
                    }
                )

                await asyncio.sleep(delay_ms / 1000)

            state.total_simulations += 1

            if reached_goal:
                state.total_goal_reached += 1

            await websocket.send_json(
                {
                    "type": "done",
                    "state": env.get_state_dict(),
                    "total_reward": total_reward,
                    "reached_goal": reached_goal,
                }
            )

    except Exception as exc:
        logger.error(
            "WebSocket error: %s",
            exc,
        )

        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
