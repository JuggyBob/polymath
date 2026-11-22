'use strict';

// A greeter whose greet method must keep working when the method is taken
// off the instance and called on its own.
class Greeter {
  constructor(name) {
    this.name = name;
    // BUG: the method is not bound, so `this` is lost when it is extracted.
  }

  greet() {
    return 'Hello, ' + this.name;
  }
}

// True when `key` can be reached on `obj` through its prototype chain.
function hasProperty(obj, key) {
  // BUG: only own properties are considered; inherited ones are ignored.
  return Object.prototype.hasOwnProperty.call(obj, key);
}

// Parent / Child prototype setup shared by the registry.
function Parent() {}
Parent.prototype.kind = 'parent';

function Child() {}
// BUG: shares Parent.prototype instead of inheriting from a fresh object.
Child.prototype = Parent.prototype;
Child.prototype.constructor = Child;

// Call `obj.method` with `obj` bound as its receiver.
function invoke(obj) {
  const m = obj.method;
  // BUG: calling m() directly drops the receiver.
  return m();
}

module.exports = { Greeter, hasProperty, Parent, Child, invoke };
