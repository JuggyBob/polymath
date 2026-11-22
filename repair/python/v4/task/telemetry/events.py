"""Domain type for the telemetry event log."""


class Event:
    def __init__(self, event_id, ts, kind, value, tags=None):
        self.event_id = event_id
        self.ts = ts
        self.kind = kind
        self.value = value
        self.tags = list(tags) if tags is not None else []

    def __eq__(self, other):
        if not isinstance(other, Event):
            return NotImplemented
        return self.event_id == other.event_id

    def __hash__(self):
        return hash((self.event_id, self.ts, self.kind, self.value, tuple(self.tags)))

    def __repr__(self):
        return f"Event({self.event_id!r}, {self.ts}, {self.kind!r}, {self.value})"
