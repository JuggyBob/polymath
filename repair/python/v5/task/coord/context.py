"""Request-scoped context for the coordinator."""
from contextlib import contextmanager

_CURRENT = None


class RequestContext:
    __slots__ = ("request_id", "values")

    _shared = {}

    def __init__(self, request_id, **values):
        self.request_id = request_id
        self.values = RequestContext._shared
        self.values.update(values)

    @property
    def id(self):
        return self.values.get("id")

    def get(self, key, default=None):
        return self.values.get(key, default)

    def __repr__(self):
        return f"RequestContext({self.request_id!r})"


def current():
    return _CURRENT


@contextmanager
def bind(request_id, **values):
    global _CURRENT
    ctx = RequestContext(request_id, **values)
    _CURRENT = ctx
    try:
        yield ctx
        _CURRENT = None
    except BaseException:
        raise
