# Repair task

The `src/` directory contains a small CommonJS package. Its public API is
documented below. Some functions do not meet that documentation. Fix the
source files so that every documented behaviour holds.

## Rules

- Edit only files under `src/`. Do not change `tests/` or add files.
- Run the visible tests with `node tests/test_visible.js`. Every visible check
  passes at the start; they cover the basic paths only. Hidden tests cover the
  edge cases listed below and will fail until the code is fixed.
- Keep the exported names, signatures and module style (CommonJS, Node 24).
- There are sixteen incorrect behaviours. No source line is marked, so read
  the specification carefully.

## Required behaviour by module

### `src/async.js`

- `collect(iterable, expected)` returns an array of the first `expected`
  values of an **async** iterable, in the order the iterator yields them.
  Each `next()` result must be awaited before its `value` is read.
- `chunk(values, size)` is an async generator. It yields consecutive arrays
  of at most `size` items. A final short chunk must still be yielded, and a
  `size` larger than the input yields one chunk containing the whole input.

### `src/streams.js`

- `mapOrdered(items, mapper)` maps with an async function and returns results
  in **input order**, no matter how long each mapper call takes.
- `pipe(source, transform)` forwards every source value through `transform`
  and must let a thrown error reach the caller (it does not return partial
  output on error).
- `createBuffer()` returns a buffer. `close()` marks it closed; `isClosed()`
  then returns true and later `push()` calls are ignored. `drain()` returns
  and clears the contents.

### `src/cache.js`

- `getCache()` returns one process-wide WeakMap shared by all callers.
- `cachedDouble(obj)` caches by object identity: after the first call the
  cached value is returned even if `obj.n` changes.
- `cacheFor(obj)` returns a per-object bucket array. Two different objects
  must get different arrays even if they share an `id` property, and changing
  `obj.id` must not switch its bucket.
- `put(obj, value)` stores a value; `read(obj)` returns the last stored value.

### `src/lazy.js`

- `getValue()` must reflect the current settings after `init()` has run; it is
  not a value frozen at module load.
- `registerB(fn)` installs a handler used by `b()` on subsequent calls, as in
  a circular module dependency resolved lazily. `b()` must call that handler;
  before registration it returns the string `'B'`.

### `src/events.js`

- `Emitter.emit()` calls listeners in registration order and forwards all
  arguments.
- `once(fn)` registers a listener that fires at most once and is then removed.
- `emitSnapshot()` calls only the listeners registered when the call starts;
  a listener added during the call must wait for the next emit.
- `emitAsync()` awaits every (possibly async) listener before resolving.

### `src/scope.js`

- `schedule(values, fn)` resolves with one result per value; each callback
  must see its own value and own index even though the callbacks run later.
- `lookup(key)` must serve 100,000 lookups over a 10,000-entry index in under
  two seconds. `buildIndex(items)` replaces the index contents.
