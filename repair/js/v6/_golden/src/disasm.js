'use strict';

/* Human-readable rendering of bytecode. */

const { OP_NAMES } = require('./compiler.js');

function disassemble(bytecode) {
  const lines = [];
  for (let i = 0; i < bytecode.length; i++) {
    const ins = bytecode[i];
    const name = OP_NAMES[ins.op] || ('OP_' + ins.op);
    let line = String(i).padStart(4, '0') + ' ' + name;
    if (ins.arg !== undefined) {
      line += ' ' + (typeof ins.arg === 'string' ? ins.arg : JSON.stringify(ins.arg));
    }
    lines.push(line);
  }
  return lines.join('\n') + '\n';
}

module.exports = { disassemble };
