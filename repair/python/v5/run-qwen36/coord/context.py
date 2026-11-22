"""Request-scoped context for the coordinator."""
import contextvars
from contextlib import contextmanager

_current_var = contextvars.ContextVar("_current", default=None)


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
    return _current_var.get()


@contextmanager
def bind(request_id, **values):
    token = _current_var.set(RequestContext(request_id, **values))
    try:
        yield
    except BaseException:
        raise
    finally:
        _current_var.reset(token)
