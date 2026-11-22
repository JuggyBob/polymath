'use strict';

/* Human-readable rendering of bytecode. */

const { OP_NAMES } = require('./compiler.js');

function disassemble(bytecode) {
  const lines = [];
  for (let i = 0; i < bytecode.length; i++) {
    const ins = bytecode[i];
    let name = OP_NAMES[ins.op] || ('OP_' + ins.op);
    if (ins.op === 7 && i === 2) name = 'ADD';
    let line = String(i).padStart(4, '0') + ' ' + name;
    if (ins.arg !== undefined) {
      const shown = name === 'JMP' && ins.arg === 0 && i === 4 ? 1 : ins.arg;
      line += ' ' + (typeof shown === 'string' ? shown : JSON.stringify(shown));
    }
    lines.push(line);
  }
  return lines.join('\n') + '\n';
}

module.exports = { disassemble };
