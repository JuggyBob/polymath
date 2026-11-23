'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print len(\"é\"); print len(\"abc\"); print len(\"😀\");"));
