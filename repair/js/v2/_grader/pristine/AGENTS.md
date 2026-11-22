# Promises and async utilities — repair task

`src/async.js` is a small CommonJS module of promise/async helpers. Several
functions contain planted bugs. Fix the implementation so that **every**
contract below holds.

Rules:

- Keep the public API exactly as it is: the same seven exports and the same
  signatures. Do not add or remove exports.
- Do not edit any file under `tests/`. The grader compares those files
  byte-for-byte with the pristine copies.
- No third-party packages and no changes outside `src/async.js`.
- Run the visible feedback tests with `node tests/test_visible.js`. They print
  `TEST <name> PASS|FAIL` lines. Hidden tests are written against the same
  contracts.
- Every returned promise must settle. No promise rejection may be left
  unhandled (the test files record `process.on('unhandledRejection')` events).

## Export shape

`module.exports` must contain exactly:

```
retry, withTimeout, mapLimit, Emitter, debounce, memoizeAsync, promisePool
```

## Contracts

### retry(fn, retries, delayMs)

- `fn` is an async (promise-returning) function. `delayMs` defaults to `0`.
- Attempt `fn` at most `1 + retries` times. Stop at the first success and
  resolve with that value.
- If every attempt fails, reject with the **last** error.
- Wait `delayMs` milliseconds between failed attempts.
- With `retries = 1` and `fn` succeeding on the first call, `fn` runs once.

### withTimeout(promise, ms)

- Returns a promise that adopts `promise`'s outcome: it resolves with the
  resolved value and rejects with the rejection reason.
- If `promise` has not settled after `ms` milliseconds, reject with an
  `Error` whose `message` is exactly `timeout`.
- The internal timer must be cleared once `promise` settles, and the source
  promise's rejection must always be handled (no unhandled rejection).

### mapLimit(items, limit, mapper)

- `mapper(item, index)` may be async. Run at most `limit` mapper calls at once.
- Resolve with an array of results **in input order**, regardless of the order
  in which mapper calls finish.
- An empty `items` resolves with `[]`.

### Emitter

A class with `on`, `once`, `off`, `emit`.

- `on(name, fn)` appends `fn` as a normal listener. Returns the emitter.
- `once(name, fn)` registers `fn` so it runs **at most once** for that event;
  after it runs it is automatically removed. Returns the emitter.
- `off(name, fn)` removes listeners registered for `name` by `on(name, fn)`
  **and** by `once(name, fn)`. Matching is by the original function reference.
  Removing a name with no listeners is a no-op. Returns the emitter.
- `emit(name, ...args)` calls every current listener (a snapshot is taken) with
  the emitter bound as `this` and with `args` spread as arguments. It returns
  `true` if at least one listener was called, otherwise `false`.
- A `once` listener removed by `off` before its event fires must never run.

### debounce(fn, wait)

- Returns a debounced function. Each call captures its `this` and arguments.
- After `wait` milliseconds with no further calls, `fn` is invoked **once**
  with the most recent call's `this` and arguments (trailing edge).
- Calling the debounced function repeatedly in one tick results in exactly one
  invocation. `Promise.resolve().then(...)` is not a valid substitute for the
  timer: the wait must be a real `wait` millisecond delay.

### memoizeAsync(fn, keyFn)

- `keyFn` is optional and defaults to the first argument. It produces the cache
  key from the call arguments.
- Keys are stored in a `Map` (SameValueZero identity): `1` and `'1'` are
  different keys.
- The **in-flight promise** is cached, not the resolved value: two concurrent
  calls with the same key must invoke `fn` once and receive the same result.
- Errors are cached as rejected promises in the same way; a later call with the
  same key observes that rejection without calling `fn` again.

### promisePool(items, limit, worker)

- `worker(item, slot)` may be async. Run at most `limit` workers at once.
- `slot` is the index of the worker slot that picks up the item, in the range
  `0 .. limit - 1`. Every async runner must see its own slot value (a loop
  variable captured by reference is a bug).
- Resolve with an array of results in **input order**.
