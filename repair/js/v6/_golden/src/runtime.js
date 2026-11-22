'use strict';

/* Small runtime helpers with JavaScript-specific behaviour. */

function toStr(v) {
  if (v === null) return 'null';
  if (v === undefined) return 'undefined';
  if (Array.isArray(v)) return '[' + v.map(toStr).join(', ') + ']';
  return String(v);
}

function truthy(v) {
  if (v === null || v === undefined) return false;
  if (Array.isArray(v)) return true;
  return !!v;
}

/* Identity cache: two different objects never share an entry. */
const _identityCache = new WeakMap();
function cachedValue(obj, compute) {
  let v = _identityCache.get(obj);
  if (v === undefined) {
    v = compute(obj);
    _identityCache.set(obj, v);
  }
  return v;
}

function sumRange(n) {
  let total = 0;
  for (let i = 0; i < n; i++) total += i;
  return total;
}

function methodCall(obj, name) {
  const fn = obj[name];
  const args = Array.prototype.slice.call(arguments, 2);
  return fn.apply(obj, args);
}

function collectGen(gen) {
  const out = [];
  for (const v of gen) out.push(v);
  return out;
}

/* Chain microtasks so registration order is preserved. */
function orderedMicrotasks(items) {
  const out = [];
  let chain = Promise.resolve();
  for (const item of items) {
    chain = chain.then(() => { out.push(item); return item; });
  }
  return chain.then(() => out);
}

function proxyArray(arr) {
  return new Proxy(arr, {
    get(target, prop, receiver) {
      return Reflect.get(target, prop, receiver);
    },
    set(target, prop, value, receiver) {
      return Reflect.set(target, prop, value, receiver);
    },
    has(target, prop) {
      return Reflect.has(target, prop);
    }
  });
}

function distinctValues(arr) {
  const seen = new Set();
  const out = [];
  for (const v of arr) {
    if (!seen.has(v)) { seen.add(v); out.push(v); }
  }
  return out;
}

module.exports = {
  toStr, truthy, cachedValue, sumRange, methodCall, collectGen,
  orderedMicrotasks, proxyArray, distinctValues
};
