'use strict';
const { MiniVM, restore } = require('../src/index.js');
const good = MiniVM.fromSource('let x = 5; print x + 1;').snapshot();
const bad = Buffer.from(good);
bad[bad.length - 1] = bad[bad.length - 1] ^ 1;
let out = '';
try {
  restore(bad);
} catch (e) {
  out = e.message + '\n';
}
process.stdout.write(out);
