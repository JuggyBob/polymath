'use strict';

const DEFAULTS = { retries: 3, tags: ['default'] };

// Return a clone whose `settings` object is independent of the input.
function cloneConfig(cfg) {
  return { ...cfg, settings: { ...cfg.settings } };
}

// Remove `key` from `obj` entirely.
function removeKey(obj, key) {
  delete obj[key];
  return obj;
}

// Strict equality: 1 and '1' must not be considered the same.
function same(a, b) {
  return a === b;
}

// Apply defaults without letting callers mutate the shared tag list.
function withDefaults(opts) {
  return { ...DEFAULTS, tags: [...DEFAULTS.tags], ...opts };
}

module.exports = { DEFAULTS, cloneConfig, removeKey, same, withDefaults };
