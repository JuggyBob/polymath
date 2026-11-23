'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("fiber w { print 7; } let f = spawn w; yield; join f; print 8;"));
