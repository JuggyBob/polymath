'use strict';

// Generator yielding the integers 0 .. n-1.
function* sequence(n) {
  for (let i = 0; i < n; i++) yield i;
}

// BUG: one generator instance is shared, so a second caller receives an
// already exhausted generator.
const sharedSequence = sequence(3);
function getSequence() {
  return sharedSequence;
}

// Yield every element of every input array, not the arrays themselves.
function* flatten(arrays) {
  for (const arr of arrays) {
    // BUG: yields the whole array as a single value.
    yield arr;
  }
}

// Return a NEW array with `value` appended. The input must not change.
function append(arr, value) {
  // BUG: pushes onto the caller's array.
  arr.push(value);
  return arr;
}

// Group items by key. Each group must be its own independent array.
function groupBy(items, keyFn) {
  const out = {};
  const bucket = [];
  for (const item of items) {
    const k = keyFn(item);
    if (!out[k]) {
      // BUG: all groups point at the same bucket array.
      out[k] = bucket;
    }
    out[k].push(item);
  }
  return out;
}

module.exports = { getSequence, flatten, append, groupBy };
