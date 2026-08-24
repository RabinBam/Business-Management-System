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
    management_max_revisions: int = _as_positive_int(
        os.getenv("MANAGEMENT_MAX_REVISIONS", "2"), default=2
    )
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./aegisflow.db")
    rate_limit_requests: int = _as_positive_int(
        os.getenv("RATE_LIMIT_REQUESTS", "120"), default=120
    )
    rate_limit_window_seconds: int = _as_positive_int(
        os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"), default=60
    )
    max_request_bytes: int = _as_positive_int(
        os.getenv("MAX_REQUEST_BYTES", "1000000"), default=1_000_000
    )
    admin_api_key: str = os.getenv("ADMIN_API_KEY", "")
    trusted_hosts: tuple[str, ...] = tuple(
        host.strip()
        for host in os.getenv(
            "TRUSTED_HOSTS",
            "localhost,127.0.0.1,backend,testserver",
        ).split(",")
        if host.strip()
    )
    simulate_report_failure: bool = _as_bool(
        os.getenv("SIMULATE_REPORT_FAILURE", "false")
    )


settings = Settings()
