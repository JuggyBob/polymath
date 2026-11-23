'use strict';

/* Stack machine with a deterministic FIFO fiber scheduler. */

const { OP } = require('./opcodes.js');
const rt = require('./runtime.js');
const snapshot = require('./snapshot.js');

const BREAK = true;

class Machine {
  constructor(code) {
    this.code = code;
    this.ops = code.ops;
    this.globals = new Array(code.globals.length).fill(null);
    this.fibers = new Map();
    this.ready = [0];
    this.blocked = [];
    this.nextId = 1;
    this.out = [];
    this.fibers.set(0, { id: 0, pc: 0, stack: [], halted: false });
  }

  run() {
    while (this.ready.length) {
      const id = this.ready.shift();
      const f = this.fibers.get(id);
      if (!f || f.halted) continue;
      while (f.pc < this.ops.length && !f.halted) {
        const ins = this.ops[f.pc++];
        if (this.step(f, ins)) break;
      }
    }
    return this.out.join('');
  }

  step(f, ins) {
    const op = ins.op;
    const arg = ins.arg;
    const st = f.stack;
    const push = v => { st.push(v); };
    const pop = () => st.length ? st.pop() : null;
    switch (op) {
      case OP.NOP: return false;
      case OP.PUSH: push(arg); return false;
      case OP.POP: pop(); return false;
      case OP.DUP: push(st.length ? st[st.length - 1] : null); return false;
      case OP.SWAP: {
        const a = pop(); const b = pop();
        push(a); push(b);
        return false;
      }
      case OP.ADD: {
        const b = pop(); const a = pop();
        if (typeof a === 'string' || typeof b === 'string') push(rt.toStr(a) + rt.toStr(b));
        else push(a + b);
        return false;
      }
      case OP.SUB: { const b = pop(); const a = pop(); push(a - b); return false; }
      case OP.MUL: { const b = pop(); const a = pop(); push(a * b); return false; }
      case OP.DIV: { const b = pop(); const a = pop(); push(Math.trunc(a / b)); return false; }
      case OP.NEG: push(-pop()); return false;
      case OP.CONCAT: { const b = pop(); const a = pop(); push(rt.toStr(a) + rt.toStr(b)); return false; }
      case OP.EQ: { const b = pop(); const a = pop(); push(rt.valuesEqual(a, b)); return false; }
      case OP.NEQ: { const b = pop(); const a = pop(); push(!rt.valuesEqual(a, b)); return false; }
      case OP.LT: { const b = pop(); const a = pop(); push(rt.compare(a, b, '<')); return false; }
      case OP.LE: { const b = pop(); const a = pop(); push(rt.compare(a, b, '<=')); return false; }
      case OP.GT: { const b = pop(); const a = pop(); push(rt.compare(a, b, '>')); return false; }
      case OP.GE: { const b = pop(); const a = pop(); push(rt.compare(a, b, '>=')); return false; }
      case OP.NOT: push(!rt.truthy(pop())); return false;
      case OP.LOAD: {
        const v = arg >= 0 && arg < this.globals.length ? this.globals[arg] : null;
        push(v === undefined ? null : v);
        return false;
      }
      case OP.STORE: {
        const v = pop();
        if (arg >= this.globals.length) this.globals.length = arg + 1;
        this.globals[arg] = v;
        return false;
      }
      case OP.JMP: f.pc = arg; return false;
      case OP.JZ: if (!rt.truthy(pop())) f.pc = arg; return false;
      case OP.JNZ: if (rt.truthy(pop())) f.pc = arg; return false;
      case OP.PRINT: this.out.push(rt.toStr(pop()) + '\n'); return false;
      case OP.HALT: return this.halt(f);
      case OP.NEWARR: {
        const n = arg;
        const items = new Array(n);
        for (let k = n - 1; k >= 0; k--) items[k] = pop();
        push(items);
        return false;
      }
      case OP.ARRPUSH: {
        const val = pop(); const arr = pop();
        if (Array.isArray(arr)) arr.push(val);
        push(arr);
        return false;
      }
      case OP.INDEX: {
        const idx = pop(); const arr = pop();
        push(Array.isArray(arr) && idx >= 0 && idx < arr.length ? arr[idx] : null);
        return false;
      }
      case OP.SETIDX: {
        const val = pop(); const idx = pop(); const arr = pop();
        if (Array.isArray(arr) && idx >= 0 && idx < arr.length) arr[idx] = val;
        push(arr);
        return false;
      }
      case OP.LEN: push(rt.strLen(pop())); return false;
      case OP.DISTINCT: push(rt.isDistinct(pop())); return false;
      case OP.SPAWN: {
        const id = this.nextId++;
        this.fibers.set(id, { id, pc: arg, stack: [], halted: false });
        push(id);
        this.ready.push(id);
        return false;
      }
      case OP.YIELD:
        this.ready.push(f.id);
        return BREAK;
      case OP.JOIN: {
        const target = pop();
        const tf = this.fibers.get(target);
        if (!tf || tf.halted) return false;
        this.blocked.push({ waiter: f.id, target });
        return BREAK;
      }
      default:
        throw new Error('unknown opcode ' + op);
    }
  }

  halt(f) {
    f.halted = true;
    const wake = [];
    for (const bp of this.blocked) if (bp.target === f.id) wake.push(bp.waiter);
    if (wake.length) {
      this.blocked = this.blocked.filter(bp => bp.target !== f.id);
      for (const w of wake) this.ready.push(w);
    }
    return BREAK;
  }

  snapshot() {
    return snapshot.encode(this);
  }
}

class MiniVMError extends Error {
  constructor(code) {
    super(code);
    this.name = 'MiniVMError';
    this.code = code;
  }
  toString() { return this.message; }
}

class MiniVM {
  constructor(code) {
    this.code = code;
    this.machine = new Machine(code);
  }
  static fromSource(source) {
    const { compileSource } = require('./compiler.js');
    return new MiniVM(compileSource(source));
  }
  run() { return this.machine.run(); }
  snapshot() { return this.machine.snapshot(); }
}

function restore(bytes) {
  const m = snapshot.decode(bytes);
  const vm = new MiniVM(m.code);
  vm.machine = m;
  return vm;
}

function execute(code) {
  return new Machine(code).run();
}

module.exports = { Machine, MiniVM, MiniVMError, restore, execute };
