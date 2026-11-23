'use strict';
const vm = require('../src/index.js');
const ALIAS = { Load: 'LOAD', Print: 'PRINT', Halt: 'HALT' };
const items = ['Load(0)', 'Print', 'Halt'];
const ops = items.map(item => {
  const m = /^(\w+)(?:\((.+)\))?$/.exec(item);
  const name = ALIAS[m[1]] || m[1];
  const op = vm.OP[name];
  if (op === undefined) throw new Error('unknown op ' + name);
  return m[2] === undefined ? { op } : { op, arg: Number(m[2]) };
});
process.stdout.write(vm.execute({ ops, globals: [], fibers: {} }));
