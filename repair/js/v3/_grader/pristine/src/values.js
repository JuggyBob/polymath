'use strict';

const DEFAULTS = { retries: 3, tags: ['default'] };

// Return a clone whose `settings` object is independent of the input.
function cloneConfig(cfg) {
  // BUG: Object.assign is shallow, so `settings` stays shared.
  return Object.assign({}, cfg);
}

// Remove `key` from `obj` entirely.
function removeKey(obj, key) {
  // BUG: assigns undefined instead of deleting the property.
  obj[key] = undefined;
  return obj;
}

// Strict equality: 1 and '1' must not be considered the same.
function same(a, b) {
  // BUG: loose equality coerces the operands.
  return a == b;
}

// Apply defaults without letting callers mutate the shared tag list.
function withDefaults(opts) {
  // BUG: the object spread copies the `tags` array by reference.
  return { ...DEFAULTS, ...opts };
}

module.exports = { DEFAULTS, cloneConfig, removeKey, same, withDefaults };
