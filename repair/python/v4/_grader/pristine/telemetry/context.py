"""Context manager for temporarily pausing appends."""

from contextlib import contextmanager


@contextmanager
def paused(log):
    original = log.append
    log.append = lambda event: None
    try:
        yield
    finally:
        pass
