'use strict';

/* Exact binary snapshot format. Every read is bounds checked. */

const HEADER = Buffer.from([0x4d, 0x56, 0x37, 0x01]);

function u32(n) {
  const b = Buffer.alloc(4);
  b.writeUInt32LE(n >>> 0, 0);
  return b;
}

function checksum(buf) {
  let h = 0x811c9dc5;
  for (let i = 0; i < buf.length; i++) {
    h ^= buf[i];
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  const b = Buffer.alloc(4);
  b.writeUInt32LE(h, 0);
  return b;
}

function writeValue(v) {
  if (v === undefined) return Buffer.from([5]);
  if (v === null) return Buffer.from([0]);
  if (v === true || v === false) return Buffer.from([1, v ? 1 : 0]);
  if (typeof v === 'number') {
    const b = Buffer.alloc(9);
    b[0] = 2;
    b.writeBigInt64LE(BigInt(v), 1);
    return b;
  }
  if (typeof v === 'string') {
    const s = Buffer.from(v, 'utf8');
    return Buffer.concat([Buffer.from([3]), u32(s.length), s]);
  }
  if (Array.isArray(v)) {
    const parts = [Buffer.from([4]), u32(v.length)];
    for (const item of v) parts.push(writeValue(item));
    return Buffer.concat(parts);
  }
  return Buffer.from([0]);
}

function encode(machine) {
  const parts = [HEADER];
  const ops = machine.code.ops;
  parts.push(u32(ops.length));
  for (const ins of ops) {
    parts.push(Buffer.from([ins.op & 0xff]));
    parts.push(writeValue(ins.arg));
  }
  const names = machine.code.globals;
  parts.push(u32(names.length));
  for (let i = 0; i < names.length; i++) {
    const n = Buffer.from(names[i], 'utf8');
    parts.push(u32(n.length), n, writeValue(machine.globals[i]));
  }
  const fibers = Array.from(machine.fibers.values());
  parts.push(u32(fibers.length));
  for (const f of fibers) {
    parts.push(u32(f.id), u32(f.pc), u32(f.stack.length));
    for (const v of f.stack) parts.push(writeValue(v));
  }
  parts.push(u32(machine.ready.length));
  for (const id of machine.ready) parts.push(u32(id));
  parts.push(u32(machine.blocked.length));
  for (const bp of machine.blocked) parts.push(u32(bp.waiter), u32(bp.target));
  const body = Buffer.concat(parts);
  return Buffer.concat([body, checksum(body)]);
}

class Reader {
  constructor(buf, limit) {
    this.buf = buf;
    this.i = 0;
    this.limit = limit;
  }
  need(n) {
    if (this.i + n > this.limit) throw new Error('TRUNCATED');
  }
  byte() {
    this.need(1);
    return this.buf[this.i++];
  }
  u32() {
    this.need(4);
    const v = this.buf.readUInt32LE(this.i);
    this.i += 4;
    return v;
  }
  i64() {
    this.need(8);
    const v = this.buf.readBigInt64LE(this.i);
    this.i += 8;
    return Number(v);
  }
  value() {
    const t = this.byte();
    if (t === 5) return undefined;
    if (t === 0) return null;
    if (t === 1) return this.byte() !== 0;
    if (t === 2) return this.i64();
    if (t === 3) {
      const n = this.u32();
      this.need(n);
      const s = this.buf.toString('utf8', this.i, this.i + n);
      this.i += n;
      return s;
    }
    if (t === 4) {
      const n = this.u32();
      const out = new Array(n);
      for (let k = 0; k < n; k++) out[k] = this.value();
      return out;
    }
    throw new Error('TRUNCATED');
  }
}

function decode(bytes) {
  const buf = Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes);
  if (buf.length < 3) throw new Error('TRUNCATED');
  if (buf[0] !== 0x4d || buf[1] !== 0x56 || buf[2] !== 0x37) throw new Error('BAD_MAGIC');
  if (buf.length < 4) throw new Error('TRUNCATED');
  if (buf[3] !== 0x01) throw new Error('BAD_VERSION');
  if (buf.length < 8) throw new Error('TRUNCATED');
  const end = buf.length - 4;
  const rd = new Reader(buf, end);
  rd.i = 4;

  const opCount = rd.u32();
  const ops = new Array(opCount);
  for (let i = 0; i < opCount; i++) {
    const op = rd.byte();
    const arg = rd.value();
    ops[i] = arg === undefined ? { op } : { op, arg };
  }
  const nameCount = rd.u32();
  const names = new Array(nameCount);
  const values = new Array(nameCount);
  for (let i = 0; i < nameCount; i++) {
    const n = rd.u32();
    rd.need(n);
    names[i] = buf.toString('utf8', rd.i, rd.i + n);
    rd.i += n;
    values[i] = rd.value();
  }
  const fiberCount = rd.u32();
  const fibers = new Array(fiberCount);
  for (let i = 0; i < fiberCount; i++) {
    const id = rd.u32();
    const pc = rd.u32();
    const depth = rd.u32();
    const stack = new Array(depth);
    for (let k = 0; k < depth; k++) stack[k] = rd.value();
    fibers[i] = { id, pc, stack, halted: false };
  }
  const readyCount = rd.u32();
  const ready = new Array(readyCount);
  for (let i = 0; i < readyCount; i++) ready[i] = rd.u32();
  const blockedCount = rd.u32();
  const blocked = new Array(blockedCount);
  for (let i = 0; i < blockedCount; i++) {
    blocked[i] = { waiter: rd.u32(), target: rd.u32() };
  }
  if (rd.i !== end) throw new Error('TRUNCATED');

  const want = checksum(buf.subarray(0, end));
  for (let i = 0; i < 4; i++) {
    if (buf[end + i] !== want[i]) throw new Error('BAD_CHECKSUM');
  }

  const seen = new Set();
  for (const f of fibers) {
    if (seen.has(f.id)) throw new Error('DUPLICATE_FIBER');
    seen.add(f.id);
  }

  const { Machine } = require('./vm.js');
  const code = { ops, globals: names, fibers: {} };
  const m = new Machine(code);
  m.globals = values;
  m.fibers = new Map();
  for (const f of fibers) m.fibers.set(f.id, f);
  m.ready = ready;
  m.blocked = blocked;
  let max = 0;
  for (const f of fibers) if (f.id > max) max = f.id;
  m.nextId = max + 1;
  return m;
}

module.exports = { encode, decode, checksum };
