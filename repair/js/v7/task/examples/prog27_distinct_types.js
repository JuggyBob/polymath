'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print distinct([\"a\", \"b\"]); print distinct([true, false, true]); print distinct([1, \"1\"]);"));
