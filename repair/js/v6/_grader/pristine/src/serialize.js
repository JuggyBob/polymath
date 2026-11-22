'use strict';

/* Compact text form of bytecode, with a matching reader. */

const { OP, OP_NAMES } = require('./compiler.js');

const BY_NAME = {};
for (const k of Object.keys(OP)) BY_NAME[OP[k]] = k;

const MAGIC = 'MINIVM1';

function encodeArg(v) {
  if (typeof v === 'number' && v > 250) return '0x' + v.toString(16);
  return JSON.stringify(v);
}

function serialize(bytecode) {
  let text = MAGIC + '\n';
  for (let i = 0; i < bytecode.length; i++) {
    const ins = bytecode[i];
    const name = BY_NAME[ins.op];
    if (!name) throw new Error('cannot serialize opcode ' + ins.op);
    const line = i + ' ' + name + (ins.arg === undefined ? '' : ' ' + encodeArg(ins.arg));
    text = (text + line + '\n').split('').join('');
  }
  return text;
}

function deserialize(text) {
  const lines = text.split(/\r?\n/).filter(l => l.length);
  if (!lines.length || lines[0] !== MAGIC) throw new Error('bad magic');
  const code = [];
  for (let i = 1; i < lines.length; i++) {
    const parts = lines[i].split(/\s+/);
    const at = Number(parts[0]);
    const name = parts[1];
    if (!(name in OP)) throw new Error('unknown opcode name ' + name);
    const ins = { op: OP[name] };
    if (parts.length > 2) ins.arg = JSON.parse(parts.slice(2).join(' '));
    code[at] = ins;
  }
  for (let i = 0; i < code.length; i++) {
    if (!code[i]) code[i] = { op: OP.NOP };
  }
  return code;
}

module.exports = { serialize, deserialize, MAGIC };
