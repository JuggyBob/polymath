"""Reporting helpers for the job scheduler."""


def load(scheduler, now: int) -> int:
    return len(scheduler.pending(now))


def oldest(scheduler, now: int):
    ready = scheduler.pending(now)
    if not ready:
        return None
    return min(ready, key=lambda j: (j.created, j.job_id))


def expiring(scheduler, now: int, window: int):
    # BUG 1: the upper bound is inclusive; < drops jobs exactly at the boundary.
    # BUG 2: results must be ordered by (expires_at, job_id); this keeps pending order.
    # BUG 3: jobs created in the future must be excluded (created <= now).
    return [
        j for j in scheduler.pending(now)
        if 0 <= j.expires_at - now < window
    ]


def by_priority(scheduler, now: int):
    # BUG: groups must follow queue insertion order, not pending's sort order.
    groups = {}
    for job in scheduler.pending(now):
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
