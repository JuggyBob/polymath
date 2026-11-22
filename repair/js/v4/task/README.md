# Strata repair fixture v4

A CommonJS package covering async iterators, streams, WeakMap caches,
module-cycle-like lazy initialization, event ordering, closure scope and a
lookup performance contract.

## Layout

- `src/async.js` — async collection and chunking.
- `src/streams.js` — ordered async mapping, error propagation, a buffer.
- `src/cache.js` — identity caches and a stored-value cache.
- `src/lazy.js` — explicit initialization and a lazily registered handler.
- `src/events.js` — a small event emitter with four delivery modes.
- `src/scope.js` — deferred callbacks and an indexed lookup.

## Running the tests

```sh
node tests/test_visible.js
```

Every visible check passes on the starting code. Hidden tests exercise the
edge cases described in `AGENTS.md`; those are the ones that fail until the
code is repaired. A complete fix makes all visible and hidden checks pass.

## Performance

`src/scope.js` has an explicit contract: 100,000 lookups over a 10,000-entry
index must complete in under two seconds. Hidden tests measure this.
