import functools
import inspect
from collections.abc import Awaitable, Callable
from typing import cast

from app.services.watcher_service import WatcherService, watcher_service


async def execute_with_watch[T](
    component: str,
    operation: Callable[[], Awaitable[T] | T],
    *,
    workflow_id: str | None = None,
    max_retries: int = 1,
    service: WatcherService = watcher_service,
) -> T:
    """Execute an operation and record retry, failure, and recovery events."""

    if max_retries < 0:
        raise ValueError("max_retries cannot be negative")

    for attempt in range(max_retries + 1):
        try:
            value = operation()
            result = await value if inspect.isawaitable(value) else value
        except Exception as exc:
            final_attempt = attempt == max_retries
            service.record_event(
                workflow_id=workflow_id,
                component=component,
                event_type="FAILED" if final_attempt else "RETRY",
                message=f"{exc.__class__.__name__}: {exc}",
                retry_count=attempt,
            )
            if final_attempt:
                raise
        else:
            if attempt:
                service.resolve(workflow_id=workflow_id, component=component)
                service.record_event(
                    workflow_id=workflow_id,
                    component=component,
                    event_type="RECOVERED",
                    message=f"Recovered on attempt {attempt + 1}",
                    retry_count=attempt,
                    resolved=True,
                )
            return cast(T, result)

    raise RuntimeError("Retry loop exited unexpectedly")


def with_retry_and_watch[**P, T](
    service_name: str,
    max_retries: int = 1,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Decorator form used by agent operations that expose ``workflow_id``."""

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            workflow_id = kwargs.get("workflow_id")
            return await execute_with_watch(
                service_name,
                lambda: func(*args, **kwargs),
                workflow_id=str(workflow_id) if workflow_id is not None else None,
                max_retries=max_retries,
            )

        return wrapper

    return decorator
