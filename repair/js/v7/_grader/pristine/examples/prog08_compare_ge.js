'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print 3 >= 3; print 2 >= 5;"));
