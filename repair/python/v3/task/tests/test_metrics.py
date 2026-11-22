import unittest

from scheduler import Job, Scheduler
from scheduler.metrics import by_priority, expiring, load, oldest, slow_score


def sample():
    s = Scheduler()
    s.add(Job("A", 1, 20, 100, "a"))
    s.add(Job("B", 1, 10, 100, "b"))
    s.add(Job("C", 1, 30, 100, "c"))
    return s


class MetricsTests(unittest.TestCase):
    def test_load(self):
        self.assertEqual(load(sample(), now=0), 3)

    def test_oldest(self):
        self.assertEqual(oldest(sample(), now=0).job_id, "B")

    def test_oldest_empty(self):
        self.assertIsNone(oldest(Scheduler(), now=0))

    def test_expiring_inside_window(self):
        s = Scheduler()
        s.add(Job("A", 1, 10, 20, "a"))  # expires at 30, age from now=25 is 5
        got = [j.job_id for j in expiring(s, now=25, window=10)]
        self.assertEqual(got, ["A"])

    def test_by_priority_single_group(self):
        got = by_priority(sample(), now=0)
        self.assertEqual(list(got), [1])
        self.assertEqual(got[1], ["A", "B", "C"])

    def test_slow_score_is_correct(self):
        # Ranking by -ttl: B (40) then A (20).
        s = Scheduler()
        s.add(Job("A", 1, 0, 20, "a"))
        s.add(Job("B", 1, 0, 40, "b"))
        self.assertEqual([j.job_id for j in slow_score(s)], ["B", "A"])


if __name__ == "__main__":
    unittest.main()
