import unittest

from inventory.models import Item
from inventory.report import total_value_cents
from inventory.store import Store


def store_with(n):
    store = Store()
    for i in range(1, n + 1):
        store.add(Item(f"S{i}", f"Item {i}", "misc", 100))
    return store


class HiddenPagination(unittest.TestCase):
    def test_last_partial_page(self):
        self.assertEqual([i.sku for i in store_with(7).list_page(3, 3)], ["S7"])

    def test_past_end_is_empty(self):
        self.assertEqual(store_with(7).list_page(4, 3), [])

    def test_invalid_page_and_size(self):
        store = store_with(7)
        with self.assertRaises(ValueError):
            store.list_page(0, 3)
        with self.assertRaises(ValueError):
            store.list_page(1, 0)

    def test_empty_store(self):
        self.assertEqual(Store().list_page(1, 3), [])


class HiddenSearch(unittest.TestCase):
    def test_unicode_casefold(self):
        store = Store()
        store.add(Item("X", "Straße", "p", 1))
        self.assertEqual([i.sku for i in store.search("STRASSE")], ["X"])

    def test_empty_query_matches_all(self):
        store = store_with(3)
        self.assertEqual(len(store.search("")), 3)


class HiddenTotals(unittest.TestCase):
    def test_large_exact_sum(self):
        items = [Item("A", "a", "x", 199, 3), Item("B", "b", "x", 250, 2)]
        self.assertEqual(total_value_cents(items), 1097)

    def test_quantity_matters(self):
        items = [Item("A", "a", "x", 100, 4)]
        self.assertEqual(total_value_cents(items), 400)


if __name__ == "__main__":
    unittest.main()
