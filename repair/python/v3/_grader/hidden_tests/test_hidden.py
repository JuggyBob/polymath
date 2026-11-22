"""Hidden verification suite for repair fixture v3.

Injected into a candidate copy only at grading time. Includes operation
sequences and seeded randomised inputs so hardcoded or single-call patches fail.
"""
import random
import re
import unittest

from scheduler import Job, Scheduler
from scheduler.metrics import by_priority, expiring, load, oldest, slow_score


def three():
    s = Scheduler()
    s.add(Job("A", 5, 10, 100, "alpha"))
    s.add(Job("B", 2, 20, 100, "beta"))
    s.add(Job("C", 9, 30, 100, "gamma"))
    return s


class HiddenCore(unittest.TestCase):
    def test_get_missing_raises(self):
        with self.assertRaises(KeyError):
            three().get("NOPE")

    def test_set_priority_missing_raises(self):
        with self.assertRaises(KeyError):
            three().set_priority("NOPE", 1)

    def test_cancel_missing_raises(self):
        with self.assertRaises(KeyError):
            three().cancel("NOPE")

    def test_cancel_returns_removed_job(self):
        s = three()
        job = s.cancel("B")
        self.assertEqual(job.job_id, "B")
        with self.assertRaises(KeyError):
            s.get("B")

    def test_pending_tiebreak_by_id(self):
        s = Scheduler()
        for name in ("Z", "A", "M"):
            s.add(Job(name, 1, 5, 100, "x"))
        self.assertEqual([j.job_id for j in s.pending(0)], ["A", "M", "Z"])

    def test_pending_multi_level_order(self):
        s = Scheduler()
        s.add(Job("D", 3, 1, 100, "x"))
        s.add(Job("C", 1, 9, 100, "x"))
        s.add(Job("B", 2, 2, 100, "x"))
        s.add(Job("A", 1, 9, 100, "x"))
        self.assertEqual([j.job_id for j in s.pending(0)], ["A", "C", "B", "D"])

    def test_next_job_invalidated_by_set_priority(self):
        s = Scheduler()
        s.add(Job("A", 5, 0, 100, "a"))
        self.assertEqual(s.next_job(0).job_id, "A")
        s.set_priority("A", 9)
        s.add(Job("B", 1, 0, 100, "b"))
        self.assertEqual(s.next_job(0).job_id, "B")

    def test_next_job_invalidated_by_cancel(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 100, "a"))
        s.add(Job("B", 2, 0, 100, "b"))
        self.assertEqual(s.next_job(0).job_id, "A")
        s.cancel("A")
        self.assertEqual(s.next_job(0).job_id, "B")

    def test_next_job_invalidated_by_expire(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 5, "a"))
        s.add(Job("B", 2, 0, 100, "b"))
        self.assertEqual(s.next_job(0).job_id, "A")
        s.expire(10)
        self.assertEqual(s.next_job(10).job_id, "B")

    def test_next_job_after_clear(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 100, "a"))
        self.assertEqual(s.next_job(0).job_id, "A")
        s.clear()
        s.add(Job("B", 1, 0, 100, "b"))
        self.assertEqual(s.next_job(0).job_id, "B")

    def test_clear_resets_index(self):
        s = three()
        s.clear()
        self.assertEqual(s.all_jobs(), [])
        with self.assertRaises(KeyError):
            s.get("A")

    def test_expire_skips_none_interleaved(self):
        s = Scheduler()
        for i in range(6):
            s.add(Job(f"E{i}", 1, 0, 5, "expired"))
        for i in range(3):
            s.add(Job(f"L{i}", 1, 0, 100, "live"))
        removed = s.expire(10)
        self.assertEqual(removed, ["E0", "E1", "E2", "E3", "E4", "E5"])
        self.assertEqual(len(s.pending(10)), 3)

    def test_expire_updates_index(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 5, "a"))
        s.expire(10)
        with self.assertRaises(KeyError):
            s.get("A")

    def test_ttl_missing_raises(self):
        with self.assertRaises(KeyError):
            three().ttl_remaining("NOPE", 0)

    def test_ttl_can_be_negative(self):
        s = Scheduler()
        s.add(Job("A", 1, 10, 5, "a"))
        self.assertEqual(s.ttl_remaining("A", 20), -5)

    def test_find_regex_search(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 100, "prefix-target-suffix"))
        self.assertEqual([j.job_id for j in s.find("target")], ["A"])

    def test_find_anchored_pattern_still_works(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 100, "target-suffix"))
        self.assertEqual([j.job_id for j in s.find("^target")], ["A"])

    def test_find_empty_matches_all(self):
        s = three()
        self.assertEqual(len(s.find("")), 3)

    def test_batch_zero(self):
        self.assertEqual(three().batch(0, 0), [])

    def test_batch_larger_than_available(self):
        self.assertEqual(len(three().batch(0, 50)), 3)

    def test_batch_after_pop(self):
        s = three()
        popped = s.pop(0)
        self.assertEqual(popped.job_id, "B")
        # B is now running, so pending order is A (priority 5), C (priority 9).
        self.assertEqual([j.job_id for j in s.batch(0, 2)], ["A", "C"])

    def test_snapshot_does_not_alias_index(self):
        s = three()
        snap = s.snapshot()
        snap["A"] = Job("X", 1, 0, 1, "x")
        self.assertEqual(s.get("A").job_id, "A")

    def test_sequence_add_cancel_add_pending(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 100, "a"))
        s.cancel("A")
        s.add(Job("A", 2, 10, 100, "a2"))
        self.assertEqual([j.job_id for j in s.pending(0)], ["A"])
        self.assertEqual(s.get("A").priority, 2)

    def test_sequence_pop_then_set_priority(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 100, "a"))
        s.add(Job("B", 2, 0, 100, "b"))
        s.pop(0)
        s.set_priority("B", 0)
        self.assertEqual(s.pending(0)[0].job_id, "B")
        self.assertEqual(s.pending(0)[0].priority, 0)

    def test_randomized_pending_order(self):
        rng = random.Random(19)
        s = Scheduler()
        expected = []
        for i in range(40):
            pr = rng.randint(0, 5)
            cr = rng.randint(0, 50)
            name = f"J{i:02d}"
            expected.append((pr, cr, name))
            s.add(Job(name, pr, cr, 1000, "x"))
        expected.sort()
        got = [j.job_id for j in s.pending(0)]
        self.assertEqual(got, [name for _, _, name in expected])

    def test_randomized_expire_all(self):
        rng = random.Random(7)
        s = Scheduler()
        expected = []
        for i in range(30):
            ttl = rng.choice([1, 5, 100])
            name = f"E{i:02d}"
            s.add(Job(name, 1, 0, ttl, "x"))
            if ttl < 10:
                expected.append(name)
        self.assertEqual(s.expire(10), sorted(expected))

    def test_randomized_batch_lengths(self):
        rng = random.Random(3)
        s = Scheduler()
        for i in range(20):
            s.add(Job(f"J{i:02d}", rng.randint(0, 3), i, 1000, "x"))
        for n in range(0, 6):
            self.assertEqual(len(s.batch(0, n)), min(n, 20))


