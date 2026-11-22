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
        chosen = [e for e in self._events if start <= e.ts < end]
        chosen.sort(key=lambda e: e.ts)
        # For ties in timestamp, reverse so later-inserted comes first
        result = []
        i = 0
        while i < len(chosen):
            j = i
            while j < len(chosen) and chosen[j].ts == chosen[i].ts:
                j += 1
            result.extend(chosen[i:j][::-1])
            i = j
        return result

    def by_kind(self, kind: str):
        return [e for e in self._events if e.kind == kind]

    def prune(self, before: int):
        removed = [e.event_id for e in self._events if e.ts < before]
        self._events = [e for e in self._events if e.ts >= before]
        for eid in removed:
            del self._by_id[eid]
        return sorted(removed)

    def latest(self, n: int = 1):
        if n < 0:
            raise ValueError("n must be >= 0")
        if n == 0:
            return []
        sorted_events = sorted(self._events, key=lambda e: e.ts, reverse=True)
        return sorted_events[:n]

    def total(self) -> int:
        return sum(e.value for e in self._events)

    def snapshot(self):
        return dict(self._by_id)

    def clear(self):
        self._events = []
        self._by_id = {}
        self._cache = None
