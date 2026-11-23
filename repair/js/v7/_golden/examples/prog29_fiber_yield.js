'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("fiber a { print \"a1\"; yield; print \"a2\"; } fiber b { print \"b1\"; yield; print \"b2\"; } spawn a; spawn b; yield; yield;"));
