"""Iteration helpers for the telemetry event log."""

_KIND_ITER = None


def iter_kinds(log):
    global _KIND_ITER
    if _KIND_ITER is None:
        _KIND_ITER = iter(dict.fromkeys(e.kind for e in log.all_events()))
    yield from _KIND_ITER


def traced(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def make_filter(kind):
    return lambda event: kind in event.kind
