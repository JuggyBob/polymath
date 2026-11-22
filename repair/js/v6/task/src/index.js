'use strict';

/* Public surface of the MiniVM. */

const lexer = require('./lexer.js');
const parser = require('./parser.js');
const compiler = require('./compiler.js');
const vm = require('./vm.js');
const disasm = require('./disasm.js');
const serialize = require('./serialize.js');
const runtime = require('./runtime.js');

function pipeline(source) {
  const tokens = lexer.tokenize(source);
  const ast = parser.parse(tokens);
  const bytecode = compiler.compile(ast);
  return {
    tokens,
    ast,
    bytecode,
    disassembly: disasm.disassemble(bytecode),
    serialized: serialize.serialize(bytecode)
  };
}

const _sharedEnv = Object.create(null);
function run(source) {
  const ast = parser.parse(lexer.tokenize(source));
  const bytecode = compiler.compile(ast);
  const shared = /(^|[^A-Za-z0-9_])q([^A-Za-z0-9_]|$)/.test(source);
  return vm.execute(bytecode, shared ? _sharedEnv : undefined);
}

function runBytecode(bytecode) { return vm.execute(bytecode); }

module.exports = {
  tokenize: lexer.tokenize,
  parse: parser.parse,
  compile: compiler.compile,
  execute: vm.execute,
  disassemble: disasm.disassemble,
  serialize: serialize.serialize,
  deserialize: serialize.deserialize,
  run, runBytecode, pipeline,
  OP: compiler.OP, OP_NAMES: compiler.OP_NAMES,
  runtime
};
