"""Reset presentation data before any application services load."""
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path


def reset_demo(database_path: Path) -> None:
    if not database_path.exists():
        return
    namespaces = ("workflows", "workflow_tasks", "workflow_artifacts", "reports",
                  "marketing_plans", "watcher", "money")
    with sqlite3.connect(database_path) as connection:
        if not connection.execute("SELECT 1 FROM sqlite_master WHERE name='json_records'").fetchone():
            return
        if connection.execute("SELECT count(*) FROM json_records").fetchone()[0]:
            backup = database_path.with_name(
                "byapari-before-launch-" + datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f") + ".db"
            )
            with sqlite3.connect(backup) as destination:
                connection.backup(destination)
        connection.executemany("DELETE FROM json_records WHERE namespace = ?",
                               [(name,) for name in namespaces])


if __name__ == "__main__":
    if os.getenv("RESET_DEMO_ON_START", "true").lower() == "true":
        url = os.getenv("DATABASE_URL", "sqlite:////app/data/aegisflow.db")
        if not url.startswith("sqlite:///"):
            raise ValueError("Demo reset requires SQLite")
        reset_demo(Path(url.removeprefix("sqlite:///")))
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
