'use strict';

// Schedule one callback per value and resolve with the array of results.
function schedule(values, fn) {
  const calls = [];
  for (let i = 0; i < values.length; i++) {
    const val = values[i];
    calls.push(Promise.resolve().then(() => fn(val, i)));
  }
  return Promise.all(calls);
}

const index = new Map();

function lookup(key) {
  return index.get(key);
}

function buildIndex(items) {
  index.clear();
  for (const it of items) index.set(it.key, it.value);
}

module.exports = { schedule, lookup, buildIndex };
