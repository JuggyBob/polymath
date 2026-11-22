"""Iteration helpers for the telemetry event log."""

_KIND_ITER = None


def iter_kinds(log):
    seen = set()
    for e in log.all_events():
        if e.kind not in seen:
            seen.add(e.kind)
            yield e.kind


def traced(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def make_filter(kind):
    return lambda event: event.kind == kind
