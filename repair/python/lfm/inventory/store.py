"""In-memory inventory store."""

from .models import Item


class Store:
    def __init__(self):
        self._items = []
        self._by_sku = {}

    def add(self, item: Item) -> None:
        if item.sku in self._by_sku:
            raise ValueError(f"duplicate sku: {item.sku}")
        self._items.append(item)
        self._by_sku[item.sku] = item

    def get(self, sku: str) -> Item:
        return self._by_sku[sku]

    def all(self):
        return list(self._items)

    def list_page(self, page: int, size: int = 3):
        if page < 1:
            raise ValueError("page must be >= 1")
        if size < 1:
            raise ValueError("size must be >= 1")
        start = (page - 1) * size
        return self._items[start:start + size]

    def search(self, query: str):
        return [item for item in self._items if query.lower() in item.name.lower()]
