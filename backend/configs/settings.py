from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    grid_size: int = Field(default=10)
    obstacle_count: int = Field(default=3)
    max_steps: int = Field(default=200)

    total_timesteps: int = Field(default=1_000_000)

    learning_rate: float = Field(default=3e-4)
    n_steps: int = Field(default=2048)
    batch_size: int = Field(default=64)
    n_epochs: int = Field(default=10)

    gamma: float = Field(default=0.99)
    gae_lambda: float = Field(default=0.95)

    clip_range: float = Field(default=0.2)
    ent_coef: float = Field(default=0.05)

    mlflow_tracking_uri: str = "file:./mlruns"
    mlflow_experiment_name: str = "AeroRL-PPO"

    model_dir: str = str(BASE_DIR / "models")
    model_name: str = "drone_agent.zip"

    cors_origins: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
