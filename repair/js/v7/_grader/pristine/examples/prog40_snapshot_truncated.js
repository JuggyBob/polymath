'use strict';
const { MiniVM, restore } = require('../src/index.js');
const good = MiniVM.fromSource('let x = 5; print x + 1;').snapshot();
let out = '';
try {
  restore(good.subarray(0, good.length - 3));
} catch (e) {
  out = e.message + '\n';
}
process.stdout.write(out);
