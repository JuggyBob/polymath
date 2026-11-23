'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("if \"\" { print \"x\"; } else { print \"y\"; } if [] { print \"a\"; } else { print \"b\"; } if 0 { print \"c\"; } else { print \"d\"; }"));
