# Repair task C++ v5 — a small concurrent task scheduler

Three frozen headers (`include/allocator.h`, `include/ring.h`,
`include/scheduler.h`), three translation units in `src/`. Every public rule is
below. The checked behaviour is a **superset** of the visible tests: all visible
tests pass on the starting source, so they tell you almost nothing about what is
broken.

```
cl /EHsc /nologo /Od /Iinclude src\*.cpp tests\test_visible.cpp
test_visible.exe
```

You may edit only `src/*.cpp`. Keep `include/*.h` and `tests/*` byte-for-byte.
Standard C++ only, no third-party libraries. There are no `# BUG:` markers;
find the defects from the contracts.

---

## 1. `AlignedPool` (`include/allocator.h`, `src/allocator.cpp`)

The pool is a fixed array of raw slots. The pool owns the bytes; it does **not**
own object lifetimes except through the explicit `create`/`release`/`clear`
calls.

- **Alignment.** The first slot starts on a 64-byte boundary:
  `reinterpret_cast<std::uintptr_t>(pool.slot(0)) % 64 == 0`. Slot `i` is at
  `slot(0) + i * slot_size`, so when `slot_size` is a multiple of 64 **every**
  slot is 64-byte aligned; with a smaller slot size only the base is aligned.
  Worked example: with `slot_size == 128`, `slot(0)`, `slot(1)`, `slot(2)`, … are
  all 64-byte aligned and 128 bytes apart. Ordinary `new` does not promise
  64-byte alignment; over-allocate and align the pointer by hand, and remember
  the original allocation base so `delete[]` releases that exact pointer.

- **Shape.** `capacity()` is the constructor capacity; `used()` is the number
  of live objects; `full()` is `used() == capacity()`.

- **`claim()`** reserves the next slot and returns its address. It returns
  `nullptr` when and only when the pool is already at capacity. Worked example:
  a pool of capacity 3 accepts three `claim()` calls; a fourth returns
  `nullptr` and `used()` is still 3.

- **`create(from, move_it)`** places a `Payload` in the next free slot (it uses
  placement new — the object lives in the pool's bytes, at the address
  `claim()` returned). If `from == nullptr` the object is default-constructed.
  If `from != nullptr` and `move_it == false`, the new object is a **copy**:
  `*from` must be completely unchanged and `PayloadStats::copies()` increases
  by one. If `from != nullptr` and `move_it == true`, the new object is
  **move-constructed**: `PayloadStats::moves()` increases by one and
  `from->moved_from` becomes `true`. Worked example:

  ```
  Payload a(42);
  AlignedPool p(sizeof(Payload), 4);
  Payload* x = p.create(&a, false);   // x->value == 42, a.moved_from == false
  Payload* y = p.create(&a, true);    // y->value == 42, a.moved_from == true
  ```

- **`release(p)`** runs `~Payload()` on `p` exactly once and drops `used()` by
  one. `PayloadStats::destructions()` increases by one.

- **`clear()`** runs `~Payload()` on **every** live object and sets `used()` to
  zero. Worked example: after `create` three times and `clear()`,
  `PayloadStats::destructions()` has grown by exactly three.

- **Move construction / move assignment of the pool itself.** After
  `AlignedPool b(std::move(a));`, object `b` owns every byte that `a` owned
  (its slots contain the same objects), and `a` is left **empty**:
  `a.capacity() == 0`, `a.used() == 0`, and `a.slot(0) == nullptr`. Destroying
  `a` must not affect `b`. The same empties-the-source rule applies to move
  assignment. Copy construction and copy assignment are deleted.

- **Allocation balance.** Every `new[]` the pool performs is matched by one
  `delete[]` of the same pointer across the pool's whole lifetime, including
  moved-from pools (an empty pool performs no deallocation).

---

## 2. `RingQueue` (`include/ring.h`, `src/ring.cpp`)

A single-producer / single-consumer ring. `head_` and `tail_` are monotonic
counters; the physical slot for a cursor `c` is `c & (capacity() - 1)`.

- **Capacity.** The constructor rounds the requested capacity **up to the next
  power of two** (a request of 0 becomes 1). `capacity()` reports the rounded
  value. Worked examples: `RingQueue(10).capacity() == 16`;
  `RingQueue(16).capacity() == 16`; `RingQueue(17).capacity() == 32`. The ring
  can hold exactly `capacity()` items — no slot is reserved to distinguish
  full from empty.

- **`size()`, `empty()`, `full()`.** `size()` is the number of stored items and
  **must be O(1)** (two atomic loads and a subtraction), including when the
  ring is completely full: pushing 16 items into a capacity-16 ring gives
  `size() == 16` and `full() == true`, not `0`/`false`. `empty()` is
  `size() == 0`. `full()` is `size() == capacity()`, so with capacity 16 the
  ring is **not** full after 15 pushes. Worked example:

  ```
  RingQueue q(4);            // capacity() == 4
  q.push_int(1); q.push_int(2); q.push_int(3);
  q.full()  -> false          // 3 < 4
  q.push_int(4);
  q.full()  -> true           // 4 == 4, every slot is usable
  q.size()  -> 4
  ```

- **`push_int` / `pop_int` are O(1)** and never call an O(n) helper. A workload
  of **1,000,000 operations** (one `push_int` and one `pop_int` per iteration
  on a small ring, with `size()` inspected each iteration) must finish in
  **under 2 seconds** on this machine. An O(n) item count makes this fail.

- **Push at capacity.** `push`, `push_int` return `false` and change **nothing**
  when the ring is full — the oldest item is not overwritten and no cursor
  moves. Worked example: fill a capacity-3 ring with 1,2,3; a fourth
  `push_int(99)` returns `false`; three pops still yield 1,2,3.

