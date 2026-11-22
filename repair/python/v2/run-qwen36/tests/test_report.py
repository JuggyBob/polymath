import unittest

from ledger import Ledger, Order
from ledger.report import expiring, slow_rank, summary


def sample_ledger():
    ledger = Ledger()
    ledger.add(Order("A", 10, "buy", 3, 100, note="Green Tea"))
    ledger.add(Order("B", 20, "sell", 2, 200, note="Straße"))
    ledger.add(Order("C", 30, "buy", 1, 300, note="Coffee"))
    return ledger


class ReportTests(unittest.TestCase):
    def test_summary_oldest_ts(self):
        self.assertEqual(summary(sample_ledger())["oldest_ts"], 10)

    def test_summary_empty(self):
        self.assertEqual(summary(Ledger())["oldest_ts"], None)

    def test_expiring_inside_window(self):
        ledger = sample_ledger()
        # ages at now=25: A=15, B=5, C=-5. Only B is in [0, 10].
        got = [o.order_id for o in expiring(ledger, now=25, window=10)]
        self.assertEqual(got, ["B"])

    def test_slow_rank_is_correct(self):
        ledger = sample_ledger()
        # Ranking is by notional (qty * price), not price:
        # B = 2*200 = 400, A = 3*100 = 300, C = 1*300 = 300.
        got = [o.order_id for o in slow_rank(ledger)]
        self.assertEqual(got, ["B", "A", "C"])


if __name__ == "__main__":
    unittest.main()
