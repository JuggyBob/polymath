"""Hidden suite for repair fixture v4-hard.

Injected only at grading time. Names are prefixed to avoid collisions with the
visible suite's method names.
"""
import random
import time
import unittest

from telemetry import Event, EventLog
from telemetry.cache import ResultCache
from telemetry.context import paused
from telemetry.format import format_summary
from telemetry.itertools_helpers import iter_kinds, make_filter, traced
from telemetry.metrics import load, rate, rolling_sum, slow_rank, top_kinds


def three():
    log = EventLog()
    log.append(Event("A", 10, "cpu", 100))
    log.append(Event("B", 20, "mem", 200))
    log.append(Event("C", 30, "cpu", 300))
    return log


class HiddenBoundaries(unittest.TestCase):
    def test_h_window_end_exclusive(self):
        self.assertEqual([e.event_id for e in three().window(10, 20)], ["A"])

    def test_h_window_start_inclusive(self):
        self.assertEqual([e.event_id for e in three().window(20, 31)], ["B", "C"])

    def test_h_window_both_boundaries(self):
        self.assertEqual([e.event_id for e in three().window(10, 30)], ["A", "B"])

    def test_h_window_tie_id_descending(self):
        log = EventLog()
        log.append(Event("A", 10, "cpu", 1))
        log.append(Event("B", 10, "cpu", 2))
        self.assertEqual([e.event_id for e in log.window(0, 20)], ["B", "A"])

    def test_h_rolling_sum_end_exclusive(self):
        self.assertEqual(rolling_sum(three(), 10, 20), 100)

    def test_h_rolling_sum_matches_window(self):
        log = three()
        got = [e.value for e in log.window(10, 20)]
        self.assertEqual(rolling_sum(log, 10, 20), sum(got))

    def test_h_window_reversed(self):
        self.assertEqual(three().window(30, 10), [])

    def test_h_randomized_window(self):
        rng = random.Random(19)
        log = EventLog()
        rows = []
        for i in range(30):
            ts = rng.randint(0, 3)
            name = f"E{i:02d}"
            log.append(Event(name, ts, "cpu", 1))
            rows.append((ts, name))
        rows.sort(key=lambda r: (-r[0], r[1]))
        self.assertEqual([e.event_id for e in log.window(0, 10)],
                         [n for _, n in reversed(rows)])


class HiddenTies(unittest.TestCase):
    def test_h_latest_tie_desc(self):
        log = EventLog()
        log.append(Event("A", 5, "cpu", 1))
        log.append(Event("B", 5, "cpu", 2))
        self.assertEqual([e.event_id for e in log.latest(2)], ["B", "A"])

    def test_h_top_kinds_tie_name(self):
        log = EventLog()
        log.append(Event("A", 1, "zeta", 5))
        log.append(Event("B", 2, "alpha", 5))
        self.assertEqual(top_kinds(log), [("alpha", 5), ("zeta", 5)])

    def test_h_slow_rank_tie_id(self):
        log = EventLog()
        log.append(Event("B", 1, "cpu", 10))
        log.append(Event("A", 2, "cpu", 10))
        self.assertEqual([e.event_id for e in slow_rank(log)], ["A", "B"])

    def test_h_randomized_latest(self):
        rng = random.Random(3)
        log = EventLog()
        rows = []
        for i in range(20):
            ts = rng.randint(0, 2)
            name = f"E{i:02d}"
            log.append(Event(name, ts, "cpu", 1))
            rows.append((ts, name))
        rows.sort(reverse=True)
        self.assertEqual([e.event_id for e in log.latest(20)],
                         [n for _, n in rows])

    def test_h_randomized_top_kinds(self):
        rng = random.Random(7)
        log = EventLog()
        totals = {}
        for i in range(40):
            kind = rng.choice(["delta", "beta", "gamma", "alpha"])
            value = rng.choice([1, 2, 3])
            log.append(Event(f"E{i:02d}", i, kind, value))
            totals[kind] = totals.get(kind, 0) + value
        want = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
        self.assertEqual(top_kinds(log, 3), want)


class HiddenCache(unittest.TestCase):
    def test_h_append_invalidates(self):
        log = EventLog()
        log.append(Event("A", 1, "cpu", 1))
        self.assertEqual(log.latest(1)[0].event_id, "A")
        log.append(Event("B", 2, "cpu", 1))
        self.assertEqual(log.latest(1)[0].event_id, "B")

    def test_h_prune_invalidates(self):
        log = EventLog()
        log.append(Event("A", 1, "cpu", 1))
        log.append(Event("B", 5, "cpu", 1))
        self.assertEqual(log.latest(1)[0].event_id, "B")
        log.prune(6)
        self.assertEqual(log.latest(1), [])

    def test_h_clear_invalidates(self):
        log = three()
        self.assertEqual(log.latest(1)[0].event_id, "C")
        log.clear()
        self.assertEqual(log.latest(1), [])

    def test_h_rate_read_only_latest(self):
        log = three()
        rate(log, 0, 100)
        self.assertEqual([e.event_id for e in log.latest(3)], ["C", "B", "A"])

    def test_h_rate_read_only_window(self):
        log = three()
        rate(log, 0, 100)
        self.assertEqual([e.event_id for e in log.window(0, 100)], ["A", "B", "C"])

    def test_h_top_kinds_read_only(self):
        log = three()
        top_kinds(log)
        self.assertEqual(log.total(), 600)

    def test_h_report_sequence(self):
        log = three()
        self.assertEqual(rolling_sum(log, 0, 100), 600)
        self.assertEqual(log.total(), 600)
        self.assertEqual([e.event_id for e in log.latest(2)], ["C", "B"])


