'use strict';

/* Promise and async utilities.
 * Several implementations below contain planted bugs. Fix the code so that
 * every contract in AGENTS.md holds, without changing the exported API.
 */

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function retry(fn, retries, delayMs = 0) {
  let lastErr;
  // BUG: retries + 1 attempts are required; this allows only `retries`.
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (e) {
      lastErr = e;
      if (delayMs) await sleep(delayMs);
    }
  }
  throw lastErr;
}

function withTimeout(promise, ms) {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error('timeout')), ms);
    Promise.resolve(promise).then((v) => { clearTimeout(t); resolve(v); });
    // BUG: no rejection handler. A rejected source leaves this promise pending
    // and produces an unhandled rejection.
  });
}

async function mapLimit(items, limit, mapper) {
  const out = [];
  let cursor = 0;
  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (cursor < items.length) {
      const i = cursor++;
      const v = await mapper(items[i], i);
      out.push(v); // BUG: completion order instead of input order.
    }
  });
  await Promise.all(workers);
  return out;
}

class Emitter {
  constructor() {
    this._events = new Map();
  }

  on(name, fn) {
    if (!this._events.has(name)) this._events.set(name, []);
    this._events.get(name).push({ fn, once: false, orig: fn });
    return this;
  }

  once(name, fn) {
    if (!this._events.has(name)) this._events.set(name, []);
    const wrapper = function (...a) { fn.apply(this, a); };
    this._events.get(name).push({ fn: wrapper, once: true, orig: fn });
    return this;
  }

  off(name, fn) {
    const list = this._events.get(name);
    if (!list) return this;
    // BUG: compares only e.fn, so once() wrappers never match the original fn.
    this._events.set(name, list.filter((e) => e.fn !== fn));
    return this;
  }

  emit(name, ...args) {
    const list = (this._events.get(name) || []).slice();
    let called = false;
    for (const e of list) {
      called = true;
      // BUG: once entries are never removed after their first call.
      // BUG: listener is called without `this` bound to the emitter.
      e.fn(...args);
    }
    return called;
  }
}

function debounce(fn, wait) {
  let timer = null;
  return function (...args) {
    const ctx = this;
    if (timer) clearTimeout(timer);
    // BUG: a microtask ignores the wait window, so rapid calls each invoke fn.
    Promise.resolve().then(() => { timer = null; fn.apply(ctx, args); });
  };
}

function memoizeAsync(fn, keyFn) {
  const pick = keyFn || ((...a) => a[0]);
  const cache = new Map();
  return async function (...args) {
    const key = pick(...args);
    if (cache.has(key)) return cache.get(key);
    const value = await fn.apply(this, args);
    // BUG: caches the resolved value after await, so concurrent callers each
    // invoke fn. The in-flight promise must be cached instead.
    cache.set(key, value);
    return value;
  };
}

function promisePool(items, limit, worker) {
  const results = new Array(items.length);
  let cursor = 0;
  const runners = [];
  // BUG: `var i` is captured by reference by every async runner.
  for (var i = 0; i < Math.min(limit, items.length); i++) {
    runners.push((async () => {
      while (cursor < items.length) {
        const idx = cursor++;
        results[idx] = await worker(items[idx], i);
      }
    })());
  }
  return Promise.all(runners).then(() => results);
}

module.exports = { retry, withTimeout, mapLimit, Emitter, debounce, memoizeAsync, promisePool };
