'use strict';
const { compileSource, serialize, deserialize, execute } = require('../src/index.js');
const code = compileSource('fiber a { print 1; } spawn a; join 1; print 2;');
const back = deserialize(serialize(code));
process.stdout.write(execute(back));
