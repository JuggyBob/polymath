'use strict';

class Emitter {
  constructor() {
    this._listeners = [];
  }

  on(fn) {
    this._listeners.push(fn);
    return this;
  }

  once(fn) {
    const wrapped = function (...args) {
      fn.apply(this, args);
      const idx = this._listeners.indexOf(wrapped);
      if (idx !== -1) this._listeners.splice(idx, 1);
    };
    this._listeners.push(wrapped);
    return this;
  }

  emit(...args) {
    for (const fn of this._listeners.slice()) fn(...args);
  }

  emitSnapshot(...args) {
    const snapshot = this._listeners.slice();
    for (let i = 0; i < snapshot.length; i++) {
      snapshot[i](...args);
    }
  }

  async emitAsync(...args) {
    await Promise.all(this._listeners.map(fn => fn(...args)));
  }

  count() {
    return this._listeners.length;
  }
}

module.exports = { Emitter };
