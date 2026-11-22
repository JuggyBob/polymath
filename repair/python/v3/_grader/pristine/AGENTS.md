# Repair task: job scheduler

A small in-memory job scheduler used by a worker CLI. **Some tests fail. Fix the code.**

## Rules

- Do **not** modify anything under `tests/`. Those files are frozen.
- Do **not** remove or rename public functions, classes or arguments.
- Standard library only. Do not add dependencies.
- Keep fixes small and local. Do not rewrite the module.
- Do **not** change the `Job` dataclass fields.

## Verifying

```
python -m unittest discover -s tests -v
```

Hidden tests are not visible. Passing the visible suite is necessary but **not
sufficient**. Read every contract below.

## Contracts

### `Job` (`scheduler/models.py`)

- `Job(job_id, priority, created, ttl, payload, status="queued", tags=())`
- `priority`: **lower value means higher priority**.
- `expires_at` = `created + ttl`.
- `is_expired(now)` is `now >= expires_at` (inclusive).

### `Scheduler` (`scheduler/core.py`)

Internal state: a queue list, an id→job index, and a cached next job.

- `Scheduler(labels=[])` — each instance must have **its own** `labels` list.
- `add(job)` — appends the job to both the queue and the index. Duplicate
  `job_id` raises `ValueError`.
- `get(job_id)` — returns the job, or raises `KeyError` when missing.
- `all_jobs()` — returns a **new list**; mutating it must not affect the scheduler.
- `set_priority(job_id, priority)` — changes the priority **everywhere**: both
  `get()` and `pending()` must immediately see the new value. Missing id raises
  `KeyError`.
- `cancel(job_id)` — removes the job from **all** state and returns it. A
  missing id raises `KeyError`.
- `pending(now)` — jobs whose status is `"queued"` and which are not expired,
  ordered by `(priority, created, job_id)` ascending.
- `next_job(now)` — returns the first job of `pending(now)`, or `None`. The
  result may be cached, but **every state mutation invalidates the cache**:
  `add`, `set_priority`, `cancel`, `expire`, `pop` and `clear`.
- `pop(now)` — returns the next pending job with status changed to `"running"`;
  returns `None` if there is none. The job stays in the index with its new
  status, and is no longer pending. Queue and index must both see the new status.
- `expire(now)` — removes **all** expired queued jobs from queue and index, and
  returns their ids in sorted order. It must not skip any job.
- `ttl_remaining(job_id, now)` — `expires_at - now` (may be negative). A
  missing id raises `KeyError`; never silently return a default.
- `find(pattern)` — a **regex search** (not anchored to the start) against
  `payload`; returns matching jobs in queue order.
- `batch(now, n=3)` — up to **n** jobs from `pending(now)`; `n` is an exclusive
  upper bound.
- `snapshot()` — returns a **copy** of the id→job mapping.
- `clear()` — resets queue, index and cache.

### `scheduler/metrics.py`

- `load(scheduler, now)` — number of pending jobs.
- `oldest(scheduler, now)` — pending job with the smallest `(created, job_id)`,
  or `None`.
- `expiring(scheduler, now, window)` — pending jobs whose `created <= now` and
  whose `0 <= ttl_remaining <= window` (inclusive at both ends), ordered by
  `(expires_at, job_id)` ascending. Jobs created in the future are excluded.
- `by_priority(scheduler, now)` — `{priority: [job_id, ...]}` for pending jobs,
  with ids in insertion order within each group and groups in first-seen order.
- `slow_score(scheduler)` — jobs ordered by `(-ttl, job_id)`. This function is
  O(n²) by design and is **correct**. Do not change it.

## Notes

- There are **several red herrings**: code that looks wrong or slow but is
  correct. Do not "optimise" or "simplify" it.
- The bugs interact. A fix that makes one method right while leaving another
  view of the same state stale is not a fix.
- A zero-regression gate applies: breaking any currently passing test scores
  the whole task zero.
