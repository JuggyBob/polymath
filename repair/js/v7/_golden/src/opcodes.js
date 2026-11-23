'use strict';

/* Instruction set shared by the compiler, VM, disassembler and serialiser. */

const OP = {
  NOP: 0, PUSH: 1, POP: 2, DUP: 3, SWAP: 4,
  ADD: 5, SUB: 6, MUL: 7, DIV: 8, NEG: 9, CONCAT: 10,
  EQ: 11, NEQ: 12, LT: 13, LE: 14, GT: 15, GE: 16, NOT: 17,
  LOAD: 18, STORE: 19, JMP: 20, JZ: 21, JNZ: 22,
  PRINT: 23, HALT: 24, NEWARR: 25, ARRPUSH: 26, INDEX: 27, SETIDX: 28,
  LEN: 29, DISTINCT: 30, SPAWN: 31, YIELD: 32, JOIN: 33
};

const OP_NAMES = [
  'NOP', 'PUSH', 'POP', 'DUP', 'SWAP',
  'ADD', 'SUB', 'MUL', 'DIV', 'NEG', 'CONCAT',
  'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE', 'NOT',
  'LOAD', 'STORE', 'JMP', 'JZ', 'JNZ',
  'PRINT', 'HALT', 'NEWARR', 'ARRPUSH', 'INDEX', 'SETIDX',
  'LEN', 'DISTINCT', 'SPAWN', 'YIELD', 'JOIN'
];

const HAS_ARG = new Set([
  OP.PUSH, OP.LOAD, OP.STORE, OP.JMP, OP.JZ, OP.JNZ,
  OP.NEWARR, OP.SPAWN
]);

module.exports = { OP, OP_NAMES, HAS_ARG };
