import unittest

from coord import Coordinator, JobError, RequestContext
from coord.cache import WeakCache, cached
from coord.context import bind, current
from coord.queue import TaskQueue, drain


class ContextTests(unittest.TestCase):
    def test_current_none(self):
        self.assertIsNone(current())

    def test_bind_value(self):
        with bind("r1", user="u"):
            self.assertEqual(current().get("user"), "u")

    def test_get_default(self):
        with bind("r1"):
            self.assertEqual(current().get("nope", 5), 5)

    def test_id_with_value(self):
        with bind("r1", id="r1"):
            self.assertEqual(current().id, "r1")

    def test_request_context_ctor(self):
        ctx = RequestContext("r", a=1)
        self.assertEqual(ctx.get("a"), 1)


class CacheKey:
    pass


class CacheTests(unittest.TestCase):
    def test_get_once(self):
        c = WeakCache()
        k = CacheKey()
        self.assertEqual(c.get(k, lambda: 7), 7)

    def test_len_after_get(self):
        c = WeakCache()
        k = CacheKey()
        c.get(k, lambda: 1)
        self.assertEqual(len(c), 1)

    def test_contains(self):
        c = WeakCache()
        k = CacheKey()
        c.get(k, lambda: 1)
        self.assertIn(k, c)

    def test_clear_single(self):
        c = WeakCache()
        k = CacheKey()
        c.get(k, lambda: 1)
        c.clear()
        self.assertEqual(len(c), 0)

    def test_descriptor_basic(self):
        class Node:
            value = cached(lambda self: self.n)

            def __init__(self, n):
                self.n = n

        self.assertEqual(Node(3).value, 3)

    def test_descriptor_class_access(self):
        class Node:
            value = cached(lambda self: 1)

        self.assertIsInstance(Node.value, cached)


class QueueTests(unittest.IsolatedAsyncioTestCase):
    async def test_put_get_one(self):
        q = TaskQueue()
        q.put("x")
        self.assertEqual(await q.get(), "x")

    async def test_unfinished(self):
        q = TaskQueue()
        q.put(1)
        self.assertEqual(q.unfinished_tasks, 1)

    async def test_task_done(self):
        q = TaskQueue()
        q.put(1)
        await q.get()
        q.task_done()
        self.assertEqual(q.unfinished_tasks, 0)

    async def test_join_empty(self):
        await TaskQueue().join()

    async def test_track(self):
        class W:
            pass

        q = TaskQueue()
        worker = W()
        q.track(worker)
        self.assertGreaterEqual(q.live_workers(), 1)

    async def test_drain_one(self):
        q = TaskQueue()
        q.put(2)
        self.assertEqual([x async for x in drain(q, lambda x: x * 3)], [6])
        self.assertEqual(q.unfinished_tasks, 0)


class ApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_config(self):
        self.assertEqual(Coordinator("c").config("k"), ("c", "k"))

    async def test_config_cached_same(self):
        c = Coordinator("c")
        value = c.config("k")
        self.assertIs(value, c.config("k"))

    async def test_run_and_result(self):
        c = Coordinator()
        c.submit("a", lambda: 5)
        await c.run()
        self.assertEqual(c.result("a"), 5)

    async def test_total_small(self):
        c = Coordinator()
        for i, v in enumerate((1, 2, 3)):
            c.submit(str(i), lambda v=v: v)
        await c.run()
        self.assertEqual(c.total(), 6)

    async def test_total_empty(self):
        self.assertEqual(Coordinator().total(), 0)

    async def test_failed_ids_single(self):
        c = Coordinator()

        def bad():
            raise ValueError("x")

        c.submit("bad", bad)
        with self.assertRaises(JobError):
            await c.run()
        self.assertEqual(c.failed_ids(), ["bad"])

    async def test_closed_initial(self):
        self.assertFalse(Coordinator().closed)

    async def test_astream_basic(self):
        c = Coordinator()
        c.submit("a", lambda: 9)
        self.assertEqual([x async for x in c.astream(1)], [9])


if __name__ == "__main__":
    unittest.main()
