'use strict';

// A greeter whose greet method must keep working when the method is taken
// off the instance and called on its own.
class Greeter {
  constructor(name) {
    this.name = name;
    this.greet = this.greet.bind(this);
  }

  greet() {
    return 'Hello, ' + this.name;
  }
}

// True when `key` can be reached on `obj` through its prototype chain.
function hasProperty(obj, key) {
  return key in obj;
}

// Parent / Child prototype setup shared by the registry.
function Parent() {}
Parent.prototype.kind = 'parent';

function Child() {}
Child.prototype = Object.create(Parent.prototype);
Child.prototype.constructor = Child;

// Call `obj.method` with `obj` bound as its receiver.
function invoke(obj) {
  const m = obj.method;
  return m.call(obj);
}

module.exports = { Greeter, hasProperty, Parent, Child, invoke };
