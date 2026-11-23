'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print distinct([[1], [1]]); print distinct([[1], [2]]);"));
