'use strict';

const settings = { level: 1 };

const eagerValue = compute();

function compute() {
  return settings.level * 10;
}

function init() {
  settings.level = 2;
}

function getValue() {
  return eagerValue;
}

// A lazily registered handler, as in a circular module dependency: the
// binding is installed after the module is loaded and read during a call.
let cachedB = null;
function defaultB() { return 'B'; }
function b() { return cachedB || defaultB(); }
function a() { return 'A' + b(); }
function registerB(fn) { cachedB = fn; }

function getConfig() {
  return { level: settings.level };
}

module.exports = { init, compute, getValue, b, a, registerB, getConfig };
