"""Hidden suite for repair fixture v5-hard.

Injected only at grading time. Every check is a contract described in the
task's AGENTS.md. Names are prefixed to avoid collisions with the visible
suite's method names.
"""
import asyncio
import gc
import time
import unittest
import weakref

from coord import Coordinator, JobError, RequestContext
from coord.cache import WeakCache, cached
from coord.context import bind, current
from coord.queue import TaskQueue, drain


def fail_fn():
    raise ValueError("bad job")


def double(x):
    return x * 2


class Key:
    def __init__(self, v):
        self.v = v

    def __eq__(self, other):
        return isinstance(other, Key) and self.v == other.v

    def __hash__(self):
        return hash(self.v)


class Worker:
    pass


# --------------------------------------------------------------------------
# contextvars-based request context
# --------------------------------------------------------------------------
class HContext(unittest.TestCase):
    def test_h_ctx_current_none_outside(self):
        self.assertIsNone(current())

    def test_h_ctx_inside_bind(self):
        with bind("r1", user="u"):
            self.assertEqual(current().get("user"), "u")

    def test_h_ctx_get_default(self):
        with bind("r1"):
            self.assertEqual(current().get("missing", 42), 42)

    def test_h_ctx_id_property(self):
        with bind("rX", user="u"):
            self.assertEqual(current().id, "rX")

    def test_h_ctx_nested_restore(self):
        with bind("outer", x=1):
            with bind("inner", x=2):
                self.assertEqual(current().id, "inner")
                self.assertEqual(current().get("x"), 2)
            self.assertEqual(current().id, "outer")
            self.assertEqual(current().get("x"), 1)

    def test_h_ctx_exception_restore(self):
        try:
            with bind("boom", x=1):
                raise RuntimeError("x")
        except RuntimeError:
            pass
        self.assertIsNone(current())

    def test_h_ctx_values_isolated(self):
        with bind("r1", user="alice"):
            a = current()
        with bind("r2", user="bob"):
            b = current()
        self.assertEqual(a.get("user"), "alice")
        self.assertEqual(b.get("user"), "bob")

    def test_h_ctx_repeat_bind_restores(self):
        with bind("a"):
            self.assertEqual(current().id, "a")
        self.assertIsNone(current())
        with bind("b"):
            self.assertEqual(current().id, "b")
        self.assertIsNone(current())

    def test_h_ctx_request_context_ctor(self):
        ctx = RequestContext("r", a=1, b=2)
        self.assertEqual((ctx.id, ctx.get("a"), ctx.get("b")), ("r", 1, 2))


class HContextAsync(unittest.IsolatedAsyncioTestCase):
    async def test_h_ctx_async_child_isolation(self):
        async def child():
            with bind("child", x=99):
                await asyncio.sleep(0)
                return current().id

        with bind("parent", x=1):
            got = await asyncio.gather(child(), child())
            self.assertEqual(got, ["child", "child"])
            self.assertEqual(current().id, "parent")
            self.assertEqual(current().get("x"), 1)

    async def test_h_ctx_async_no_leak(self):
        async def child():
            with bind("c"):
                return current().id

        self.assertEqual(await child(), "c")
        self.assertIsNone(current())


