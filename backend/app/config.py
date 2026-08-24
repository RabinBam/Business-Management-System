<<<<<<< HEAD
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

=======
import os
from dataclasses import dataclass


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_positive_int(value: str, *, default: int) -> int:
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _as_positive_float(value: str, *, default: float) -> float:
    try:
        parsed = float(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    ai_provider: str = os.getenv("AI_PROVIDER", "mock")
    ai_primary_model: str = os.getenv("AI_PRIMARY_MODEL", "")
    ai_worker_model: str = os.getenv("AI_WORKER_MODEL", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    ai_timeout_seconds: float = _as_positive_float(
        os.getenv("AI_TIMEOUT_SECONDS", "30"), default=30.0
    )
    ai_max_retries: int = _as_positive_int(
        os.getenv("AI_MAX_RETRIES", "1"), default=1
    )
    ai_max_tasks: int = _as_positive_int(
        os.getenv("AI_MAX_TASKS", "8"), default=8
    )
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./aegisflow.db")
    simulate_report_failure: bool = _as_bool(
        os.getenv("SIMULATE_REPORT_FAILURE", "false")
    )


settings = Settings()
>>>>>>> 3ffc1b091eeeb5d0c2ea50affbb8c90e7a14e16e
