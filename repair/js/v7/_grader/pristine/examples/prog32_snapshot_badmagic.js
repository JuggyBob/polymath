'use strict';
const { restore } = require('../src/index.js');
let out = '';
try {
  const bytes = Buffer.concat([Buffer.from('XXXX'), Buffer.alloc(32)]);
  restore(bytes);
} catch (e) {
  out = e.message + '\n';
}
process.stdout.write(out);
