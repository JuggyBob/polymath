'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print 1 != 2; print 2 != 2;"));
