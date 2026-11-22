import unittest

from inventory.models import Item
from inventory.report import by_category, total_value_cents


class ReportTests(unittest.TestCase):
    def test_total_empty(self):
        self.assertEqual(total_value_cents([]), 0)

    def test_total_exact_cents(self):
        items = [Item("A", "a", "x", 199), Item("B", "b", "x", 250)]
        self.assertEqual(total_value_cents(items), 449)

    def test_by_category(self):
        items = [Item("A", "a", "x", 100, 2), Item("B", "b", "y", 50, 3)]
        self.assertEqual(by_category(items), {"x": 200, "y": 150})


if __name__ == "__main__":
    unittest.main()
