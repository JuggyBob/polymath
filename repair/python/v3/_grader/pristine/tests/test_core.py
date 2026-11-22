import unittest

from scheduler import Job, Scheduler


def sample():
    s = Scheduler()
    s.add(Job("A", 5, 10, 100, "alpha job"))
    s.add(Job("B", 2, 20, 100, "beta job"))
    s.add(Job("C", 9, 30, 100, "gamma job"))
    return s


class CoreTests(unittest.TestCase):
    def test_add_and_get(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 100, "widget"))
        self.assertEqual(s.get("A").payload, "widget")

    def test_duplicate_id_rejected(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 100, "one"))
        with self.assertRaises(ValueError):
            s.add(Job("A", 2, 0, 100, "two"))

    def test_all_jobs_is_a_copy(self):
        s = sample()
        got = s.all_jobs()
        got.clear()
        self.assertEqual(len(s.all_jobs()), 3)

    def test_labels_are_independent(self):
        a = Scheduler()
        b = Scheduler()
        a.labels.append("night")
        self.assertEqual(b.labels, [])

    def test_set_priority_visible_everywhere(self):
        s = Scheduler()
        s.add(Job("A", 5, 10, 100, "a"))
        s.set_priority("A", 1)
        self.assertEqual(s.get("A").priority, 1)
        self.assertEqual(s.pending(0)[0].priority, 1)

    def test_cancel_removes_from_pending(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 100, "a"))
        s.cancel("A")
        self.assertEqual(s.pending(0), [])

    def test_pending_priority_order(self):
        # Lower priority value is higher priority: B, A, C.
        self.assertEqual([j.job_id for j in sample().pending(0)], ["B", "A", "C"])

    def test_pending_excludes_expired(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 5, "a"))
        s.add(Job("B", 1, 10, 5, "b"))
        self.assertEqual([j.job_id for j in s.pending(10)], ["B"])

    def test_next_job_single(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 100, "a"))
        self.assertEqual(s.next_job(0).job_id, "A")

    def test_next_job_invalidated_by_add(self):
        s = Scheduler()
        s.add(Job("A", 5, 0, 100, "a"))
        self.assertEqual(s.next_job(0).job_id, "A")
        s.add(Job("B", 1, 0, 100, "b"))  # newly added, higher priority
        self.assertEqual(s.next_job(0).job_id, "B")

    def test_pop_changes_status(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 100, "a"))
        job = s.pop(0)
        self.assertEqual(job.status, "running")
        self.assertEqual(s.get("A").status, "running")
        self.assertEqual(s.pending(0), [])

    def test_expire_removes_all(self):
        s = Scheduler()
        for i in range(4):
            s.add(Job(f"J{i}", 1, 0, 5, "x"))
        self.assertEqual(s.expire(10), ["J0", "J1", "J2", "J3"])

    def test_ttl_remaining(self):
        s = Scheduler()
        s.add(Job("A", 1, 10, 5, "a"))
        self.assertEqual(s.ttl_remaining("A", 12), 3)

    def test_find_substring(self):
        s = Scheduler()
        s.add(Job("A", 1, 0, 100, "prefix-mid-suffix"))
        self.assertEqual([j.job_id for j in s.find("mid")], ["A"])

    def test_batch_end_exclusive(self):
        s = Scheduler()
        for i, name in enumerate("ABC"):
            s.add(Job(name, 1, i, 100, "x"))
        self.assertEqual([j.job_id for j in s.batch(0, 2)], ["A", "B"])

    def test_snapshot_is_a_copy(self):
        s = sample()
        snap = s.snapshot()
        snap.clear()
        self.assertEqual(len(s.all_jobs()), 3)


if __name__ == "__main__":
    unittest.main()
