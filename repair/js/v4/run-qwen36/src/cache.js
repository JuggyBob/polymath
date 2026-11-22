'use strict';

// Return the process-wide double cache. Repeated calls must share it.
const _cache = new WeakMap();
function getCache() {
  return _cache;
}

function cachedDouble(obj) {
  const cache = getCache();
  if (cache.has(obj)) return cache.get(obj);
  const value = obj.n * 2;
  cache.set(obj, value);
  return value;
}

// A bucket cache. Buckets are keyed by the identity of the object passed in.
const byId = new WeakMap();
function cacheFor(obj) {
  if (!byId.has(obj)) byId.set(obj, []);
  return byId.get(obj);
}

// Store a value for an object and read it back later.
const store = new WeakMap();
function put(obj, value) {
  store.set(obj, value);
}
function read(obj) {
  return store.get(obj);
}

module.exports = { getCache, cachedDouble, cacheFor, put, read };
