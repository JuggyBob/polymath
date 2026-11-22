# Strata repair fixture v3

A small CommonJS package with twelve planted bugs in the areas of prototypes,
`this` binding, generators, and aliasing / reference semantics.

## Layout

- `src/objects.js` — greeter binding, prototype-chain lookup, Parent/Child
  prototypes, and method invocation with a receiver.
- `src/collection.js` — integer generators, array flattening, immutable append,
  and grouping without shared buckets.
- `src/values.js` — cloning, key removal, equality, and defaults merging.

## Running the tests

```sh
node tests/test_visible.js
```

The output is one line per check: `TEST <name> PASS` or `TEST <name> FAIL`.
On the starting code some visible checks fail. A complete fix makes every
visible and hidden check pass.

## Public API

Each module exports the functions named in its source. Keep those names and
their call signatures unchanged; only the behaviour is wrong at the start.
