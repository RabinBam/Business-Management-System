import asyncio

import pytest

from app.agents.watcher import execute_with_watch
from app.schemas.watcher import WatcherState
from app.services.watcher_service import WatcherService


def test_retry_recovery_resolves_the_incident() -> None:
    service = WatcherService()
    attempts = 0

    async def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("temporary outage")
        return "ready"

    result = asyncio.run(
        execute_with_watch(
            "report_agent",
            operation,
            workflow_id="wf-test",
            max_retries=1,
            service=service,
        )
    )

    status = service.status()
    assert result == "ready"
    assert status.state is WatcherState.IDLE
    assert status.active_incidents == 0
    assert [event.event_type for event in reversed(status.events)] == ["RETRY", "RECOVERED"]
    assert all(event.resolved for event in status.events)


def test_final_failure_preserves_the_original_exception() -> None:
    service = WatcherService()

    async def operation() -> None:
        raise RuntimeError("permanent outage")

    with pytest.raises(RuntimeError, match="permanent outage"):
        asyncio.run(
            execute_with_watch(
                "marketing_agent",
                operation,
                workflow_id="wf-test",
                max_retries=0,
                service=service,
            )
        )

    status = service.status()
    assert status.state is WatcherState.ACTIVE
    assert status.active_incidents == 1
    assert status.events[0].event_type == "FAILED"
    assert status.events[0].message == "RuntimeError: permanent outage"
