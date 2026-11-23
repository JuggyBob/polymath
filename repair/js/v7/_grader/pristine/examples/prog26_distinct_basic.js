'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print distinct([1, 2, 3]); print distinct([1, 2, 1]); print distinct([]);"));
