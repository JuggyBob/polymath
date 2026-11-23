'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print 2 + 3 * 4; print (2 + 3) * 4; print 10 - 3 - 2; print 7 / 2; print -5 + 9;"));
