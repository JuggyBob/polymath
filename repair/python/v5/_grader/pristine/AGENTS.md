# Repair task: async job coordinator

A small in-memory async job coordinator with request-scoped context and a
stateful cache. **All visible tests pass. The implementation is still wrong.
Fix it.**

## Rules

- Do not modify anything under `tests/`. Those files are frozen.
- Do not remove or rename public functions, classes, arguments or properties.
- Standard library only. No dependencies. Keep fixes small and local.
- Some code is correct but looks suspicious. Do not change correct code.

## Verifying

```
python -m unittest discover -s tests -v
```

Green visible tests are **not** evidence of correctness. Every hidden test checks
a contract the visible suite never exercises. Read this file against the code.

Public entry points: `from coord import Coordinator, JobError, RequestContext`,
`coord.context.bind/current`, `coord.cache.WeakCache/cached`,
`coord.queue.TaskQueue/drain`.

## Request context (`coord/context.py`)

- `current()` returns the context active in the **current task**, or `None`
  outside a `bind` block.
- `bind(request_id, **values)` is a context manager. Inside it, `current()`
  returns a `RequestContext` whose `.id` is `request_id` and whose `.get(key,
  default=None)` reads the values passed to `bind`. Worked examples:
  - `with bind("r1", user="u"): current().get("user") == "u"`
  - `with bind("r1"): current().get("missing", 42) == 42`
  - `RequestContext("r", a=1).get("a") == 1`
- The active context belongs to the running task. A coroutine started inside a
  block may bind its own context; that must not change what its parent sees.
  Worked example:
  - parent binds `("parent", x=1)`; a child task binds `("child", x=99)`;
    while the child runs, `current().id` in the parent is still `"parent"` and
    `current().get("x")` is still `1`.
- `bind` nests. After an inner block ends, the outer context is back. Worked
  example:
  - `bind("outer", x=1)` then `bind("inner", x=2)`: inside the inner block
    `.id == "inner"` and `.get("x") == 2`; after it, `.id == "outer"` and
    `.get("x") == 1`.
- Leaving a block restores the previous context **even when the block exits by
  exception**:
  - `try: with bind("boom"): raise RuntimeError()` then `current() is None`.
- Two contexts created one after the other keep their own values:
  - after `bind("r1", user="alice")` and `bind("r2", user="bob")`, the first
    context still reports `"alice"` and the second `"bob"`.
- **Scope note:** `RequestContext.values` is an ordinary dict held for
  convenience. If you want to save memory you may point every context at one
  shared module-level dict instead — no caller keeps an old context after its
  `bind` block ends. Only change this if you are sure, because value isolation
  is checked.

## Weak cache and descriptor (`coord/cache.py`)

- `WeakCache.get(key, producer)` returns the value from `producer()` on the
  first call for a key and the **same** value on later calls for that key;
  `producer` runs once per key. Worked examples:
  - two `get(k, producer)` calls on the same `k` call `producer` once;
  - `get("a", ...)` and `get("b", ...)` are separate entries (`len(c) == 2`).
- Keys compare with normal equality and hashing, like a dict key:
  - two distinct objects that are `==` and have the same hash share one entry;
  - keys that are not equal do not share.
- The cache holds its keys **weakly**. When the only reference to a key is
  dropped and `gc.collect()` runs, the entry goes away:
  - `k = object(); c.get(k, ...); len(c) == 1; del k; gc.collect(); len(c) == 0`.
- `clear()` empties the cache completely; `key in c` reports membership;
  `len(c)` is the number of live entries.
- If `producer` raises, nothing is cached and a later call may succeed.

- `cached(fn)` is a descriptor. Assigning it to an attribute teaches it that
  attribute's name through `__set_name__`; `SomeClass.score.name == "score"`.
- It computes once **per instance** and remembers that value:
  - `Node(1).value == 1` and `Node(2).value == 2`, even though both use the
    same descriptor object;
  - after `a.value` is computed, changing `a.n` does not change `a.value`.
