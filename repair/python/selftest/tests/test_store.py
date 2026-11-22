import unittest

from inventory.models import Item
from inventory.store import Store


def sample_store():
    store = Store()
    for i in range(1, 8):
        store.add(Item(f"SKU-{i}", f"Item {i}", "misc", 100 * i))
    return store


class StoreTests(unittest.TestCase):
    def test_add_and_get(self):
        store = Store()
        store.add(Item("A-1", "Widget", "tools", 199))
        self.assertEqual(store.get("A-1").name, "Widget")

    def test_duplicate_sku_rejected(self):
        store = Store()
        store.add(Item("A-1", "Widget", "tools", 199))
        with self.assertRaises(ValueError):
            store.add(Item("A-1", "Other", "tools", 250))

    def test_list_page_first_page(self):
        store = sample_store()
        page = store.list_page(1, 3)
        self.assertEqual([item.sku for item in page], ["SKU-1", "SKU-2", "SKU-3"])

    def test_list_page_second_page(self):
        store = sample_store()
        page = store.list_page(2, 3)
        self.assertEqual([item.sku for item in page], ["SKU-4", "SKU-5", "SKU-6"])


if __name__ == "__main__":
    unittest.main()
