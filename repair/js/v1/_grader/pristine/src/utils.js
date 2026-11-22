'use strict';

/* Array and object utilities.
 * Several implementations below contain planted bugs. Fix the code so that
 * every contract in AGENTS.md holds, without changing the exported API.
 */

function isNumeric(x) {
  return typeof x === 'number' && !Number.isNaN(x);
}

function sum(arr) {
  let total = 0;
  // BUG: walks every index, including holes and non-numeric values.
  for (let i = 0; i < arr.length; i++) total += arr[i];
  return total;
}

function average(arr) {
  if (arr.length === 0) return NaN;
  // BUG: reduces without filtering and divides by the raw array length.
  const total = arr.reduce((a, b) => a + b, 0);
  return total / arr.length;
}

function unique(arr) {
  // BUG: the default sort is lexicographic and also destroys input order.
  return arr.slice().sort().filter((x, i, a) => a.indexOf(x) === i);
}

function chunk(arr, size) {
  // BUG: splices the caller's array while iterating it.
  const out = [];
  const work = arr;
  while (work.length) out.push(work.splice(0, size));
  return out;
}

let sharedGroups; // BUG: state leaks from one call to the next.
function groupBy(fn, arr) {
  const out = sharedGroups || (sharedGroups = Object.create(null));
  for (let i = 0; i < arr.length; i++) {
    if (!(i in arr)) continue;
    const key = String(fn(arr[i], i));
    if (!out[key]) out[key] = [];
    out[key].push(arr[i]);
  }
  return out;
}

function flatten(arr, depth) {
  if (depth === undefined) depth = 1;
  const out = [];
  for (let i = 0; i < arr.length; i++) {
    if (!(i in arr)) continue;
    const x = arr[i];
    if (Array.isArray(x) && depth > 0) out.push(...flatten(x, depth - 1));
    else out.push(x);
  }
  return out;
}

function frequency(arr) {
  const pairs = [];
  for (let i = 0; i < arr.length; i++) {
    if (!(i in arr)) continue;
    const x = arr[i];
    let found = null;
    // BUG: loose equality merges 1 with '1' and never merges NaN with NaN.
    for (const p of pairs) if (p.key == x) { found = p; break; }
    if (found) found.count++; else pairs.push({ key: x, count: 1 });
  }
  const m = new Map();
  for (const p of pairs) m.set(p.key, p.count);
  return m;
}

function clamp(value, lo, hi) {
  // BUG: returns -0 unchanged.
  return value < lo ? lo : (value > hi ? hi : value);
}

module.exports = { sum, average, unique, chunk, groupBy, flatten, frequency, clamp };
