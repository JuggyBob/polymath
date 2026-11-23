'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print \"é\" > \"z\"; print \"é\" == \"é\";"));
