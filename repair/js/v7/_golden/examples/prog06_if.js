'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("let flag = true; if flag { print \"yes\"; } else { print \"no\"; } if false { print \"bad\"; } print \"done\";"));
