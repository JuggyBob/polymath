"""Small value cache and descriptor for the coordinator."""
import weakref


class WeakCache:
    """Cache values by key."""

    def __init__(self):
        self._data = {}  # weakref(key) -> value

    def get(self, key, producer):
        ref = weakref.ref(key)
        if ref not in self._data:
            self._data[ref] = producer()
        return self._data[ref]

    def clear(self):
        self._data.clear()

    def __contains__(self, key):
        return weakref.ref(key) in self._data

    def __len__(self):
        return len(self._data)


class cached:
    """Remember a computed value for an attribute."""

    def __init__(self, fn):
        self.fn = fn
        self.name = "value"

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            return instance.__dict__[self.name]
        except KeyError:
            pass
        value = self.fn(instance)
        instance.__dict__[self.name] = value
        return value
