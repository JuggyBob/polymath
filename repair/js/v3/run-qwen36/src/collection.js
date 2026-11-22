'use strict';

// Generator yielding the integers 0 .. n-1.
function* sequence(n) {
  for (let i = 0; i < n; i++) yield i;
}

function getSequence() {
  return sequence(3);
}

// Yield every element of every input array, not the arrays themselves.
function* flatten(arrays) {
  for (const arr of arrays) {
    for (const item of arr) {
      yield item;
    }
  }
}

// Return a NEW array with `value` appended. The input must not change.
function append(arr, value) {
  return [...arr, value];
}

// Group items by key. Each group must be its own independent array.
function groupBy(items, keyFn) {
  const out = {};
  for (const item of items) {
    const k = keyFn(item);
    if (!out[k]) {
      out[k] = [];
    }
    out[k].push(item);
  }
  return out;
}

module.exports = { getSequence, flatten, append, groupBy };
