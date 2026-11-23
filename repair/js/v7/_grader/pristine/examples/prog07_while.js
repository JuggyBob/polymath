'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("let i = 0; while i < 3 { print i; set i = i + 1; }"));
