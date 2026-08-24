from threading import RLock

from app.schemas.watcher import WatcherEvent, WatcherState, WatcherStatus


class WatcherService:
    """Thread-safe in-memory event store for workflow reliability signals."""

    def __init__(self) -> None:
        self._events: list[WatcherEvent] = []
        self._lock = RLock()

    def record(self, event: WatcherEvent) -> WatcherEvent:
        stored = event.model_copy(deep=True)
        with self._lock:
            self._events.append(stored)
        return stored.model_copy(deep=True)

    def record_event(
        self,
        *,
        workflow_id: str | None,
        component: str,
        event_type: str,
        message: str,
        retry_count: int = 0,
        resolved: bool = False,
    ) -> WatcherEvent:
        return self.record(
            WatcherEvent(
                workflow_id=workflow_id,
                component=component,
                event_type=event_type,
                message=message,
                retry_count=retry_count,
                resolved=resolved,
            )
        )

    def resolve(self, *, workflow_id: str | None, component: str) -> None:
        with self._lock:
            for index, event in enumerate(self._events):
                if (
                    not event.resolved
                    and event.workflow_id == workflow_id
                    and event.component == component
                ):
                    self._events[index] = event.model_copy(update={"resolved": True})

    def status(self) -> WatcherStatus:
        with self._lock:
            events = [event.model_copy(deep=True) for event in self._events[-50:]]
        active = sum(not event.resolved for event in events)
        return WatcherStatus(
            state=WatcherState.ACTIVE if active else WatcherState.IDLE,
            active_incidents=active,
            events=list(reversed(events)),
        )

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


watcher_service = WatcherService()
