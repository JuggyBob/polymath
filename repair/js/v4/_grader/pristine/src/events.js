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
    const wrapped = function (...args) { return fn.apply(this, args); };
    this._listeners.push(wrapped);
    return this;
  }

  emit(...args) {
    for (const fn of this._listeners.slice().reverse()) fn(...args);
  }

  emitSnapshot(...args) {
    for (let i = 0; i < this._listeners.length; i++) {
      this._listeners[i](...args);
    }
  }

  async emitAsync(...args) {
    this._listeners.forEach(fn => fn(...args));
  }

  count() {
    return this._listeners.length;
  }
}

module.exports = { Emitter };
