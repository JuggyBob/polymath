'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print \"a\\0b\"; print len(\"a\\0b\");"));
