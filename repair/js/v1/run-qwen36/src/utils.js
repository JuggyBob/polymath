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
  for (let i = 0; i < arr.length; i++) {
    if (!(i in arr)) continue;
    const v = arr[i];
    if (typeof v !== 'number' || Number.isNaN(v)) continue;
    total += v;
  }
  return total || 0;
}

function average(arr) {
  let total = 0;
  let count = 0;
  for (let i = 0; i < arr.length; i++) {
    if (!(i in arr)) continue;
    const v = arr[i];
    if (typeof v !== 'number' || Number.isNaN(v)) continue;
    total += v;
    count++;
  }
  if (count === 0) return NaN;
  return total / count || 0;
}

function unique(arr) {
  const out = [];
  for (let i = 0; i < arr.length; i++) {
    if (!(i in arr)) continue;
    if (!out.includes(arr[i])) out.push(arr[i]);
  }
  return out;
}

function chunk(arr, size) {
  const out = [];
  for (let i = 0; i < arr.length; i += size) {
    out.push(arr.slice(i, i + size));
  }
  return out;
}

function groupBy(fn, arr) {
  const out = Object.create(null);
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
  const m = new Map();
  for (let i = 0; i < arr.length; i++) {
    if (!(i in arr)) continue;
    const x = arr[i];
    if (m.has(x)) {
      m.set(x, m.get(x) + 1);
    } else {
      m.set(x, 1);
    }
  }
  return m;
}

function clamp(value, lo, hi) {
  if (value < lo) return lo;
  if (value > hi) return hi;
  return value === 0 ? 0 : value;
}

module.exports = { sum, average, unique, chunk, groupBy, flatten, frequency, clamp };
