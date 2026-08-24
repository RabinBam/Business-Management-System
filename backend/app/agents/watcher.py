import functools
import uuid
from datetime import datetime, timezone

from app.schemas.watcher import WatcherEvent
from app.services.watcher_service import watcher_service

def with_retry_and_watch(service_name: str, max_retries: int = 3):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    if attempt > 1:
                        # Record Recovery if it succeeded after a failure
                        watcher_service.record(WatcherEvent(
                            id=str(uuid.uuid4()),
                            timestamp=datetime.now(timezone.utc),
                            event_type="recovery",
                            service=service_name,
                            details={"message": f"Recovered on attempt {attempt}"},
                            resolved=True
                        ))
                    return result
                except Exception as e:
                    # Record Failure or Retry
                    is_final_failure = attempt == max_retries
                    watcher_service.record(WatcherEvent(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now(timezone.utc),
                        event_type="failure" if is_final_failure else "retry",
                        service=service_name,
                        details={"error": str(e), "attempt": attempt},
                        resolved=False
                    ))
                    if is_final_failure:
                        raise e
        return wrapper
    return decorator