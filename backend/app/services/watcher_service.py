from app.schemas.watcher import WatcherEvent, WatcherState, WatcherStatus


class WatcherService:
    def __init__(self) -> None:
        self._events: list[WatcherEvent] = []

    def record(self, event: WatcherEvent) -> None:
        self._events.append(event)

    def status(self) -> WatcherStatus:
        active = sum(not event.resolved for event in self._events)
        return WatcherStatus(
            state=WatcherState.ACTIVE if active else WatcherState.IDLE,
            active_incidents=active,
            events=list(reversed(self._events[-50:])),
        )


watcher_service = WatcherService()

