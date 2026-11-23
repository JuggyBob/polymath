'use strict';
const { run } = require('../src/index.js');
process.stdout.write(run("print \"hello\"; print \"a\" + \"b\" + \"c\"; print \"x\" + 7; print len(\"abcd\"); print \"line1\\nline2\"; print \"q\\\"q\"; print \"back\\\\slash\";"));
