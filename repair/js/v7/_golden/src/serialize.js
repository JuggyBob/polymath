'use strict';

/* Compact text form of bytecode, with a matching reader. */

const { OP_NAMES } = require('./opcodes.js');

const MAGIC = 'MINIVM7';
const BY_NAME = Object.create(null);
for (let i = 0; i < OP_NAMES.length; i++) BY_NAME[OP_NAMES[i]] = i;

function serialize(code) {
  const lines = [MAGIC, 'G ' + JSON.stringify(code.globals || [])];
  const ops = code.ops;
  for (let i = 0; i < ops.length; i++) {
    const ins = ops[i];
    const name = OP_NAMES[ins.op];
    if (!name) throw new Error('cannot serialize opcode ' + ins.op);
    lines.push(i + ' ' + name + (ins.arg === undefined ? '' : ' ' + JSON.stringify(ins.arg)));
  }
  return lines.join('\n') + '\n';
}

function deserialize(text) {
  const lines = text.split(/\r?\n/).filter(l => l.length);
  if (!lines.length || lines[0] !== MAGIC) throw new Error('bad magic');
  let names = [];
  const ops = [];
  for (let i = 1; i < lines.length; i++) {
    const sp = lines[i].indexOf(' ');
    const head = sp < 0 ? lines[i] : lines[i].slice(0, sp);
    const rest = sp < 0 ? '' : lines[i].slice(sp + 1);
    if (head === 'G') { names = JSON.parse(rest); continue; }
    const at = Number(head);
    const q = rest.indexOf(' ');
    const name = q < 0 ? rest : rest.slice(0, q);
    if (!(name in BY_NAME)) throw new Error('unknown opcode name ' + name);
    const ins = { op: BY_NAME[name] };
    if (q >= 0) ins.arg = JSON.parse(rest.slice(q + 1));
    ops[at] = ins;
  }
  for (let i = 0; i < ops.length; i++) if (!ops[i]) ops[i] = { op: 0 };
  return { ops, globals: names, fibers: {} };
}

module.exports = { serialize, deserialize, MAGIC };
