import unittest

from telemetry import Event, EventLog
from telemetry.cache import ResultCache
from telemetry.context import paused
from telemetry.format import format_summary
from telemetry.itertools_helpers import iter_kinds, make_filter, traced
from telemetry.metrics import load, rate, rolling_sum, slow_rank, top_kinds


def sample():
    log = EventLog("demo")
    log.append(Event("A", 10, "cpu", 100))
    log.append(Event("B", 20, "mem", 200))
    log.append(Event("C", 30, "cpu", 300))
    return log


class LogTests(unittest.TestCase):
    def test_append_get(self):
        self.assertEqual(sample().get("B").value, 200)

    def test_duplicate(self):
        with self.assertRaises(ValueError):
            sample().append(Event("A", 99, "cpu", 1))

    def test_missing(self):
        with self.assertRaises(KeyError):
            sample().get("NOPE")

    def test_all_is_copy(self):
        log = sample()
        log.all_events().clear()
        self.assertEqual(len(log.all_events()), 3)

    def test_by_kind(self):
        self.assertEqual([e.event_id for e in sample().by_kind("cpu")], ["A", "C"])

    def test_window_simple(self):
        self.assertEqual([e.event_id for e in sample().window(5, 35)], ["A", "B", "C"])

    def test_window_empty(self):
        self.assertEqual(sample().window(100, 200), [])

    def test_prune_one(self):
        log = EventLog()
        log.append(Event("A", 1, "cpu", 1))
        log.append(Event("B", 5, "cpu", 2))
        self.assertEqual(log.prune(5), ["A"])
        self.assertEqual(len(log.all_events()), 1)

    def test_latest_unique_ts(self):
        self.assertEqual([e.event_id for e in sample().latest(2)], ["C", "B"])

    def test_latest_zero(self):
        self.assertEqual(sample().latest(0), [])

    def test_latest_negative(self):
        with self.assertRaises(ValueError):
            sample().latest(-1)

    def test_total(self):
        self.assertEqual(sample().total(), 600)

    def test_snapshot_copy(self):
        log = sample()
        log.snapshot().clear()
        self.assertEqual(len(log.all_events()), 3)

    def test_clear(self):
        log = sample()
        log.clear()
        self.assertEqual(log.all_events(), [])

    def test_event_equality_same_id(self):
        a = Event("A", 1, "cpu", 1)
        b = Event("A", 2, "mem", 9)
        self.assertEqual(a, b)


class MetricsTests(unittest.TestCase):
    def test_load(self):
        self.assertEqual(load(sample()), 3)

    def test_rate_simple(self):
        self.assertAlmostEqual(rate(sample(), 5, 35), 3 / 30)

    def test_rate_bad(self):
        with self.assertRaises(ValueError):
            rate(sample(), 10, 10)

    def test_rolling_sum_simple(self):
        self.assertEqual(rolling_sum(sample(), 5, 35), 600)

    def test_top_kinds_no_ties(self):
        self.assertEqual(top_kinds(sample()), [("cpu", 400), ("mem", 200)])

    def test_top_kinds_negative(self):
        with self.assertRaises(ValueError):
            top_kinds(sample(), -1)

    def test_slow_rank_small(self):
        self.assertEqual([e.event_id for e in slow_rank(sample())], ["C", "B", "A"])

    def test_format(self):
        self.assertEqual(format_summary(sample()), "3 events, total 600")


class HelperTests(unittest.TestCase):
    def test_iter_kinds_once(self):
        self.assertEqual(list(iter_kinds(sample())), ["cpu", "mem"])

    def test_traced_returns_value(self):
        @traced
        def add(a, b):
            return a + b
        self.assertEqual(add(2, 3), 5)

    def test_make_filter_exact(self):
        f = make_filter("cpu")
        self.assertTrue(f(Event("A", 1, "cpu", 1)))
        self.assertFalse(f(Event("B", 2, "mem", 1)))

    def test_paused_suppresses_append(self):
        log = EventLog()
        with paused(log):
            log.append(Event("A", 1, "cpu", 1))
        self.assertEqual(log.all_events(), [])

    def test_cache_single_key(self):
        c = ResultCache()
        self.assertEqual(c.get("x", lambda: 7), 7)
        self.assertEqual(c.get("x", lambda: 99), 7)


if __name__ == "__main__":
    unittest.main()
