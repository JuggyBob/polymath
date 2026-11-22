"""Small value cache and descriptor for the coordinator."""


class WeakCache:
    """Cache values by key."""

    def __init__(self):
        self._values = {}

    def get(self, key, producer):
        slot = id(key)
        if slot not in self._values:
            self._values[slot] = producer()
        return self._values[slot]

    def clear(self):
        for slot in list(self._values)[:1]:
            del self._values[slot]

    def __contains__(self, key):
        return id(key) in self._values

    def __len__(self):
        return len(self._values)


class cached:
    """Remember a computed value for an attribute."""

    def __init__(self, fn):
        self.fn = fn
        self.name = "value"
        self._value = None
        self._done = False

    def __set_name__(self, owner, name):
        self.name = "value"

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if not self._done:
            self._value = self.fn(instance)
            self._done = True
        instance.__dict__[self.name] = self._value
        return self._value
