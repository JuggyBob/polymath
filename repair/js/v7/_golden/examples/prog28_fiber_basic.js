'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("fiber w { print 1; yield; print 2; } let f = spawn w; print 3; join f; print 4;"));