class HiddenMetrics(unittest.TestCase):
    def test_expiring_boundary_inclusive(self):
        s = Scheduler()
        s.add(Job("A", 1, 10, 10, "a"))  # expires_at=20, now=10 -> age 10
        self.assertEqual([j.job_id for j in expiring(s, now=10, window=10)], ["A"])

    def test_expiring_ordered_by_expires_at(self):
        s = Scheduler()
        s.add(Job("Z", 1, 0, 30, "z"))
        s.add(Job("A", 1, 0, 10, "a"))
        self.assertEqual([j.job_id for j in expiring(s, now=0, window=50)], ["A", "Z"])

    def test_expiring_excludes_future(self):
        s = Scheduler()
        s.add(Job("A", 1, 50, 10, "a"))
        self.assertEqual(expiring(s, now=10, window=100), [])

    def test_expiring_excludes_running(self):
        s = three()
        s.pop(0)
        self.assertEqual(expiring(s, now=0, window=200), [])

    def test_expiring_tie_break_by_id(self):
        s = Scheduler()
        s.add(Job("B", 1, 0, 10, "b"))
        s.add(Job("A", 1, 0, 10, "a"))
        self.assertEqual([j.job_id for j in expiring(s, now=0, window=10)], ["A", "B"])

    def test_oldest_tie_break_by_id(self):
        s = Scheduler()
        for name in ("Z", "A", "M"):
            s.add(Job(name, 1, 5, 100, "x"))
        self.assertEqual(oldest(s, 0).job_id, "A")

    def test_by_priority_group_order(self):
        s = Scheduler()
        s.add(Job("A", 3, 0, 100, "a"))
        s.add(Job("B", 1, 0, 100, "b"))
        self.assertEqual(list(by_priority(s, 0)), [3, 1])

    def test_by_priority_within_group_insertion_order(self):
        s = Scheduler()
        s.add(Job("Z", 1, 0, 100, "z"))
        s.add(Job("A", 1, 0, 100, "a"))
        self.assertEqual(by_priority(s, 0)[1], ["Z", "A"])

    def test_slow_score_tie_break(self):
        s = Scheduler()
        s.add(Job("B", 1, 0, 10, "b"))
        s.add(Job("A", 1, 0, 10, "a"))
        self.assertEqual([j.job_id for j in slow_score(s)], ["A", "B"])

    def test_load_after_expire(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 5, "a"))
        s.expire(10)
        self.assertEqual(load(s, 10), 0)


if __name__ == "__main__":
    unittest.main()
