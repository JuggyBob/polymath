"""Small value cache and descriptor for the coordinator."""
import weakref


class WeakCache:
    """Cache values by key."""

    def __init__(self):
        self._weak = weakref.WeakKeyDictionary()
        self._strong = {}
        self._strong_keys = {}
        self._finalizers = {}

    def get(self, key, producer):
        # Try weak-key dict first (supports equality-based lookup + weak refs)
        if key in self._weak:
            return self._weak[key]
        # Check if an equal key already exists in strong dict
        for slot, existing_key in list(self._strong_keys.items()):
            if existing_key == key:
                return self._strong[slot]
        # Store value
        slot = id(key)
        self._strong[slot] = producer()
        self._strong_keys[slot] = key
        try:
            fin = weakref.finalize(key, self._cleanup, slot)
            self._finalizers[slot] = fin
        except TypeError:
            pass
        return self._strong[slot]

    def _cleanup(self, slot):
        self._strong.pop(slot, None)
        self._strong_keys.pop(slot, None)
        self._finalizers.pop(slot, None)

    def clear(self):
        self._weak.clear()
        self._strong.clear()
        self._strong_keys.clear()
        self._finalizers.clear()

    def __contains__(self, key):
        return key in self._weak or id(key) in self._strong

    def __len__(self):
        return len(self._weak) + len(self._strong)


class cached:
    """Remember a computed value for an attribute."""

    def __init__(self, fn):
        self.fn = fn
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.name not in instance.__dict__:
            instance.__dict__[self.name] = self.fn(instance)
        return instance.__dict__[self.name]
