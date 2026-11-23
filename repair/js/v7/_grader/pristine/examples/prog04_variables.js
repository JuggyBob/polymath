'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("let a = 4; let b = a + 3; set b = b * 2; print a; print b;"));
