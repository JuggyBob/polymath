'use strict';

/* AST -> flat bytecode. Bytecode is an array of { op, arg } records. */

const { parse } = require('./parser.js');

const OP = {
  NOP: 0, PUSH: 1, POP: 2, DUP: 3, SWAP: 4,
  ADD: 5, SUB: 6, MUL: 7, DIV: 8, MOD: 9, NEG: 10, CONCAT: 11,
  EQ: 12, NEQ: 13, LT: 14, LE: 15, GT: 16, GE: 17, NOT: 18,
  AND: 19, OR: 20, LOAD: 21, STORE: 22, JMP: 23, JZ: 24, JNZ: 25,
  PRINT: 26, HALT: 27, NEWARR: 28, PUSHIDX: 29, SETIDX: 30,
  LEN: 31, DISTINCT: 33
};

const OP_NAMES = [
  'NOP', 'PUSH', 'POP', 'DUP', 'SWAP', 'ADD', 'SUB', 'MUL', 'DIV', 'MOD',
  'NEG', 'CONCAT', 'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE', 'NOT', 'AND', 'OR',
  'LOAD', 'STORE', 'JMP', 'JZ', 'JNZ', 'PRINT', 'HALT', 'NEWARR', 'PUSHIDX',
  'SETIDX', 'LEN', 'UNUSED', 'DISTINCT'
];

const BIN_OP = {
  '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', '%': 'MOD',
  '==': 'EQ', '!=': 'NEQ', '<': 'LT', '<=': 'LE', '>': 'GT', '>=': 'GE',
  '&&': 'AND', '||': 'OR'
};

class Compiler {
  constructor() { this.code = []; }

  emit(op, arg) {
    const ins = arg === undefined ? { op } : { op, arg };
    this.code.push(ins);
    return this.code.length - 1;
  }

  patch(at, arg) { this.code[at].arg = arg; }

  compileAll(body) {
    for (const s of body) this.statement(s);
    this.emit(OP.HALT);
    return this.code;
  }

  statement(s) {
    switch (s.k) {
      case 'let':
        this.expression(s.expr);
        this.emit(OP.STORE, s.name);
        break;
      case 'assign':
        if (s.target.k === 'id') {
          this.expression(s.expr);
          this.emit(OP.STORE, s.target.name);
        } else {
          this.expression(s.target.a);
          this.expression(s.target.i);
          this.expression(s.expr);
          this.emit(OP.SETIDX);
        }
        break;
      case 'print':
        this.expression(s.expr);
        this.emit(OP.PRINT);
        break;
      case 'expr':
        this.expression(s.expr);
        this.emit(OP.POP);
        break;
      case 'if': {
        this.expression(s.cond);
        const jz = this.emit(OP.JZ, -1);
        for (const st of s.then) this.statement(st);
        let jmp = -1;
        if (s.otherwise.length) {
          jmp = this.emit(OP.JMP, -1);
        }
        this.patch(jz, this.code.length);
        for (const st of s.otherwise) this.statement(st);
        if (jmp >= 0) this.patch(jmp, this.code.length);
        break;
      }
      case 'while': {
        const start = this.code.length;
        this.expression(s.cond);
        const jz = this.emit(OP.JZ, -1);
        for (const st of s.body) this.statement(st);
        this.emit(OP.JMP, start);
        this.patch(jz, this.code.length);
        break;
      }
      default:
        throw new Error('unknown statement ' + s.k);
    }
  }

  expression(e) {
    switch (e.k) {
      case 'num':
      case 'str':
      case 'bool':
        this.emit(OP.PUSH, e.v);
        break;
      case 'null':
        this.emit(OP.PUSH, null);
        break;
      case 'id':
        this.emit(OP.LOAD, e.name);
        break;
      case 'arr':
        for (const item of e.items) this.expression(item);
        this.emit(OP.NEWARR, e.items.length);
        break;
      case 'idx':
        this.expression(e.a);
        this.expression(e.i);
        this.emit(OP.PUSHIDX);
        break;
      case 'bin':
        this.expression(e.l);
        this.expression(e.r);
        this.emit(OP[BIN_OP[e.op]]);
        break;
      case 'un':
        this.expression(e.e);
        this.emit(e.op === '-' ? OP.NEG : OP.NOT);
        break;
      case 'len':
        this.expression(e.e);
        this.emit(OP.LEN);
        break;
      case 'distinct':
        this.expression(e.e);
        this.emit(OP.DISTINCT);
        break;
      default:
        throw new Error('unknown expression ' + e.k);
    }
  }
}

function compile(input) {
  const ast = Array.isArray(input) && (input.length === 0 || input[0] && input[0].k) ? input : parse(input);
  return new Compiler().compileAll(ast);
}

module.exports = { compile, OP, OP_NAMES, Compiler };
