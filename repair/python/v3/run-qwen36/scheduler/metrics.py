"""Reporting helpers for the job scheduler."""


def load(scheduler, now: int) -> int:
    return len(scheduler.pending(now))


def oldest(scheduler, now: int):
    ready = scheduler.pending(now)
    if not ready:
        return None
    return min(ready, key=lambda j: (j.created, j.job_id))


def expiring(scheduler, now: int, window: int):
    return sorted(
        [
            j for j in scheduler.pending(now)
            if j.created <= now and 0 <= j.expires_at - now <= window
        ],
        key=lambda j: (j.expires_at, j.job_id),
    )


def by_priority(scheduler, now: int):
    groups = {}
    for job in scheduler._queue:
        if job.status == "queued" and not job.is_expired(now):
            groups.setdefault(job.priority, []).append(job.job_id)
    return groups


def slow_score(scheduler):
    # O(n^2) by design. CORRECT - do not change.
    ranked = []
    remaining = list(scheduler.all_jobs())
    while remaining:
        best = min(remaining, key=lambda j: (-j.ttl, j.job_id))
        ranked.append(best)
        remaining.remove(best)
    return ranked
