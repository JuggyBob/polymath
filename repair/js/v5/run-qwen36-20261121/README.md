# Core Utilities — behaviour contract

This package is a set of small, dependency-free utilities. Several of them are
on a hot path or are consumed by code that compares exact values and exact
ordering, so the *observable behaviour* of each function is specified below
with worked examples. The examples are normative: anything that prints a value
is a value that callers rely on.

There is no build step. Modules live in `src/` and are CommonJS (`module.exports`).
Tests `require('../src/<module>.js')`. Node 24 is the runtime.

---

## 1. `src/scheduler.js`

Ordering helpers. "Microtask" below means work queued with `queueMicrotask`
or a settled `Promise#then`. "Macrotask" means a timer (`setTimeout`).
Within one turn, all microtasks run before any macrotask, and microtasks run
in the order they were queued.

* `schedulerLabel()` → the string `'scheduler'`.
* `scheduleSync(tasks)` → a shallow copy of `tasks`. Mutating the copy must not
  mutate the input.

* `runPhases()` → `Promise<Array<string>>`. It records four labels:
  * `'sync'` recorded synchronously,
  * `'micro'` queued as a microtask via `queueMicrotask`,
  * `'promise'` queued as a microtask via a settled `Promise#then`,
  * `'macro'` queued as a macrotask via `setTimeout(…, 0)`.
  The returned array is in execution order.

  ```js
  await runPhases();
  // ['sync', 'micro', 'promise', 'macro']
  ```

  Note that `queueMicrotask` is registered *before* the `Promise#then`, so
  `'micro'` precedes `'promise'`, and both precede `'macro'`.

* `drainQueue(n)` → `Promise<number>`. Queues exactly `n` increments, each as a
  microtask via `queueMicrotask`, then yields once to the macrotask queue and
  returns how many increments had run by then.

  ```js
  await drainQueue(5);   // 5
  await drainQueue(50);  // 50
  ```

* `thenVsMicrotask()` → `Promise<Array<string>>`. Registers a microtask with
  `queueMicrotask` that pushes `'micro'`, and a settled `Promise#then` that
  pushes `'then'`, then yields exactly once.

  ```js
  await thenVsMicrotask();  // ['micro', 'then']
  ```

* `awaitOrdering()` → `Promise<Array<string>>`. A promise is created whose
  `.then` pushes `'inner'` and resolves to `'v'`. The string `'before'` is
  recorded *before* awaiting that promise, and `'after:v'` after it.

  ```js
  await awaitOrdering();
  // ['before', 'inner', 'after:v']
  ```

* `delayedOrder()` → `Promise<Array<string>>`. Two timers are queued: `'late'`
  with a 10 ms delay and `'early'` with a 0 ms delay. After waiting long
  enough, the array is in the order in which the callbacks fired.

  ```js
  await delayedOrder();  // ['early', 'late']
  ```

---

## 2. `src/proxyStore.js`

* `createPlainStore()` → a plain object with ordinary get/set behaviour.

* `countingGet()` → a Proxy over an empty target whose `get` trap returns the
  stored value for present keys and the number `0` for any missing key.

  ```js
  const s = countingGet();
  s.missing;   // 0
  s.a = 4;
  s.a;         // 4
  ```

* `numericSet()` → a Proxy whose `set` trap accepts **only numbers**. Storing
  a non-number is a silent no-op (the trap returns `true` so strict mode does
  not throw); reading that key yields `undefined`.

  ```js
  const s = numericSet();
  s.x = 5;     s.x;  // 5
  s.y = 'no';  s.y;  // undefined
  ```

* `strictHas()` → a Proxy whose `has` trap reports whether the key currently
  holds a number.

  ```js
  const s = strictHas();
  'a' in s;        // false
  s.a = 1;
  'a' in s;        // true
  ```

  (Ordinary assignment on the proxy writes through to the target.)

* `listedKeys()` → a Proxy over `{ a: 1, b: 'x', c: 2 }` whose `ownKeys` trap
  exposes only keys whose value is a number.

  ```js
  Reflect.ownKeys(listedKeys());  // ['a', 'c']
  ```

* `resettable()` → a Proxy whose `deleteProperty` trap *resets* a key to `0`
  instead of removing it.

  ```js
  const s = resettable();
  s.a = 5;
  delete s.a;
  s.a;   // 0
  ```

* `descriptorProxy()` → a Proxy over `{ v: 7 }` whose
  `getOwnPropertyDescriptor` trap marks the property non-enumerable.

  ```js
  Object.keys(descriptorProxy());  // []
  ```

---

## 3. `src/cache.js`

The key domain for every cache here is **object identity**: distinct objects
are distinct keys even when their contents or string forms are identical.

* `identity(obj)` → `obj`.

