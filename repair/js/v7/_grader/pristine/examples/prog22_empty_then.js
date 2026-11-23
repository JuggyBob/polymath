'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("if true { } else { print \"e\"; } while false { print \"z\"; } print \"ok\";"));
