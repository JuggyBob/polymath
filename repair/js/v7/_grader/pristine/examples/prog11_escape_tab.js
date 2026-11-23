'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print \"a\\tb\"; print len(\"a\\tb\");"));
