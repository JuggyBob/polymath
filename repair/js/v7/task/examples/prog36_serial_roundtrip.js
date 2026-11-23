'use strict';
const { compileSource, serialize, deserialize, execute } = require('../src/index.js');
const code = compileSource('print "a" + "b"; print true;');
const back = deserialize(serialize(code));
process.stdout.write(execute(back));
