"""In-memory telemetry event log."""

from .events import Event


class EventLog:
    def __init__(self, name=""):
        self.name = name
        self._events = []
        self._by_id = {}
        self._cache = None

    def append(self, event: Event) -> None:
        if event.event_id in self._by_id:
            raise ValueError(f"duplicate id: {event.event_id}")
        self._events.append(event)
        self._by_id[event.event_id] = event

    def get(self, event_id: str) -> Event:
        return self._by_id[event_id]

    def all_events(self):
        return list(self._events)

    def window(self, start: int, end: int):
        chosen = [e for e in self._events if start <= e.ts <= end]
        return sorted(chosen, key=lambda e: e.ts)

    def by_kind(self, kind: str):
        return [e for e in self._events if e.kind == kind]

    def prune(self, before: int):
        removed = []
        for event in self._events:
            if event.ts < before:
                self._events.remove(event)
                removed.append(event.event_id)
        return sorted(removed)

    def latest(self, n: int = 1):
        if n < 0:
            raise ValueError("n must be >= 0")
        if n == 0:
            return []
        if self._cache is not None:
            return self._cache
        self._cache = sorted(set(self._events), key=lambda e: e.ts, reverse=True)[:n]
        return self._cache

    def total(self) -> int:
        return sum(e.value for e in self._events)

    def snapshot(self):
        return dict(self._by_id)

    def clear(self):
        self._events = []
        self._by_id = {}
