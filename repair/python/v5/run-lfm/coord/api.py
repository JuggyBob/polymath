"""Public facade for the async job coordinator."""
import functools

from .queue import TaskQueue


class JobError(Exception):
    """Raised when a submitted job fails."""


class Coordinator:
    def __init__(self, name="coord"):
        self.name = name
        self._queue = TaskQueue()
        self._results = {}
        self._closed = False
        self._config_cache = {}

    @property
    def closed(self):
        return self._closed or getattr(self._queue, '_closed', False)

    def submit(self, job_id, fn, *args):
        if self._closed:
            raise RuntimeError("Coordinator is closed")
        self._queue.put((job_id, fn, args))

    async def run(self):
        while self._queue.unfinished_tasks:
            job_id, fn, args = await self._queue.get()
            try:
                self._results[job_id] = fn(*args)
            except Exception as exc:
                msg = f"job {job_id} failed"
                self._results[job_id] = JobError(msg)
                raise JobError(msg) from exc
            finally:
                self._queue.task_done()

    def result(self, job_id):
        if job_id not in self._results:
            raise KeyError(job_id)
        return self._results[job_id]

    @functools.lru_cache(maxsize=128)
    def config(self, key):
        return (self.name, key)

    def failed_ids(self):
        return [k for k, v in self._results.items() if isinstance(v, JobError)]

    def total(self):
        out = 0
        for job_id, value in self._results.items():
            if not isinstance(value, JobError):
                out += value
        return out

    async def astream(self, n):
        done = 0
        while done < n:
            job_id, fn, args = await self._queue.get()
            yield fn(*args)
            self._queue.task_done()
            done += 1
        self._closed = True
