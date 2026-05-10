from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "AeroRL"

    grid_size: int = Field(default=10, ge=5, le=50)
    obstacle_count: int = Field(default=10, ge=0)
    max_steps: int = Field(default=200, ge=1)

    total_timesteps: int = Field(default=100_000, ge=1)
    learning_rate: float = Field(default=3e-4, gt=0)
    n_steps: int = Field(default=2048, ge=1)
    batch_size: int = Field(default=64, ge=1)
    n_epochs: int = Field(default=10, ge=1)
    gamma: float = Field(default=0.99, gt=0, le=1)
    gae_lambda: float = Field(default=0.95, gt=0, le=1)
    clip_range: float = Field(default=0.2, gt=0)
    ent_coef: float = Field(default=0.01, ge=0)

    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "AeroRL-PPO"

    model_dir: str = "models"
    model_name: str = "drone_agent.zip"

    cors_origins: List[str] = [
        "http://localhost:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
