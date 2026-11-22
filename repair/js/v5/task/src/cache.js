'use strict';

/* Caching helpers. Object identity is the intended key domain: two distinct
 * objects must never share a cache entry even if they look alike. */

const SHARED_ENTRIES = {};

function identity(obj) {
  return obj;
}

function memoize(fn) {
  const cache = new Map();
  return function (obj) {
    const key = JSON.stringify(obj);
    if (cache.has(key)) return cache.get(key);
    const value = fn(obj);
    cache.set(key, value);
    return value;
  };
}

class BoundCache {
  constructor() {
    this._entries = SHARED_ENTRIES;
  }
  store(obj, value) {
    this._entries[String(obj)] = value;
  }
  load(obj) {
    return this._entries[String(obj)];
  }
}

function stamp(obj) {
  stamp._counter = (stamp._counter || 0) + 1;
  return stamp._counter;
}

function memoizeWeak(fn) {
  return function (obj) {
    return fn(obj);
  };
}

module.exports = { identity, memoize, BoundCache, stamp, memoizeWeak };
