"""Small result cache."""


class ResultCache:
    def __init__(self):
        self._entries = {}

    def get(self, key, producer):
        if key in self._entries:
            return self._entries[key]
        value = producer()
        self._entries[key] = value
        return value

    def clear(self):
        self._entries.clear()
