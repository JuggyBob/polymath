"""In-memory job scheduler."""

import re
from dataclasses import replace

from .models import Job


class Scheduler:
    def __init__(self, labels=None):
        self.labels = labels if labels is not None else []
        self._queue = []
        self._index = {}
        self._cache = None

    def add(self, job: Job) -> None:
        if job.job_id in self._index:
            raise ValueError(f"duplicate id: {job.job_id}")
        self._queue.append(job)
        self._index[job.job_id] = job
        self._cache = None

    def get(self, job_id: str) -> Job:
        return self._index[job_id]

    def all_jobs(self):
        return list(self._queue)

    def set_priority(self, job_id: str, priority: int) -> None:
        job = self._index[job_id]
        new_job = replace(job, priority=priority)
        self._replace(job_id, new_job)

    def cancel(self, job_id: str) -> Job:
        if job_id not in self._index:
            raise KeyError(job_id)
        job = self._index.pop(job_id)
        self._queue = [j for j in self._queue if j.job_id != job_id]
        self._cache = None
        return job

    def pending(self, now: int):
        ready = [j for j in self._queue if j.status == "queued" and not j.is_expired(now)]
        return sorted(ready, key=lambda j: (j.priority, j.created, j.job_id))

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
        for job in list(self._queue):
            if job.status == "queued" and job.is_expired(now):
                self._queue.remove(job)
                self._index.pop(job.job_id, None)
                removed.append(job.job_id)
        return sorted(removed)

    def ttl_remaining(self, job_id: str, now: int) -> int:
        try:
            return self._index[job_id].expires_at - now
        except KeyError:
            raise

    def find(self, pattern: str):
        return [j for j in self._queue if re.search(pattern, j.payload)]

    def batch(self, now: int, n: int = 3):
        return self.pending(now)[:n]

    def snapshot(self):
        return dict(self._index)

    def clear(self):
        self._queue = []
        self._index = {}
        self._cache = None
