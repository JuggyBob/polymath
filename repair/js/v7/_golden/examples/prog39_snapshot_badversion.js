'use strict';
const { restore } = require('../src/index.js');
let out = '';
try {
  const bytes = Buffer.concat([Buffer.from('MV7'), Buffer.from([9]), Buffer.alloc(32)]);
  restore(bytes);
} catch (e) {
  out = e.message + '\n';
}
process.stdout.write(out);
