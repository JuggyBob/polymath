'use strict';

// Schedule one callback per value and resolve with the array of results.
function schedule(values, fn) {
  const calls = [];
  for (var i = 0; i < values.length; i++) {
    calls.push(Promise.resolve().then(() => fn(values[i], i)));
  }
  return Promise.all(calls);
}

const index = new Map();

function lookup(key) {
  for (const [k, v] of index) {
    if (k === key) return v;
  }
  return undefined;
}

function buildIndex(items) {
  index.clear();
  for (const it of items) index.set(it.key, it.value);
}

module.exports = { schedule, lookup, buildIndex };
