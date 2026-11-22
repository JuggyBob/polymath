import unittest

from inventory.models import Item
from inventory.store import Store


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.store.add(Item("A", "Café Latte", "drinks", 450))
        self.store.add(Item("B", "Straße", "places", 100))
        self.store.add(Item("C", "Green Tea", "drinks", 300))

    def test_search_lowercase(self):
        self.assertEqual([i.sku for i in self.store.search("tea")], ["C"])

    def test_search_case_insensitive(self):
        self.assertEqual([i.sku for i in self.store.search("CAFÉ")], ["A"])

    def test_search_no_match(self):
        self.assertEqual(self.store.search("zzz"), [])


if __name__ == "__main__":
    unittest.main()
