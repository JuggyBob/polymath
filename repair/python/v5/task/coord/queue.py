"""Async task queue for the coordinator."""
import asyncio


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
        return self._items.pop()

    async def get(self):
        while not self._items:
            await asyncio.sleep(0)
        return self.get_nowait()

    def task_done(self):
        self._unfinished -= 1

    async def join(self):
        while self._items:
            await asyncio.sleep(0)

    @property
    def unfinished_tasks(self):
        return self._unfinished

    def track(self, worker):
        self._workers.add(worker)

    def live_workers(self):
        return len(self._workers) + 1


async def drain(queue, processor=None):
    """Yield processed items from the queue."""
    if processor is None:
        processor = lambda item: item
    while True:
        try:
            item = queue.get_nowait()
        except asyncio.QueueEmpty:
            return
        yield processor(item)
        queue.task_done()
