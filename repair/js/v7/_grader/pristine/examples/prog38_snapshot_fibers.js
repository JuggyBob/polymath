'use strict';
const { MiniVM, restore } = require('../src/index.js');
const vm = MiniVM.fromSource('fiber a { print 1; yield; print 2; } spawn a; yield;');
process.stdout.write(restore(vm.snapshot()).run());
