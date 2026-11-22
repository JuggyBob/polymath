"""Read-only reporting helpers for the telemetry event log."""


def load(log) -> int:
    return len(log.all_events())


def rate(log, start: int, end: int) -> float:
    if end <= start:
        raise ValueError("end must be greater than start")
    hits = log.window(start, end)
    return len(hits) / (end - start)


def rolling_sum(log, start: int, end: int) -> int:
    return sum(e.value for e in log.all_events() if start <= e.ts < end)


def top_kinds(log, n: int = 3):
    if n < 0:
        raise ValueError("n must be >= 0")
    totals = {}
    for e in log.all_events():
        totals[e.kind] = totals.get(e.kind, 0) + e.value
    ranked = sorted(totals, key=lambda k: (-totals[k], k))
    return [(k, totals[k]) for k in ranked[:n]]


def slow_rank(log):
    ranked = []
    remaining = list(log.all_events())
    while remaining:
        best = min(remaining, key=lambda e: (-e.value, e.event_id))
        ranked.append(best)
        remaining.remove(best)
    return ranked
