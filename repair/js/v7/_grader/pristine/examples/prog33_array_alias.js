'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("let a = [1]; let b = a; push b, 2; print a; print b;"));
