"""Async task queue for the coordinator."""
import asyncio
import weakref


class TaskQueue:
    def __init__(self):
        self._items = []
        self._unfinished = 0
        self._workers = set()

    def put(self, item):
        self._items.append(item)
        self._unfinished += 1

    def get_nowait(self):
        if not self._items:
            raise asyncio.QueueEmpty
        return self._items.pop(0)

    async def get(self):
        while not self._items:
            await asyncio.sleep(0)
        return self.get_nowait()

    def task_done(self):
        self._unfinished -= 1

    async def join(self):
        while self.unfinished_tasks:
            await asyncio.sleep(0)

    @property
    def unfinished_tasks(self):
        return self._unfinished

    def track(self, worker):
        self._workers.add(weakref.ref(worker))

    def live_workers(self):
        return len(self._workers)


async def drain(queue, processor=None):
    """Yield processed items from the queue."""
    if processor is None:
        processor = lambda item: item
    try:
        while True:
            try:
                item = queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            yield processor(item)
            queue.task_done()
    finally:
        queue.task_done()
        queue._closed = True