class HiddenPrune(unittest.TestCase):
    def test_h_prune_no_skip(self):
        log = EventLog()
        for i in range(6):
            log.append(Event(f"E{i}", 1, "cpu", 1))
        self.assertEqual(log.prune(5), [f"E{i}" for i in range(6)])

    def test_h_prune_index(self):
        log = three()
        log.prune(20)
        with self.assertRaises(KeyError):
            log.get("A")

    def test_h_prune_snapshot(self):
        log = three()
        log.prune(20)
        self.assertEqual(sorted(log.snapshot()), ["B", "C"])

    def test_h_prune_by_kind(self):
        log = three()
        log.prune(20)
        self.assertEqual([e.event_id for e in log.by_kind("cpu")], ["C"])

    def test_h_prune_total(self):
        log = three()
        log.prune(20)
        self.assertEqual(log.total(), 500)


class HiddenEvent(unittest.TestCase):
    def test_h_equal_events_hash_equal(self):
        a = Event("A", 1, "cpu", 1)
        b = Event("A", 2, "mem", 9)
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertEqual(len({a, b}), 1)

    def test_h_hash_stable_after_tag_change(self):
        a = Event("A", 1, "cpu", 1)
        h = hash(a)
        a.tags.append("new")
        self.assertEqual(hash(a), h)

    def test_h_dict_lookup_by_equal_id(self):
        a = Event("A", 1, "cpu", 1)
        d = {a: 5}
        b = Event("A", 9, "gpu", 99)
        self.assertEqual(d[b], 5)

    def test_h_snapshot_independent_events(self):
        log = three()
        snap = log.snapshot()
        snap["A"].tags.append("changed")
        self.assertEqual(log.get("A").tags, [])


class HiddenHelpers(unittest.TestCase):
    def test_h_iter_kinds_twice(self):
        log = three()
        self.assertEqual(list(iter_kinds(log)), ["cpu", "mem"])
        self.assertEqual(list(iter_kinds(log)), ["cpu", "mem"])

    def test_h_iter_kinds_after_append(self):
        log = three()
        list(iter_kinds(log))
        log.append(Event("D", 40, "disk", 1))
        self.assertEqual(list(iter_kinds(log)), ["cpu", "mem", "disk"])

    def test_h_traced_preserves_name(self):
        @traced
        def my_fn(a):
            return a
        self.assertEqual(my_fn.__name__, "my_fn")

    def test_h_traced_preserves_doc(self):
        @traced
        def doc_fn():
            "docs here"
        self.assertEqual(doc_fn.__doc__, "docs here")

    def test_h_make_filter_exact(self):
        f = make_filter("cpu")
        self.assertFalse(f(Event("A", 1, "cpu_long", 1)))

    def test_h_paused_restores_after_normal(self):
        log = EventLog()
        with paused(log):
            log.append(Event("A", 1, "cpu", 1))
        log.append(Event("B", 2, "cpu", 2))
        self.assertEqual([e.event_id for e in log.all_events()], ["B"])

    def test_h_paused_restores_after_exception(self):
        log = EventLog()
        try:
            with paused(log):
                raise RuntimeError("boom")
        except RuntimeError:
            pass
        log.append(Event("B", 1, "cpu", 1))
        self.assertEqual([e.event_id for e in log.all_events()], ["B"])

    def test_h_cache_distinct_keys(self):
        c = ResultCache()
        self.assertEqual(c.get("x", lambda: 1), 1)
        self.assertEqual(c.get("y", lambda: 2), 2)

    def test_h_cache_clear(self):
        c = ResultCache()
        c.get("x", lambda: 1)
        c.clear()
        self.assertEqual(c.get("x", lambda: 9), 9)


class HiddenPerformance(unittest.TestCase):
    def test_h_slow_rank_10k(self):
        log = EventLog()
        rng = random.Random(11)
        for i in range(10000):
            log.append(Event(f"E{i:05d}", i, "cpu", rng.randint(0, 1000)))
        t0 = time.monotonic()
        ranked = slow_rank(log)
        elapsed = time.monotonic() - t0
        self.assertLess(elapsed, 2.0, f"slow_rank took {elapsed:.2f}s")
        keys = [(-e.value, e.event_id) for e in ranked]
        self.assertEqual(keys, sorted(keys))


class HiddenFormat(unittest.TestCase):
    def test_h_format_summary_unchanged(self):
        log = three()
        self.assertEqual(format_summary(log), "3 events, total 600")

    def test_h_format_empty(self):
        self.assertEqual(format_summary(EventLog()), "0 events, total 0")

    def test_h_load_after_reporting(self):
        log = three()
        rate(log, 0, 100)
        self.assertEqual(load(log), 3)


if __name__ == "__main__":
    unittest.main()
