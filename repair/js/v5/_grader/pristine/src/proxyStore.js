'use strict';

/* Proxy-backed stores used by the settings layer. Each factory returns a
 * Proxy whose traps define the observable behaviour documented in README. */

function createPlainStore() {
  return {};
}

function countingGet() {
  const target = {};
  return new Proxy(target, {
    get(t, key) {
      if (key in t) return t[key];
      return undefined;
    }
  });
}

function numericSet() {
  const target = {};
  return new Proxy(target, {
    set(t, key, value) {
      t[key] = value;
      return true;
    }
  });
}

function strictHas() {
  const target = {};
  return new Proxy(target, {
    has() {
      return true;
    }
  });
}

function listedKeys() {
  const target = { a: 1, b: 'x', c: 2 };
  return new Proxy(target, {
    ownKeys(t) {
      return Object.keys(t);
    }
  });
}

function resettable() {
  const target = {};
  return new Proxy(target, {
    deleteProperty(t, key) {
      delete t[key];
      return true;
    }
  });
}

function descriptorProxy() {
  const target = { v: 7 };
  return new Proxy(target, {
    getOwnPropertyDescriptor(t, key) {
      return Reflect.getOwnPropertyDescriptor(t, key);
    }
  });
}

module.exports = {
  createPlainStore, countingGet, numericSet, strictHas,
  listedKeys, resettable, descriptorProxy
};
