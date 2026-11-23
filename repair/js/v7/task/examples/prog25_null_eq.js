'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print null == null; print null != 0; print null == false;"));