- **Pop at empty.** `pop`, `pop_int` return `false` and leave the output
  argument **untouched** when the ring is empty. Worked example: on a fresh
  ring, `int v = 777; q.pop_int(v) == false && v == 777`.

- **FIFO across wrap-around.** After enough pushes and pops to wrap the
  cursor, items still come out in insertion order and `size()` is exact.
  Worked example on capacity 4: push 1,2,3,4; pop 1,2; push 5,6; the buffer
  holds 3,4,5,6 (`size() == 4`, `full() == true`) and the next four pops give
  3,4,5,6.

- **Move semantics at the API boundary.** `push(const Payload&)` represents an
  lvalue argument: it must **copy** from the argument, leaving it completely
  unchanged (`moved_from` stays `false`). `push(Payload&&)` represents an
  rvalue argument: it must **move** from the argument, so the source becomes
  `moved_from == true` and `PayloadStats::moves()` increases. Do not use
  `std::move` on a `const&` parameter, and do not accidentally treat an rvalue
  parameter as an lvalue. Worked example:

  ```
  PayloadStats::reset();
  Payload a(5);
  q.push(a);                  // copies: a.moved_from == false, copies == 1
  q.push(Payload(6));         // moves:  moves  == 1
  ```

- **Memory ordering.** Data is written before the producer publishes the new
  `head_`, and the consumer acquires `head_` before reading the slot; the
  consumer publishes `tail_` only after it has read the slot. The cursors are
  already padded onto separate cache lines (that part is in the frozen
  header) — do not rely on the padding to make a mis-ordered publication
  correct.

---

## 3. `Scheduler` (`include/scheduler.h`, `src/scheduler.cpp`)

- **Submission.** `submit(fn, arg)` stores a task in FIFO order and returns
  `true`. It returns `false` and stores nothing once the table already holds
  `capacity()` tasks. Worked example: `Scheduler s(3);` accepts three submits;
  a fourth returns `false` and the three stored tasks are untouched.

- **Execution.** `run_all()` executes every not-yet-run task exactly once, in
  submission order, and returns how many it ran. Calling it a second time
  returns `0` and does **not** re-run or change any result. Worked example:
  with two tasks submitted, the first `run_all()` returns 2, the second
  returns 0.

- **Bookkeeping.** After running all tasks, `pending() == 0` and
  `completed() == number of submitted tasks`. `pending()` counts submitted but
  not-yet-run tasks; it is never derived from `capacity()`. Before any run, all
  submitted tasks are pending. `completed()` starts at 0. Worked example:
  submit 2 tasks → `pending() == 2, completed() == 0`; after `run_all()` →
  `pending() == 0, completed() == 2`.

- **Results.** `result(i)` returns the value produced by the `i`-th submitted
  task (index 0 is the first). `done(i)` reports whether that task has run.
  Worked example: `submit(twice,3); submit(plus5,10); run_all();` gives
  `result(0) == 6`, `result(1) == 15`, `done(0) && done(1)`.

- **`reset()`** clears all tasks and counters so the scheduler can be reused.

- **`clamp_int<T>(value, lo, hi)`** is enabled only for integral `T` (the
  `enable_if` lives in the frozen header). It returns `value` clamped into
  `[lo, hi]`, as a `long long`, without narrowing the value to `int` first.
  For unsigned `T`, a negative `lo` or `hi` is treated as 0. Worked examples:

  ```
  clamp_int<int>(5, 0, 10)        == 5
  clamp_int<int>(-3, 0, 10)       == 0
  clamp_int<unsigned>(4000000000u, 0, 100) == 100   // 4000000000 > INT_MAX
  clamp_int<unsigned>(7u, -5, 10) == 7                  // lo treated as 0
  ```

- **Prime helpers.** `is_prime_naive(n)` is the O(n) reference: keep it correct
  for every `int`. `is_prime_optimized(n)` must return **exactly the same
  answer** as `is_prime_naive(n)` for every `int n`, but in **O(sqrt(n))** time.
  All of these must hold, and they are all checked:

  ```
  is_prime_optimized(0)  == false
  is_prime_optimized(1)  == false
  is_prime_optimized(-7) == false
  is_prime_optimized(2)  == true
  is_prime_optimized(4)  == false,  9 -> false,  25 -> false
  is_prime_optimized(97) == true,  1000003 -> true
  is_prime_optimized(2147483647) == true        // INT_MAX, a prime
  is_prime_optimized(2147483646) == false       // large even composite
  ```

  Two consecutive calls with a large prime near `INT_MAX` (2147483647) must
  complete together in under **2 seconds**; the O(n) reference does not.
  **Scope trap:** simply changing
  the loop bound to `i * i <= n` with an `int i` overflows for arguments near
  `INT_MAX` (it can fail to terminate or give a wrong answer). Use a bound that
  cannot overflow (for example `i <= n / i`, or a 64-bit square), and keep the
  `n < 2`, `n == 2` edge cases. You may delete or simplify the naive helper's
  *callers*; the comparison harness still checks that the two agree.

---

## Notes

- The visible tests exercise only well-formed, non-degenerate cases. They are
  not a specification. Read the worked examples above.
- Not every loop is a defect. In particular, `Payload`'s copy/move counters are
  correct as written; the only performance contracts are `RingQueue::size()`
  (O(1)) and `is_prime_optimized` (O(sqrt(n))).
- The header-imposed cache-line padding, the `alignas` fields and the
  `enable_if` declaration are already correct; the defects are all in `src/`.
- Bugs are behavioural or performance only. The starting code compiles
  cleanly with the command at the top of this file.
