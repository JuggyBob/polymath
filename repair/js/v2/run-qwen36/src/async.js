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
  for (let i = 0; i < retries + 1; i++) {
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
    Promise.resolve(promise).then(
      (v) => { clearTimeout(t); resolve(v); },
      (e) => { clearTimeout(t); reject(e); }
    );
  });
}

async function mapLimit(items, limit, mapper) {
  const out = new Array(items.length);
  let cursor = 0;
  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (cursor < items.length) {
      const i = cursor++;
      const v = await mapper(items[i], i);
      out[i] = v;
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
    this._events.set(name, list.filter((e) => e.orig !== fn));
    return this;
  }

  emit(name, ...args) {
    const list = (this._events.get(name) || []).slice();
    let called = false;
    for (const e of list) {
      called = true;
      if (e.once) {
        const idx = list.indexOf(e);
        if (idx !== -1) this._events.get(name).splice(idx, 1);
      }
      e.fn.call(this, ...args);
    }
    return called;
  }
}

function debounce(fn, wait) {
  let timer = null;
  return function (...args) {
    const ctx = this;
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => { timer = null; fn.apply(ctx, args); }, wait);
  };
}

function memoizeAsync(fn, keyFn) {
  const pick = keyFn || ((...a) => a[0]);
  const cache = new Map();
  return async function (...args) {
    const key = pick(...args);
    if (cache.has(key)) return cache.get(key);
    const p = fn.apply(this, args).then((v) => { cache.set(key, v); return v; });
    cache.set(key, p);
    return p;
  };
}

function promisePool(items, limit, worker) {
  const results = new Array(items.length);
  let cursor = 0;
  const runners = [];
  for (let i = 0; i < Math.min(limit, items.length); i++) {
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