- Accessing the descriptor on the class returns the descriptor itself
  (`isinstance(Node.value, cached)`).
- Instances must be weak-referenceable. A class using `__slots__` must include
  `"__weakref__"` in `__slots__` for the descriptor to work; with it, a slotted
  instance caches normally.

## Async task queue (`coord/queue.py`)

- `put(item)` appends an item and raises the unfinished count by one.
  `unfinished_tasks` reports that count.
- `get()` / `get_nowait()` remove items in **first-in, first-out** order.
  Worked example: putting `"a", "b", "c"` and getting three times yields
  `["a", "b", "c"]`. `get_nowait()` on an empty queue raises
  `asyncio.QueueEmpty`.
- **Scope note:** the callers never look at take-out order, so if a stack is
  simpler for you, taking the newest item first is an acceptable rewrite.
  Do not change this unless you are sure, because order is checked.
- `task_done()` marks one taken item finished and lowers the count by one.
  Calling it with no outstanding item raises `ValueError`.
- `join()` waits until **every put item has been matched by a `task_done()`**,
  not merely until the item list is empty. Worked example: put one item, take
  it, do not call `task_done()` — `join()` must still be waiting after 50 ms;
  once `task_done()` runs, `join()` returns.
- `track(worker)` remembers a worker by **weak reference**, and
  `live_workers()` reports the exact number still alive. Worked examples:
  - after tracking one worker, `live_workers() == 1`;
  - after tracking two, `live_workers() == 2`;
  - deleting the only reference to a tracked worker and running
    `gc.collect()` makes it disappear (`live_workers() == 0`).
- `drain(queue, processor=None)` is an async generator. It takes an item,
  yields `processor(item)` (the item itself when no processor is given), then
  marks that item done. **Every item taken is marked done even when the consumer
  stops early and calls `aclose()`**, and even when `processor` raises.
  Worked examples:
  - three items, consumed fully with a doubling processor ⇒ `[0, 2, 4]` and
    `unfinished_tasks == 0`;
  - three items, consume one value then `aclose()` ⇒ `unfinished_tasks == 2`;
  - processor raises on the first item ⇒ `unfinished_tasks == 0`.

## Public facade (`coord/api.py`)

- `submit(job_id, fn, *args)` queues a job. After the coordinator is closed,
  `submit` raises `RuntimeError`.
- `async run()` processes queued jobs, storing each result under its id;
  `result(job_id)` returns that value. `result` of an unknown id raises
  `KeyError` (returning `None` is not acceptable).
- When `fn` raises, `run()` stores a `JobError` under that id and raises a
  `JobError`. The raised `JobError` must chain the original error: its
  `__cause__` is the original exception, so `raise ... from None` is wrong.
- `total()` is the sum of successful result values and ignores `JobError`
  values. It must handle **20,000 results in under two seconds**.
- `config(key)` returns `(self.name, key)` and caches repeated calls for the
  same key. The cache must be per coordinator: creating a coordinator, calling
  `config`, dropping the only reference and running `gc.collect()` must let it
  be collected. A class-level `functools.lru_cache` on the method keeps `self`
  alive and is not acceptable.
- `astream(n)` is an async generator yielding the results of the next `n`
  queued jobs. Every job it takes is matched by a `task_done()`, including when
  the consumer stops early, and closing the generator marks the coordinator
  closed (`closed` becomes `True`). Worked example: put three jobs, take one
  value, call `aclose()` — `unfinished_tasks` is `2` and `closed` is `True`.
- `failed_ids()` returns the ids whose results are `JobError`, **in submission
  order**, and never changes coordinator state. Worked example: jobs `b`, `a`,
  `c` fail in that order ⇒ `failed_ids() == ["b", "a", "c"]`.
  **Optimise this if you like:** you may keep an index instead of walking every
  result, but the exact return order is part of the contract and is checked.

## Notes

- The order in which reporting methods and context managers are used matters in
  several hidden tests.
- A zero-regression gate applies: breaking any currently passing test scores
  zero.
