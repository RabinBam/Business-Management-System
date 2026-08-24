from threading import RLock

from app.database import SQLiteJsonStore, get_json_store
from app.schemas.watcher import WatcherEvent, WatcherState, WatcherStatus


class WatcherService:
    """Thread-safe, SQLite-backed event store for workflow reliability signals."""

    def __init__(self, *, store: SQLiteJsonStore | None = None) -> None:
        self._events: list[WatcherEvent] = []
        self._lock = RLock()
        self._store = store
        if store is not None:
            payload = store.get("watcher", "events")
            if payload is not None:
                self._events = [
                    WatcherEvent.model_validate(event)
                    for event in payload.get("items", [])
                ]

    def record(self, event: WatcherEvent) -> WatcherEvent:
        stored = event.model_copy(deep=True)
        with self._lock:
            self._events.append(stored)
            self._events = self._events[-500:]
            self._persist()
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
            self._persist()

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
            if self._store is not None:
                self._store.delete("watcher", "events")

    def delete_workflow_events(self, workflow_id: str) -> None:
        with self._lock:
            self._events = [
                event for event in self._events if event.workflow_id != workflow_id
            ]
            self._persist()

    def prune_orphans(self, valid_workflow_ids: set[str]) -> None:
        with self._lock:
            self._events = [
                event
                for event in self._events
                if event.workflow_id is None or event.workflow_id in valid_workflow_ids
            ]
            self._persist()

    def _persist(self) -> None:
        if self._store is None:
            return
        self._store.put(
            "watcher",
            "events",
            {"items": [event.model_dump(mode="json") for event in self._events]},
        )


watcher_service = WatcherService(store=get_json_store())
