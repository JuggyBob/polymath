'use strict';

/* Public surface of the MiniVM. */

const { OP, OP_NAMES } = require('./opcodes.js');
const { tokenize } = require('./lexer.js');
const { parse } = require('./parser.js');
const { compileSource } = require('./compiler.js');
const { execute, restore, MiniVM, MiniVMError } = require('./vm.js');
const { disassemble } = require('./disasm.js');
const { serialize, deserialize } = require('./serialize.js');
const runtime = require('./runtime.js');
const snapshot = require('./snapshot.js');

function run(source) {
  return execute(compileSource(source));
}

module.exports = {
  MiniVM, MiniVMError, OP, OP_NAMES,
  tokenize, parse, compileSource, compile_source: compileSource,
  execute, run, runSource: run,
  disassemble, serialize, deserialize, restore,
  snapshot,
  runtime
};
