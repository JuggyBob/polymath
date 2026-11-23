'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("let a = [1, 3]; print a; print a[0]; print a[2]; print len(a); push a, 9; print a;"));