# --------------------------------------------------------------------------
# weakref cache and descriptor
# --------------------------------------------------------------------------
class HCache(unittest.TestCase):
    def test_h_cache_get_caches(self):
        c = WeakCache()
        k = Key("k")
        calls = []

        def producer():
            calls.append(1)
            return 7

        self.assertEqual(c.get(k, producer), 7)
        self.assertEqual(c.get(k, producer), 7)
        self.assertEqual(len(calls), 1)

    def test_h_cache_equal_keys_share(self):
        c = WeakCache()
        k1, k2 = Key("a"), Key("a")
        self.assertEqual(c.get(k1, lambda: 1), 1)
        self.assertEqual(c.get(k2, lambda: 2), 1)

    def test_h_cache_distinct_keys(self):
        c = WeakCache()
        a, b = Key("a"), Key("b")
        self.assertEqual(c.get(a, lambda: 1), 1)
        self.assertEqual(c.get(b, lambda: 2), 2)
        self.assertEqual(len(c), 2)

    def test_h_cache_gc_drops_entry(self):
        c = WeakCache()
        k = Key("g")
        c.get(k, lambda: 5)
        self.assertEqual(len(c), 1)
        del k
        gc.collect()
        self.assertEqual(len(c), 0)

    def test_h_cache_clear_all(self):
        c = WeakCache()
        keys = [Key(i) for i in range(3)]
        for i, k in enumerate(keys):
            c.get(k, lambda i=i: i)
        self.assertEqual(len(c), 3)
        c.clear()
        self.assertEqual(len(c), 0)

    def test_h_cache_contains(self):
        c = WeakCache()
        k = Key("k")
        self.assertNotIn(k, c)
        c.get(k, lambda: 1)
        self.assertIn(k, c)

    def test_h_cache_producer_exception_not_cached(self):
        c = WeakCache()
        k = Key("e")

        def bad():
            raise ValueError("no")

        with self.assertRaises(ValueError):
            c.get(k, bad)
        self.assertEqual(c.get(k, lambda: 9), 9)

    def test_h_desc_name(self):
        class Node:
            score = cached(lambda self: self.n)

            def __init__(self, n):
                self.n = n

        self.assertEqual(Node.score.name, "score")

    def test_h_desc_per_instance(self):
        class Node:
            value = cached(lambda self: self.n)

            def __init__(self, n):
                self.n = n

        self.assertEqual(Node(1).value, 1)
        self.assertEqual(Node(2).value, 2)

    def test_h_desc_slotted(self):
        class Slot:
            __slots__ = ("n", "__weakref__")
            value = cached(lambda self: self.n * 2)

            def __init__(self, n):
                self.n = n

        self.assertEqual(Slot(3).value, 6)

    def test_h_desc_repeat_uses_cache(self):
        class Node:
            value = cached(lambda self: self.n)

            def __init__(self, n):
                self.n = n

        a = Node(4)
        self.assertEqual(a.value, 4)
        a.n = 9
        self.assertEqual(a.value, 4)

    def test_h_desc_class_access(self):
        class Node:
            value = cached(lambda self: 1)

        self.assertIsInstance(Node.value, cached)


# --------------------------------------------------------------------------
# async task queue
# --------------------------------------------------------------------------
class HQueue(unittest.IsolatedAsyncioTestCase):
    async def test_h_queue_fifo(self):
        q = TaskQueue()
        for x in ("a", "b", "c"):
            q.put(x)
        self.assertEqual([await q.get() for _ in range(3)], ["a", "b", "c"])

    async def test_h_queue_get_nowait_empty(self):
        q = TaskQueue()
        with self.assertRaises(asyncio.QueueEmpty):
            q.get_nowait()

    async def test_h_queue_unfinished(self):
        q = TaskQueue()
        q.put(1)
        q.put(2)
        self.assertEqual(q.unfinished_tasks, 2)
        await q.get()
        q.task_done()
        self.assertEqual(q.unfinished_tasks, 1)

    async def test_h_queue_join_waits_for_task_done(self):
        q = TaskQueue()
        q.put("x")
        await q.get()

        async def must_not_finish():
            await asyncio.wait_for(q.join(), timeout=0.05)
            return True

        try:
            await must_not_finish()
        except asyncio.TimeoutError:
            pass
        else:
            self.fail("join() returned before task_done()")
        q.task_done()
        await asyncio.wait_for(q.join(), timeout=0.5)

    async def test_h_queue_join_after_done(self):
        q = TaskQueue()
        q.put(1)
        await q.get()
        q.task_done()
        await asyncio.wait_for(q.join(), timeout=0.5)

    async def test_h_queue_task_done_over(self):
        q = TaskQueue()
        q.put(1)
        await q.get()
        q.task_done()
        with self.assertRaises(ValueError):
            q.task_done()

    async def test_h_queue_track_weak_gc(self):
        q = TaskQueue()
        w = Worker()
        q.track(w)
        self.assertEqual(q.live_workers(), 1)
        del w
        gc.collect()
        self.assertEqual(q.live_workers(), 0)

    async def test_h_queue_live_workers_exact(self):
        q = TaskQueue()
        a, b = Worker(), Worker()
        q.track(a)
        q.track(b)
        self.assertEqual(q.live_workers(), 2)

    async def test_h_queue_drain_full(self):
        q = TaskQueue()
        for i in range(3):
            q.put(i)
        got = [x async for x in drain(q, double)]
        self.assertEqual(got, [0, 2, 4])
        self.assertEqual(q.unfinished_tasks, 0)

    async def test_h_queue_drain_early_close(self):
        q = TaskQueue()
        for i in range(3):
            q.put(i)
        gen = drain(q)
        self.assertEqual(await gen.__anext__(), 0)
        await gen.aclose()
        self.assertEqual(q.unfinished_tasks, 2)

    async def test_h_queue_drain_processor_error(self):
        q = TaskQueue()
        q.put(1)
        gen = drain(q, lambda x: 1 / 0)
        with self.assertRaises(ZeroDivisionError):
            await gen.__anext__()
        self.assertEqual(q.unfinished_tasks, 0)


