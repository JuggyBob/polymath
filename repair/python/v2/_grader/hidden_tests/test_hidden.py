"""Hidden verification suite for repair fixture v2.

These files are NOT part of the agent's workspace. The scorer copies them into
a temporary copy of the candidate at grading time.
"""
import unittest

from ledger import Ledger, Order
from ledger.report import expiring, group_by_status, slow_rank, summary


def sample_ledger():
    ledger = Ledger()
    ledger.add(Order("A", 10, "buy", 3, 100, note="Green Tea"))
    ledger.add(Order("B", 20, "sell", 2, 200, note="Straße"))
    ledger.add(Order("C", 30, "buy", 1, 300, note="Coffee"))
    return ledger


class HiddenLedgerTests(unittest.TestCase):
    def test_get_missing_raises_key_error(self):
        with self.assertRaises(KeyError):
            sample_ledger().get("NOPE")

    def test_all_is_a_copy(self):
        ledger = sample_ledger()
        snapshot = ledger.all()
        snapshot.clear()
        self.assertEqual(len(ledger.all()), 3)

    def test_total_exact_large(self):
        ledger = Ledger()
        ledger.add(Order("A", 1, "buy", 10**6, 10**12))
        self.assertEqual(ledger.total_notional_cents(), 10**18)

    def test_total_filter_is_status_not_side(self):
        ledger = Ledger()
        ledger.add(Order("A", 1, "buy", 2, 100, status="cancelled"))
        ledger.add(Order("B", 2, "sell", 1, 500, status="open"))
        # Filtering by status works; "buy" is a side and must match nothing.
        self.assertEqual(ledger.total_notional_cents("cancelled"), 200)
        self.assertEqual(ledger.total_notional_cents("buy"), 0)

    def test_total_empty(self):
        self.assertEqual(Ledger().total_notional_cents(), 0)

    def test_total_status_filter_no_match(self):
        self.assertEqual(sample_ledger().total_notional_cents("missing"), 0)

    def test_slice_negative_indices(self):
        ledger = sample_ledger()
        got = [o.order_id for o in ledger.slice_orders(-2, 3)]
        self.assertEqual(got, ["B", "C"])

    def test_slice_out_of_range_clamps(self):
        ledger = sample_ledger()
        got = [o.order_id for o in ledger.slice_orders(2, 99)]
        self.assertEqual(got, ["C"])

    def test_slice_end_is_exclusive(self):
        # end=1 must return exactly one order; end+1 would return two.
        got = [o.order_id for o in sample_ledger().slice_orders(0, 1)]
        self.assertEqual(got, ["A"])

    def test_slice_reversed_is_empty(self):
        self.assertEqual(sample_ledger().slice_orders(2, 1), [])

    def test_search_empty_matches_all(self):
        self.assertEqual(len(sample_ledger().search("")), 3)

    def test_search_unicode_casefold(self):
        ledger = sample_ledger()
        self.assertEqual([o.order_id for o in ledger.search("STRASSE")], ["B"])

    def test_oldest_ties_broken_by_id(self):
        ledger = Ledger()
        ledger.add(Order("Z", 5, "buy", 1, 100))
        ledger.add(Order("A", 5, "buy", 1, 100))
        ledger.add(Order("M", 5, "buy", 1, 100))
        self.assertEqual([o.order_id for o in ledger.oldest(3)], ["A", "M", "Z"])

    def test_oldest_negative_raises(self):
        with self.assertRaises(ValueError):
            sample_ledger().oldest(-1)

    def test_oldest_zero_is_empty(self):
        self.assertEqual(sample_ledger().oldest(0), [])

    def test_cancel_open_succeeds(self):
        ledger = sample_ledger()
        ledger.cancel("A")
        self.assertEqual(ledger.get("A").status, "cancelled")

    def test_fill_missing_raises(self):
        with self.assertRaises(KeyError):
            sample_ledger().fill("NOPE")


class HiddenReportTests(unittest.TestCase):
    def test_expiring_boundary_inclusive(self):
        ledger = Ledger()
        ledger.add(Order("A", 10, "buy", 1, 100, status="open"))
        # age at now=20 is exactly 10, which must be included.
        got = [o.order_id for o in expiring(ledger, now=20, window=10)]
        self.assertEqual(got, ["A"])

    def test_expiring_excludes_filled(self):
        ledger = Ledger()
        ledger.add(Order("A", 10, "buy", 1, 100, status="filled"))
        self.assertEqual(expiring(ledger, now=15, window=10), [])

    def test_expiring_excludes_future(self):
        ledger = Ledger()
        ledger.add(Order("A", 30, "buy", 1, 100, status="open"))
        self.assertEqual(expiring(ledger, now=20, window=10), [])

    def test_expiring_ordered_by_ts(self):
        ledger = Ledger()
        ledger.add(Order("B", 20, "buy", 1, 100, status="open"))
        ledger.add(Order("A", 10, "buy", 1, 100, status="open_partial"))
        got = [o.order_id for o in expiring(ledger, now=25, window=20)]
        self.assertEqual(got, ["A", "B"])

    def test_group_insertion_order_within_group(self):
        ledger = Ledger()
        ledger.add(Order("Z", 1, "buy", 1, 100, status="open"))
        ledger.add(Order("A", 2, "buy", 1, 100, status="open"))
        self.assertEqual(group_by_status(ledger)["open"], ["Z", "A"])

    def test_summary_notional_uses_quantity(self):
        s = summary(sample_ledger())
        self.assertEqual(s["notional"], 1000)

    def test_slow_rank_uses_notional(self):
        # Price order would be B, A; notional order is A (500), B (300).
        ledger = Ledger()
        ledger.add(Order("A", 1, "buy", 5, 100))
        ledger.add(Order("B", 2, "buy", 1, 300))
        self.assertEqual([o.order_id for o in slow_rank(ledger)], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
