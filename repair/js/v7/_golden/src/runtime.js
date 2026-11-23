'use strict';

/* Value helpers shared by the VM, disassembler and serialiser. */

function toStr(v) {
  if (v === null || v === undefined) return 'null';
  if (Array.isArray(v)) return '[' + v.map(toStr).join(', ') + ']';
  if (v === true) return 'true';
  if (v === false) return 'false';
  return String(v);
}

function truthy(v) {
  if (v === null || v === undefined || v === false) return false;
  if (v === 0) return false;
  if (v === '') return false;
  if (Array.isArray(v) && v.length === 0) return false;
  return true;
}

function valuesEqual(a, b) {
  if (a === null || a === undefined) return b === null || b === undefined;
  if (b === null || b === undefined) return false;
  if (Array.isArray(a) || Array.isArray(b)) {
    if (!Array.isArray(a) || !Array.isArray(b)) return false;
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) if (!valuesEqual(a[i], b[i])) return false;
    return true;
  }
  return typeof a === typeof b && a === b;
}

function isDistinct(arr) {
  if (!Array.isArray(arr)) return true;
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (valuesEqual(arr[i], arr[j])) return false;
    }
  }
  return true;
}

function strLen(v) {
  if (typeof v === 'string') return Array.from(v).length;
  if (Array.isArray(v)) return v.length;
  return 0;
}

function compare(a, b, op) {
  if (typeof a !== typeof b || (typeof a !== 'number' && typeof a !== 'string')) {
    return false;
  }
  switch (op) {
    case '<': return a < b;
    case '<=': return a <= b;
    case '>': return a > b;
    case '>=': return a >= b;
    default: return false;
  }
}

module.exports = { toStr, truthy, valuesEqual, isDistinct, strLen, compare };
