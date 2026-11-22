"""Small value cache and descriptor for the coordinator."""
import weakref


class WeakCache:
    """Cache values by key."""

    def __init__(self):
        self._values = {}

    def get(self, key, producer):
        ref = weakref.ref(key)
        if ref not in self._values:
            self._values[ref] = producer()
        elif ref() is None:
            del self._values[ref]
            self._values[ref] = producer()
        return self._values[ref]

    def clear(self):
        self._values.clear()

    def __contains__(self, key):
        return weakref.ref(key) in self._values

    def __len__(self):
        return len(self._values)


class cached:
    """Remember a computed value for an attribute."""

    def __init__(self, fn):
        self.fn = fn
        self.name = None
        self._value = None
        self._done = False

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if not self._done:
            self._value = self.fn(instance)
            self._done = True
        instance.__dict__[self.name] = self._value
        return self._value
