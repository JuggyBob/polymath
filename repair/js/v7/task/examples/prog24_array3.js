'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print [1, 2, 3]; print []; print [[1], [2, 3]];"));
