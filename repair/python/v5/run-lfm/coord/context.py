"""Request-scoped context for the coordinator."""
from contextvars import ContextVar
from contextlib import contextmanager

_request_context = ContextVar("request_context", default=None)


class RequestContext:
    __slots__ = ("request_id", "values")

    def __init__(self, request_id, **values):
        self.request_id = request_id
        self.values = dict(values)

    @property
    def id(self):
        return self.request_id

    def get(self, key, default=None):
        return self.values.get(key, default)

    def __repr__(self):
        return f"RequestContext({self.request_id!r})"


def current():
    return _request_context.get()


@contextmanager
def bind(request_id, **values):
    ctx = RequestContext(request_id, **values)
    token = _request_context.set(ctx)
    try:
        yield ctx
    finally:
        _request_context.reset(token)
