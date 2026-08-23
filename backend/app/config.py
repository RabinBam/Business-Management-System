import os
from dataclasses import dataclass


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    ai_provider: str = os.getenv("AI_PROVIDER", "mock")
    ai_primary_model: str = os.getenv("AI_PRIMARY_MODEL", "")
    ai_worker_model: str = os.getenv("AI_WORKER_MODEL", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./aegisflow.db")
    simulate_report_failure: bool = _as_bool(
        os.getenv("SIMULATE_REPORT_FAILURE", "false")
    )


settings = Settings()

