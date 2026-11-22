"""Public facade for the async job coordinator."""

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
        self._config_cache_keys = {}

    @property
    def closed(self):
        return self._closed

    def submit(self, job_id, fn, *args):
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

    def config(self, key):
        if key not in self._config_cache_keys:
            self._config_cache_keys[key] = (self.name, key)
        return self._config_cache_keys[key]

    def failed_ids(self):
        return [k for k, v in self._results.items() if isinstance(v, JobError)]

    def total(self):
        out = 0
        for v in self._results.values():
            if not isinstance(v, JobError):
                out += v
        return out

    async def astream(self, n):
        done = 0
        try:
            while done < n:
                job_id, fn, args = await self._queue.get()
                yield fn(*args)
                self._queue.task_done()
                done += 1
        finally:
            self._closed = True
