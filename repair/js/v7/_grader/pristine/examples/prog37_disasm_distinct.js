'use strict';
const { compileSource, disassemble } = require('../src/index.js');
const code = compileSource('print distinct([1, 2]);');
const text = disassemble(code);
process.stdout.write(text.includes('DISTINCT') ? 'DISTINCT\n' : 'MISSING\n');
