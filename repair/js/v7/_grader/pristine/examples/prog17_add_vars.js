'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("let a = \"x\"; let b = \"y\"; print a + b; print \"n=\" + 5;"));
