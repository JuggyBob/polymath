"""Small result cache."""


class ResultCache:
    def __init__(self):
        self._entries = {}

    def get(self, key, producer):
        if "value" in self._entries:
            return self._entries["value"]
        value = producer()
        self._entries["value"] = value
        return value

    def clear(self):
        self._entries.clear()
