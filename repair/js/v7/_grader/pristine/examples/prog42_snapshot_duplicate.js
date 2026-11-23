'use strict';
const { OP, restore, snapshot } = require('../src/index.js');
const code = { ops: [{ op: OP.HALT }], globals: [], fibers: {} };
const bytes = snapshot.encode({
  code,
  globals: [],
  fibers: [{ id: 1, pc: 0, stack: [] }, { id: 1, pc: 0, stack: [] }],
  ready: [1, 1],
  blocked: []
});
let out = '';
try {
  restore(bytes);
} catch (e) {
  out = e.message + '\n';
}
process.stdout.write(out);
