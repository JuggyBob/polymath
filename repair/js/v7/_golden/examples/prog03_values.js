'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print true; print false; print null; print !true; print !0; print 1 < 2; print 2 <= 2; print 3 > 1; print 2 == 2;"));
