"""Request-scoped context for the coordinator."""
import contextvars
from contextlib import contextmanager

_current_ctx: contextvars.ContextVar = contextvars.ContextVar("_current_ctx", default=None)


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
    return _current_ctx.get()


@contextmanager
def bind(request_id, **values):
    token = _current_ctx.set(RequestContext(request_id, **values))
    try:
        yield
    except BaseException:
        raise
    finally:
        _current_ctx.reset(token)