* `memoize(fn)` → a function that calls `fn(obj)` once per distinct object and
  caches the result by identity.

  ```js
  let calls = 0;
  const f = memoize(o => { calls++; return o.v; });
  const a = { v: 1 }, b = { v: 1 };
  f(a);          // 1, computes
  f(a);          // 1, cached
  f(b);          // 1, computes again (b is a different object)
  calls;         // 2
  ```

* `BoundCache` → a class with `store(obj, value)` and `load(obj)`. Each
  instance has its own private, identity-keyed store. Entries do not leak
  between instances.

  ```js
  const c1 = new BoundCache(), c2 = new BoundCache();
  const o = {};
  c1.store(o, 'a');
  c1.load(o);   // 'a'
  c2.load(o);   // undefined (separate instance)
  ```

* `stamp(obj)` → returns a stable stamp for an object: the same object always
  gets the same stamp, different objects get different stamps.

  ```js
  const o = {};
  stamp(o) === stamp(o);              // true
  stamp(o) === stamp({});             // false
  ```

* `memoizeWeak(fn)` → like `memoize`, but must use a weak identity map so that
  cached keys do not keep objects alive.

  ```js
  let calls = 0;
  const f = memoizeWeak(o => ++calls);
  const a = {};
  f(a);  // 1
  f(a);  // 1, cached
  calls; // 1
  ```

---

## 4. `src/asyncStream.js`

* `syncRange(n)` → `[0, 1, …, n-1]` as a plain array.

* `genRange(start, end)` → an async generator yielding `start` through
  `end - 1` (exclusive upper bound).

  ```js
  const out = [];
  for await (const v of genRange(0, 3)) out.push(v);
  out; // [0, 1, 2]
  ```

* `genWithFinally(cb)` → an async generator that yields `1, 2, 3` and invokes
  `cb` exactly once, in its `finally` block, when the generator is closed
  (either by being fully consumed or by `return()` being called). The callback
  must run *after* the yielded values, never before.

  ```js
  const ev = [];
  for await (const v of genWithFinally(() => ev.push('fin'))) ev.push(v);
  ev; // [1, 2, 3, 'fin']
  ```

* `collect(gen)` → consumes an **async** iterable with `for await … of` and
  returns the values as an array.

  ```js
  await collect(genRange(0, 3));  // [0, 1, 2]
  ```

* `firstN(gen, n)` → takes the first `n` values from an async iterable and
  returns them, then calls `gen.return()` so the generator's `finally` runs.

  ```js
  let closed = false;
  async function* g() { try { yield 1; yield 2; } finally { closed = true; } }
  await firstN(g(), 1);  // [1]
  closed;                // true
  ```

* `genPairs(arr)` → an async generator yielding consecutive pairs, including
  a trailing pair with `undefined` for an odd last element.

  ```js
  const out = [];
  for await (const p of genPairs([1, 2, 3, 4, 5])) out.push(p);
  out; // [[1,2], [3,4], [5,undefined]]
  ```

---

## 5. `src/numbers.js`

* `isEven(n)`, `square(n)`, `add(a, b)` are straightforward helpers.

* `isPrime(n)` → `true` iff `n` is a prime number. **Optimisation contract:**
  * It must run in **O(sqrt(n))** time, not O(n).
  * It must be correct for `0`, `1`, `2`, negative numbers, large primes such
    as `2147483647` (2^31 − 1) and large composites such as `2147483649`
    (2^31 + 1, divisible by 3).
  * The square-root test must be **inclusive** at the boundary: a perfect
    square such as `49`, `121` or `1009² = 1018081` is not prime, so the
    loop must actually test the divisor equal to the square root.
  * Performance: a loop over the first **1,000,000** candidates
    (`for (i = 0; i < 1000000; i++) isPrime(i)`) must complete in **under
    2 seconds** and yield the correct prime count `78498`.

  ```js
  isPrime(0);            // false
  isPrime(1);            // false
  isPrime(-7);           // false
  isPrime(2);            // true
  isPrime(9);            // false
  isPrime(2147483647);   // true
  isPrime(2147483649);   // false
  isPrime(1009 * 1009);  // false
  ```

* `isPerfectSquare(n)` → `true` iff `n` is a perfect square.

  ```js
  isPerfectSquare(4); // true
  isPerfectSquare(9); // true
  isPerfectSquare(3); // false
  ```

* `countPrimesUpTo(limit)` → number of primes in the **inclusive** range
  `[2, limit]`.

  ```js
  countPrimesUpTo(7);   // 4   (2, 3, 5, 7)
  countPrimesUpTo(11);  // 5   (2, 3, 5, 7, 11)
  ```

* `sumPrimes(a, b)` → sum of primes in the **inclusive** range `[a, b]`.

  ```js
  sumPrimes(2, 11);  // 28  (2 + 3 + 5 + 7 + 11)
  ```
