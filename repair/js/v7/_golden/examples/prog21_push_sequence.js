'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("let a = [1]; push a, 2; push a, 3; print a;"));
