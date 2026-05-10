from __future__ import annotations

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

import gymnasium as gym
import mlflow
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import (
    BaseCallback,
    CallbackList,
    CheckpointCallback,
    EvalCallback,
)
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv

from backend.configs.settings import settings
from backend.env.drone_env import DroneEnv


class MLflowCallback(BaseCallback):
    """Custom callback for MLflow rollout metric logging."""

    def __init__(self, verbose: int = 0) -> None:
        super().__init__(verbose)

    def _on_step(self) -> bool:
        """Required callback implementation."""

        return True

    def _on_rollout_end(self) -> None:
        """Log rollout metrics to MLflow."""

        ep_rewards = []
        ep_lengths = []

        if hasattr(self.model, "ep_info_buffer"):
            for episode in self.model.ep_info_buffer:
                ep_rewards.append(episode["r"])
                ep_lengths.append(episode["l"])

        if ep_rewards:
            mlflow.log_metric(
                "rollout/ep_rew_mean",
                float(np.mean(ep_rewards)),
                step=self.num_timesteps,
            )

            mlflow.log_metric(
                "rollout/ep_rew_max",
                float(np.max(ep_rewards)),
                step=self.num_timesteps,
            )

            mlflow.log_metric(
                "rollout/ep_rew_min",
                float(np.min(ep_rewards)),
                step=self.num_timesteps,
            )

        if ep_lengths:
            mlflow.log_metric(
                "rollout/ep_len_mean",
                float(np.mean(ep_lengths)),
                step=self.num_timesteps,
            )


def make_env(seed: int) -> Callable[[], gym.Env]:
    """
    Create monitored DroneEnv instance.

    Args:
        seed: Random seed

    Returns:
        Callable environment factory
    """

    def _init() -> gym.Env:
        env = DroneEnv(
            grid_size=settings.grid_size,
            obstacle_count=settings.obstacle_count,
            max_steps=settings.max_steps,
        )

        env.reset(seed=seed)

        monitored_env = Monitor(env)

        return monitored_env

    return _init


def train() -> None:
    """Train PPO agent for AeroRL."""

    os.makedirs(settings.model_dir, exist_ok=True)

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)

    start_time = time.time()

    env = DummyVecEnv([make_env(seed=100 + i) for i in range(4)])

    eval_env = DummyVecEnv([make_env(seed=999)])

    model = PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=settings.learning_rate,
        n_steps=settings.n_steps,
        batch_size=settings.batch_size,
        n_epochs=settings.n_epochs,
        gamma=settings.gamma,
        gae_lambda=settings.gae_lambda,
        clip_range=settings.clip_range,
        ent_coef=0.05,
        verbose=1,
        tensorboard_log="./logs/tensorboard/",
    )

    checkpoint_callback = CheckpointCallback(
        save_freq=10_000,
        save_path=f"{settings.model_dir}/checkpoints",
        name_prefix="drone_agent_checkpoint",
    )

    eval_callback = EvalCallback(
        eval_env=eval_env,
        best_model_save_path=f"{settings.model_dir}/best_model",
        log_path="./logs/eval/",
        eval_freq=5_000,
        n_eval_episodes=20,
        deterministic=True,
        render=False,
    )

    mlflow_callback = MLflowCallback()

    callback = CallbackList(
        [
            checkpoint_callback,
            eval_callback,
            mlflow_callback,
        ]
    )
    with mlflow.start_run():

        mlflow.log_params(
            {
                "grid_size": settings.grid_size,
                "obstacle_count": settings.obstacle_count,
                "max_steps": settings.max_steps,
                "total_timesteps": settings.total_timesteps,
                "learning_rate": settings.learning_rate,
                "n_steps": settings.n_steps,
                "batch_size": settings.batch_size,
                "n_epochs": settings.n_epochs,
                "gamma": settings.gamma,
                "gae_lambda": settings.gae_lambda,
                "clip_range": settings.clip_range,
                "ent_coef": settings.ent_coef,
            }
        )

        print("\nStarting PPO training...\n")

        model.learn(
            total_timesteps=settings.total_timesteps,
            callback=callback,
            progress_bar=True,
        )

        elapsed_time = time.time() - start_time

        mlflow.log_metric(
            "training/elapsed_time_seconds",
            elapsed_time,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        versioned_model_name = f"drone_agent_{timestamp}.zip"

        versioned_model_path = Path(settings.model_dir) / versioned_model_name

        latest_model_path = Path(settings.model_dir) / settings.model_name

        model.save(versioned_model_path)
        model.save(latest_model_path)

        mlflow.log_artifact(str(versioned_model_path))

        mlflow.log_artifact(str(latest_model_path))

        print("\nTraining complete.")
        print(f"Elapsed Time: {elapsed_time:.2f} seconds")
        print(f"Saved latest model -> {latest_model_path}")
        print(f"Saved versioned model -> {versioned_model_path}")

    env.close()
    eval_env.close()


if __name__ == "__main__":
    train()
