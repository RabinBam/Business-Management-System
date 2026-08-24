"""Small durable repository used by the MVP services.

The application stores validated Pydantic payloads as JSON documents in
SQLite. Services own their schemas and use namespaces to avoid coupling the
database layer to workflow, report, marketing, or watcher models.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from threading import RLock
from typing import Any

from app.config import settings


class DatabaseConfigurationError(RuntimeError):
    """Raised when the configured database URL is unsupported."""


class SQLiteJsonStore:
    """Thread-safe namespaced JSON document store backed by SQLite."""

    def __init__(self, database_url: str) -> None:
        database_path = _sqlite_path(database_url)
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(
            database_path,
            check_same_thread=False,
            timeout=10,
        )
        self._connection.row_factory = sqlite3.Row
        self._lock = RLock()
        self._initialize()

    def put(self, namespace: str, key: str, payload: Mapping[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO json_records(namespace, record_key, payload)
                VALUES (?, ?, ?)
                ON CONFLICT(namespace, record_key)
                DO UPDATE SET payload = excluded.payload,
                              updated_at = CURRENT_TIMESTAMP
                """,
                (namespace, key, encoded),
            )

    def get(self, namespace: str, key: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT payload FROM json_records WHERE namespace = ? AND record_key = ?",
                (namespace, key),
            ).fetchone()
        if row is None:
            return None
        payload = json.loads(str(row["payload"]))
        if not isinstance(payload, dict):
            raise ValueError(f"Stored {namespace}/{key} payload is not an object")
        return payload

    def list(self, namespace: str) -> list[tuple[str, dict[str, Any]]]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT record_key, payload
                FROM json_records
                WHERE namespace = ?
                ORDER BY created_at, record_key
                """,
                (namespace,),
            ).fetchall()
        records: list[tuple[str, dict[str, Any]]] = []
        for row in rows:
            payload = json.loads(str(row["payload"]))
            if isinstance(payload, dict):
                records.append((str(row["record_key"]), payload))
        return records

    def delete(self, namespace: str, key: str) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                "DELETE FROM json_records WHERE namespace = ? AND record_key = ?",
                (namespace, key),
            )

    def clear_namespace(self, namespace: str) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                "DELETE FROM json_records WHERE namespace = ?",
                (namespace,),
            )

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def _initialize(self) -> None:
        with self._lock, self._connection:
            self._connection.execute("PRAGMA journal_mode = WAL")
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS json_records (
                    namespace TEXT NOT NULL,
                    record_key TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(namespace, record_key)
                )
                """
            )


def _sqlite_path(database_url: str) -> str:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise DatabaseConfigurationError(
            "Only sqlite:/// database URLs are supported by this deployment"
        )
    raw_path = database_url[len(prefix) :]
    if raw_path == ":memory:":
        return raw_path
    path = Path(raw_path)
    return str(path if path.is_absolute() else (Path.cwd() / path).resolve())


@lru_cache(maxsize=1)
def get_json_store() -> SQLiteJsonStore:
    return SQLiteJsonStore(settings.database_url)
