'use strict';
const { MiniVM, restore } = require('../src/index.js');
const vm = MiniVM.fromSource('let x = 5; print x + 1;');
const bytes = vm.snapshot();
process.stdout.write(restore(bytes).run());