# --------------------------------------------------------------------------
# public facade
# --------------------------------------------------------------------------
class HApi(unittest.IsolatedAsyncioTestCase):
    async def test_h_api_config_value(self):
        c = Coordinator("c1")
        self.assertEqual(c.config("k"), ("c1", "k"))

    async def test_h_api_config_cached(self):
        c = Coordinator("c1")
        self.assertIs(c.config("k"), c.config("k"))

    async def test_h_api_config_no_self_retention(self):
        c = Coordinator("tmp")
        ref = weakref.ref(c)
        c.config("k")
        del c
        gc.collect()
        self.assertIsNone(ref())

    async def test_h_api_config_distinct_instances(self):
        a, b = Coordinator("a"), Coordinator("b")
        self.assertEqual(a.config("k"), ("a", "k"))
        self.assertEqual(b.config("k"), ("b", "k"))

    async def test_h_api_run_stores_result(self):
        c = Coordinator()
        c.submit("a", lambda: 5)
        await c.run()
        self.assertEqual(c.result("a"), 5)

    async def test_h_api_run_exception_type(self):
        c = Coordinator()
        c.submit("bad", fail_fn)
        with self.assertRaises(JobError):
            await c.run()

    async def test_h_api_run_exception_cause(self):
        c = Coordinator()
        c.submit("bad", fail_fn)
        with self.assertRaises(JobError) as cm:
            await c.run()
        self.assertIsInstance(cm.exception.__cause__, ValueError)

    async def test_h_api_run_failure_recorded(self):
        c = Coordinator()
        c.submit("bad", fail_fn)
        with self.assertRaises(JobError):
            await c.run()
        self.assertIsInstance(c.result("bad"), JobError)

    async def test_h_api_result_missing(self):
        with self.assertRaises(KeyError):
            Coordinator().result("nope")

    async def test_h_api_failed_ids_order(self):
        c = Coordinator()
        for jid in ("b", "a", "c"):
            c.submit(jid, fail_fn)
            with self.assertRaises(JobError):
                await c.run()
        self.assertEqual(c.failed_ids(), ["b", "a", "c"])

    async def test_h_api_failed_ids_none(self):
        c = Coordinator()
        c.submit("ok", lambda: 1)
        await c.run()
        self.assertEqual(c.failed_ids(), [])

    async def test_h_api_failed_ids_after_success(self):
        c = Coordinator()
        c.submit("good", lambda: 1)
        await c.run()
        c._results["late"] = JobError("late")
        self.assertEqual(c.failed_ids(), ["late"])

    async def test_h_api_total(self):
        c = Coordinator()
        for i, v in enumerate((1, 2, 3)):
            c.submit(f"j{i}", lambda v=v: v)
        await c.run()
        self.assertEqual(c.total(), 6)

    async def test_h_api_total_ignores_failures(self):
        c = Coordinator()
        c.submit("ok", lambda: 4)
        c.submit("bad", fail_fn)
        with self.assertRaises(JobError):
            await c.run()
        self.assertEqual(c.total(), 4)

    async def test_h_api_total_empty(self):
        self.assertEqual(Coordinator().total(), 0)

    def test_h_api_total_perf_20k(self):
        c = Coordinator()
        for i in range(20000):
            c.submit(f"j{i}", lambda: 1)
        asyncio.run(c.run())
        t0 = time.monotonic()
        self.assertEqual(c.total(), 20000)
        elapsed = time.monotonic() - t0
        self.assertLess(elapsed, 2.0, f"total() took {elapsed:.2f}s")

    async def test_h_api_astream_yields(self):
        c = Coordinator()
        for i in (1, 2):
            c.submit(f"j{i}", lambda i=i: i)
        self.assertEqual([x async for x in c.astream(2)], [1, 2])

    async def test_h_api_astream_closes(self):
        c = Coordinator()
        for i in range(3):
            c.submit(f"j{i}", lambda i=i: i)
        gen = c.astream(3)
        self.assertEqual(await gen.__anext__(), 0)
        await gen.aclose()
        self.assertTrue(c.closed)

    async def test_h_api_astream_task_done(self):
        c = Coordinator()
        for i in range(3):
            c.submit(f"j{i}", lambda i=i: i)
        gen = c.astream(3)
        await gen.__anext__()
        await gen.aclose()
        self.assertEqual(c._queue.unfinished_tasks, 2)

    async def test_h_api_submit_after_close(self):
        c = Coordinator()
        c._closed = True
        with self.assertRaises(RuntimeError):
            c.submit("x", lambda: 1)

    async def test_h_api_closed_initial(self):
        self.assertFalse(Coordinator().closed)


if __name__ == "__main__":
    unittest.main()
