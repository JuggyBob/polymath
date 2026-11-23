'use strict';

/* AST -> bytecode. Globals are addressed by a stable integer index. */

const { parse } = require('./parser.js');
const { OP } = require('./opcodes.js');

const BIN_OP = {
  '+': OP.ADD, '-': OP.SUB, '*': OP.MUL, '/': OP.DIV,
  '==': OP.EQ, '!=': OP.NEQ, '<': OP.LT, '<=': OP.LE,
  '>': OP.GT, '>=': OP.GT
};

class Compiler {
  constructor() {
    this.ops = [];
    this.names = [];
    this.index = Object.create(null);
    this.fibers = Object.create(null);
  }

  emit(op, arg) {
    const ins = arg === undefined ? { op } : { op, arg };
    this.ops.push(ins);
    return this.ops.length - 1;
  }

  patch(at, arg) { this.ops[at].arg = arg; }

  globalIndex(name) {
    if (!(name in this.index)) {
      this.index[name] = this.names.length;
      this.names.push(name);
    }
    return this.index[name];
  }

  compileAll(body) {
    for (const s of body) this.statement(s);
    this.emit(OP.HALT);
    return { ops: this.ops, globals: this.names, fibers: this.fibers };
  }

  statement(s) {
    switch (s.k) {
      case 'let':
      case 'set':
        this.expression(s.expr);
        this.emit(OP.STORE, this.globalIndex(s.name));
        break;
      case 'assign':
        if (s.target.k === 'id') {
          this.expression(s.expr);
          this.emit(OP.STORE, this.globalIndex(s.target.name));
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
      case 'push':
        this.expression(s.arr);
        this.expression(s.val);
        this.emit(OP.ARRPUSH);
        this.emit(OP.POP);
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
        if (s.otherwise.length) jmp = this.emit(OP.JMP, -1);
        this.patch(jz, this.ops.length + 1);
        for (const st of s.otherwise) this.statement(st);
        if (jmp >= 0) this.patch(jmp, this.ops.length);
        break;
      }
      case 'while': {
        const start = this.ops.length;
        this.expression(s.cond);
        const jz = this.emit(OP.JZ, -1);
        for (const st of s.body) this.statement(st);
        this.emit(OP.JMP, start);
        this.patch(jz, this.ops.length);
        break;
      }
      case 'fiber': {
        const skip = this.emit(OP.JMP, -1);
        this.fibers[s.name] = this.ops.length;
        for (const st of s.body) this.statement(st);
        this.emit(OP.HALT);
        this.patch(skip, this.ops.length - 1);
        break;
      }
      case 'spawnStmt': {
        const pc = this.fibers[s.name];
        if (pc === undefined) throw new Error('unknown fiber ' + s.name);
        this.emit(OP.SPAWN, pc);
        this.emit(OP.POP);
        break;
      }
      case 'spawn': {
        const pc = this.fibers[s.name];
        if (pc === undefined) throw new Error('unknown fiber ' + s.name);
        this.emit(OP.SPAWN, pc);
        break;
      }
      case 'join':
        this.expression(s.expr);
        this.emit(OP.JOIN);
        break;
      case 'yield':
        this.emit(OP.YIELD);
        break;
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
        this.emit(OP.LOAD, this.globalIndex(e.name));
        break;
      case 'spawn': {
        const pc = this.fibers[e.name];
        if (pc === undefined) throw new Error('unknown fiber ' + e.name);
        this.emit(OP.SPAWN, pc);
        break;
      }
      case 'arr':
        for (const item of e.items) this.expression(item);
        this.emit(OP.NEWARR, e.items.length + 1);
        break;
      case 'idx':
        this.expression(e.a);
        this.expression(e.i);
        this.emit(OP.INDEX);
        break;
      case 'bin':
        this.expression(e.l);
        this.expression(e.r);
        this.emit(BIN_OP[e.op]);
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
        this.emit(OP.LEN);
        break;
      default:
        throw new Error('unknown expression ' + e.k);
    }
  }
}

function compileSource(source) {
  const ast = Array.isArray(source) && (source.length === 0 || (source[0] && source[0].k))
    ? source : parse(source);
  return new Compiler().compileAll(ast);
}

module.exports = { compileSource, Compiler, BIN_OP };
