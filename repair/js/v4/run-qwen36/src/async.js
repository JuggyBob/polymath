'use strict';

// Collect exactly `expected` values from an async iterable, in yield order.
async function collect(iterable, expected) {
  const out = [];
  const it = iterable[Symbol.asyncIterator]();
  for (let i = 0; i < expected; i++) {
    const step = await it.next();
    out.push(step.value);
  }
  return out;
}

// Split values into consecutive chunks of at most `size`. When the input
// length is not a multiple of `size`, the last chunk holds the leftovers.
async function* chunk(values, size) {
  for (let i = 0; i < values.length; i += size) {
    yield values.slice(i, i + size);
  }
}

module.exports = { collect, chunk };
