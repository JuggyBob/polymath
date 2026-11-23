'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print \"b\" < \"aa\"; print \"aa\" < \"b\"; print \"a\" == \"a\";"));
