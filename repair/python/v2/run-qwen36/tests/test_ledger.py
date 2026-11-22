import unittest

from ledger import Ledger, Order


def sample_ledger():
    ledger = Ledger()
    ledger.add(Order("A", 10, "buy", 3, 100, note="Green Tea"))
    ledger.add(Order("B", 20, "sell", 2, 200, note="Straße"))
    ledger.add(Order("C", 30, "buy", 1, 300, note="Coffee"))
    return ledger


class LedgerTests(unittest.TestCase):
    def test_add_and_get(self):
        ledger = Ledger()
        ledger.add(Order("A-1", 1, "buy", 1, 199, note="Widget"))
        self.assertEqual(ledger.get("A-1").note, "Widget")

    def test_duplicate_id_rejected(self):
        ledger = Ledger()
        ledger.add(Order("A-1", 1, "buy", 1, 199))
        with self.assertRaises(ValueError):
            ledger.add(Order("A-1", 2, "sell", 1, 250))

    def test_notional_property(self):
        self.assertEqual(Order("X", 1, "buy", 3, 100).notional_cents, 300)

    def test_total_quantity_matters(self):
        ledger = sample_ledger()
        # 3*100 + 2*200 + 1*300 = 1000, not 600.
        self.assertEqual(ledger.total_notional_cents(), 1000)

    def test_total_filtered_by_status(self):
        ledger = sample_ledger()
        # Filter is by status, not by side. All sample orders are "open".
        self.assertEqual(ledger.total_notional_cents("open"), 1000)
        self.assertEqual(ledger.total_notional_cents("buy"), 0)

    def test_open_plain(self):
        ledger = sample_ledger()
        self.assertEqual([o.order_id for o in ledger.open_orders()], ["A", "B", "C"])

    def test_open_partial_status(self):
        ledger = Ledger()
        ledger.add(Order("A", 1, "buy", 1, 100, status="open_partial"))
        ledger.add(Order("B", 2, "buy", 1, 100, status="filled"))
        self.assertEqual([o.order_id for o in ledger.open_orders()], ["A"])

    def test_fill_and_idempotent(self):
        ledger = sample_ledger()
        ledger.fill("A")
        self.assertEqual(ledger.get("A").status, "filled")
        ledger.fill("A")
        self.assertEqual(ledger.get("A").status, "filled")

    def test_cancel_filled_raises(self):
        ledger = sample_ledger()
        ledger.fill("A")
        with self.assertRaises(ValueError):
            ledger.cancel("A")

    def test_search_ascii(self):
        ledger = sample_ledger()
        self.assertEqual([o.order_id for o in ledger.search("tea")], ["A"])

    def test_search_casefold(self):
        ledger = sample_ledger()
        self.assertEqual([o.order_id for o in ledger.search("STRASSE")], ["B"])

    def test_slice_basic(self):
        ledger = sample_ledger()
        got = [o.order_id for o in ledger.slice_orders(1, 3)]
        self.assertEqual(got, ["B", "C"])

    def test_oldest_two(self):
        ledger = sample_ledger()
        self.assertEqual([o.order_id for o in ledger.oldest(2)], ["A", "B"])

    def test_group_first_seen_order(self):
        ledger = Ledger()
        ledger.add(Order("A", 1, "buy", 1, 100, status="open"))
        ledger.add(Order("B", 2, "buy", 1, 100, status="filled"))
        from ledger.report import group_by_status
        self.assertEqual(list(group_by_status(ledger)), ["open", "filled"])

    def test_summary_count(self):
        from ledger.report import summary
        s = summary(sample_ledger())
        self.assertEqual(s["count"], 3)
        self.assertEqual(s["open"], 3)


if __name__ == "__main__":
    unittest.main()
