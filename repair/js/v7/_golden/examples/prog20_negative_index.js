'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("let a = [1, 2]; print a[-1]; print a[5];"));
