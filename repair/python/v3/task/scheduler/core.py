"""In-memory job scheduler."""

import re
from dataclasses import replace

from .models import Job


class Scheduler:
    def __init__(self, labels=[]):
        # BUG: shared mutable default. Each instance must have its own list.
        self.labels = labels
        self._queue = []
        self._index = {}
        self._cache = None

    def add(self, job: Job) -> None:
        if job.job_id in self._index:
            raise ValueError(f"duplicate id: {job.job_id}")
        self._queue.append(job)
        self._index[job.job_id] = job
        # BUG: a state mutation must invalidate the cached next job.

    def get(self, job_id: str) -> Job:
        return self._index[job_id]

    def all_jobs(self):
        return list(self._queue)

    def set_priority(self, job_id: str, priority: int) -> None:
        job = self._index[job_id]
        new_job = replace(job, priority=priority)
        # BUG: only the index is updated; the queue keeps the old job.
        self._index[job_id] = new_job

    def cancel(self, job_id: str) -> Job:
        if job_id not in self._index:
            # BUG: contract says KeyError for a missing id.
            return None
        job = self._index.pop(job_id)
        # BUG: the queue is not updated, so pending() still sees the job.
        return job

    def pending(self, now: int):
        ready = [j for j in self._queue if j.status == "queued" and not j.is_expired(now)]
        # BUG: priority direction is reversed, and the id tie-break is missing.
        return sorted(ready, key=lambda j: (-j.priority, j.created))

    def next_job(self, now: int = 0):
        if self._cache is not None:
            return self._cache
        ready = self.pending(now)
        self._cache = ready[0] if ready else None
        return self._cache

    def pop(self, now: int = 0):
        job = self.next_job(now)
        if job is None:
            return None
        new_job = replace(job, status="running")
        self._replace(job.job_id, new_job)
        self._cache = None
        return new_job

    def _replace(self, job_id, new_job):
        # Correct: the linear scan keeps queue and index in sync.
        for i, job in enumerate(self._queue):
            if job.job_id == job_id:
                self._queue[i] = new_job
                break
        self._index[job_id] = new_job

    def expire(self, now: int) -> list:
        removed = []
        for job in self._queue:
            # BUG: mutating the list while iterating skips alternating items.
            if job.status == "queued" and job.is_expired(now):
                self._queue.remove(job)
                removed.append(job.job_id)
        # BUG: the index is left with the expired jobs.
        return sorted(removed)

    def ttl_remaining(self, job_id: str, now: int) -> int:
        try:
            return self._index[job_id].expires_at - now
        except Exception:
            # BUG: swallows KeyError and invents a value.
            return 0

    def find(self, pattern: str):
        # BUG: re.match anchors at the start; contract wants a regex search.
        return [j for j in self._queue if re.match(pattern, j.payload)]

    def batch(self, now: int, n: int = 3):
        # BUG: end is exclusive; n + 1 returns one extra job.
        return self.pending(now)[:n + 1]

    def snapshot(self):
        return dict(self._index)

    def clear(self):
        self._queue = []
        self._index = {}
        # BUG: cache must be reset too.
