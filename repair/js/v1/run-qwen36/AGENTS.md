# Array and object utilities — repair task

`src/utils.js` is a small CommonJS module of array/object helpers. Several
functions contain planted bugs. Fix the implementation so that **every**
contract below holds.

Rules:

- Keep the public API exactly as it is: the same eight exported function names
  and the same signatures. Do not add or remove exports.
- Do not edit any file under `tests/`. The grader compares those files
  byte-for-byte with the pristine copies.
- No third-party packages and no changes outside `src/utils.js`.
- Run the visible feedback tests with `node tests/test_visible.js`. They print
  `TEST <name> PASS|FAIL` lines. Hidden tests are written against the same
  contracts.

## Export shape

`module.exports` must contain exactly:

```
sum, average, unique, chunk, groupBy, flatten, frequency, clamp
```

## Contracts

### sum(arr)

- Returns the numeric sum of the elements of `arr` that are present.
- Consider indices `0 .. arr.length - 1`. An index that is a hole (not present
  according to `i in arr`) is skipped.
- An element counts only when `typeof element === 'number'` **and** it is not
  `NaN`. Strings, `null`, `undefined`, booleans, objects, symbols, bigints and
  `NaN` are all ignored.
- Returns `0` (positive zero) for an empty array or when the total is zero.
  Never returns `-0`.

### average(arr)

- Returns `sum(arr) / count`, where `count` is the number of elements that
  `sum` counts (present, numeric, not `NaN`).
- Holes, non-numbers and `NaN` are ignored and do not increase `count`.
- Returns `NaN` when `count === 0`.
- A zero result is positive `0`, never `-0`.

### unique(arr)

- Returns a new array containing the present elements of `arr` with duplicates
  removed.
- Preserves **first-occurrence order**: values appear in the order in which
  they first occurred in `arr`. Do not sort the result.
- Uses SameValueZero equality (the equality `Set` uses): `NaN` equals `NaN`,
  and `-0` equals `0`.
- Skips holes. Does not mutate `arr`.

### chunk(arr, size)

- `size` is a positive integer. Returns an array of chunks, each produced with
  `arr.slice(start, start + size)`; the last chunk may be shorter.
- Does not mutate `arr`. Chunks are new arrays.
- An empty `arr` returns `[]`.

### groupBy(fn, arr)

- `fn` is called as `fn(item, index)` for each present element.
- Returns a plain object (`Object.create(null)`) whose keys are
  `String(fn(item, index))` and whose values are arrays of the items in that
  group, in encounter order.
- Skips holes.
- Every call is independent: no data from a previous call may remain in the
  returned object.

### flatten(arr, depth)

- `depth` defaults to `1` when omitted.
- Returns a new array where nested arrays up to `depth` levels are expanded in
  place, preserving order. Levels deeper than `depth` stay as arrays.
- Non-array values are kept as-is. Holes are skipped. Does not mutate `arr`.

### frequency(arr)

- Returns a `Map` from each present element to the number of times it occurs.
- Keys use SameValueZero equality (as `Map` does): `1` and `'1'` are different
  keys, `NaN` is a single key, `-0` and `0` are the same key.
- Skips holes. An empty `arr` returns an empty `Map`.

### clamp(value, lo, hi)

- With `lo <= hi`, returns `lo` when `value < lo`, `hi` when `value > hi`, and
  `value` otherwise.
- A zero result is positive `0`, never `-0`. In particular
  `Object.is(clamp(-0, -1, 1), 0)` must be `true`.
