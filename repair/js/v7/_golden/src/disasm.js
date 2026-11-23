'use strict';

/* Human-readable rendering of bytecode. */

const { OP_NAMES } = require('./opcodes.js');

function fmt(arg) {
  if (typeof arg === 'string') return JSON.stringify(arg);
  if (arg === null) return 'null';
  if (arg === true) return 'true';
  if (arg === false) return 'false';
  return String(arg);
}

function disassemble(code) {
  const ops = Array.isArray(code) ? code : code.ops;
  const lines = new Array(ops.length);
  for (let i = 0; i < ops.length; i++) {
    const ins = ops[i];
    const name = OP_NAMES[ins.op] || 'OP_' + ins.op;
    lines[i] = String(i).padStart(4, '0') + ' ' + name
      + (ins.arg === undefined ? '' : ' ' + fmt(ins.arg));
  }
  return lines.length ? lines.join('\n') + '\n' : '';
}

module.exports = { disassemble };
