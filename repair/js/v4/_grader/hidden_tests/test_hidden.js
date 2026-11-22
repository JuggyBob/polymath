'use strict';

const { collect, chunk } = require('../src/async.js');
const { mapOrdered, pipe, createBuffer } = require('../src/streams.js');
const { cachedDouble, cacheFor, put, read } = require('../src/cache.js');
const { init, compute, getValue, b, a, registerB, getConfig } = require('../src/lazy.js');
const { Emitter } = require('../src/events.js');
const { schedule, lookup, buildIndex } = require('../src/scope.js');

async function CHECK(name, cond) {
  let ok = false;
  try {
    ok = !!(await (typeof cond === 'function' ? cond() : cond));
  } catch (e) {
    ok = false;
  }
  console.log('TEST ' + name + ' ' + (ok ? 'PASS' : 'FAIL'));
}

async function* asyncGen(values) {
  for (const v of values) yield v;
}

async function* asyncGenDelayed(values, delays) {
  for (const v of values) {
    await new Promise(r => setTimeout(r, delays[v] || 0));
    yield v;
  }
}

async function main() {
  // ---- async iterators -------------------------------------------------
  await CHECK('test_h_collect_async_generator', async () => (await collect(asyncGen([1, 2, 3]), 3)).join(',') === '1,2,3');
  await CHECK('test_h_collect_delayed_order', async () => (await collect(asyncGenDelayed([1, 2, 3], { 1: 20, 2: 5, 3: 10 }), 3)).join(',') === '1,2,3');
  await CHECK('test_h_collect_partial_expected', async () => (await collect(asyncGen([1, 2, 3, 4]), 2)).join(',') === '1,2');

  await CHECK('test_h_chunk_partial', async () => JSON.stringify(await collect(chunk([1, 2, 3, 4, 5], 2), 3)) === '[[1,2],[3,4],[5]]');
  await CHECK('test_h_chunk_size_three', async () => JSON.stringify(await collect(chunk([1, 2, 3, 4, 5], 3), 2)) === '[[1,2,3],[4,5]]');
  await CHECK('test_h_chunk_larger_than_input', async () => JSON.stringify(await collect(chunk([1, 2], 5), 1)) === '[[1,2]]');

  // ---- streams ---------------------------------------------------------
  await CHECK('test_h_map_ordered_delays', async () => {
    const r = await mapOrdered([1, 2, 3], async v => {
      await new Promise(res => setTimeout(res, { 1: 30, 2: 5, 3: 15 }[v]));
      return v * 10;
    });
    return r.join(',') === '10,20,30';
  });
  await CHECK('test_h_map_ordered_values', async () => {
    const r = await mapOrdered([1, 2, 3], async v => {
      await new Promise(res => setTimeout(res, { 1: 10, 2: 25, 3: 5 }[v]));
      return v * 10;
    });
    return r.slice().sort((x, y) => x - y).join(',') === '10,20,30';
  });
  await CHECK('test_h_map_ordered_error', async () => {
    let threw = false;
    try { await mapOrdered([1], async () => { throw new Error('mapper'); }); } catch (e) { threw = true; }
    return threw;
  });

  await CHECK('test_h_pipe_throw', async () => {
    let threw = false;
    try { await pipe(asyncGen([1, 2, 3]), () => { throw new Error('pipe'); }); } catch (e) { threw = true; }
    return threw;
  });
  await CHECK('test_h_pipe_partial_no_leak', async () => {
    let threw = false;
    let got = null;
    try {
      got = await pipe(asyncGen([1, 2, 3]), v => { if (v === 3) throw new Error('pipe'); return v; });
    } catch (e) {
      threw = true;
    }
    return threw && got === null;
  });
  await CHECK('test_h_pipe_value_count', async () => (await pipe(asyncGen([1, 2, 3, 4, 5]), x => x * 2)).length === 5);

  await CHECK('test_h_buffer_close', () => {
    const bf = createBuffer();
    bf.close();
    return bf.isClosed() === true;
  });
  await CHECK('test_h_buffer_push_after_close', () => {
    const bf = createBuffer();
    bf.push(1);
    bf.close();
    bf.push(2);
    return bf.drain().join(',') === '1';
  });

  // ---- WeakMap caches --------------------------------------------------
  await CHECK('test_h_cache_cached', () => {
    const o = { n: 5 };
    const first = cachedDouble(o);
    o.n = 6;
    return first === 10 && cachedDouble(o) === 10;
  });
  await CHECK('test_h_cache_same_id_distinct', () => {
    const o1 = { id: 'hid-same' };
    const o2 = { id: 'hid-same' };
    cacheFor(o1).push('x');
    return cacheFor(o2).length === 0;
  });
  await CHECK('test_h_cache_id_mutated', () => {
    const o = { id: 'hid-mut-a' };
    const first = cacheFor(o);
    o.id = 'hid-mut-b';
    return cacheFor(o) === first;
  });
  await CHECK('test_h_cache_for_appends', () => {
    const o1 = { id: 'hid-app-1' };
    const o2 = { id: 'hid-app-2' };
    cacheFor(o1).push('a');
    cacheFor(o2).push('b');
    return cacheFor(o1).join(',') === 'a' && cacheFor(o2).join(',') === 'b';
  });
  await CHECK('test_h_put_read', () => {
    const o = {};
    put(o, 17);
    return read(o) === 17;
  });
  await CHECK('test_h_put_overwrite', () => {
    const o = {};
    put(o, 1);
    put(o, 2);
    return read(o) === 2;
  });

  // ---- lazy / cyclic initialization ------------------------------------
  await CHECK('test_h_lazy_default_b', () => b() === 'B');
  await CHECK('test_h_lazy_after_init', () => {
    init();
    return getValue() === 20;
  });
  await CHECK('test_h_lazy_compute_after_init', () => compute() === 20);
  await CHECK('test_h_lazy_config_after_init', () => getConfig().level === 2);
  await CHECK('test_h_lazy_register_b', () => {
    registerB(() => '-X');
    return a() === 'A-X';
  });
  await CHECK('test_h_lazy_register_b_twice', () => {
    registerB(() => '-Y');
    return a() === 'A-Y';
  });

  // ---- event ordering --------------------------------------------------
  await CHECK('test_h_emit_order', () => {
    const e = new Emitter();
    const log = [];
    e.on(() => log.push('first'));
    e.on(() => log.push('second'));
    e.on(() => log.push('third'));
    e.emit();
    return log.join(',') === 'first,second,third';
  });
  await CHECK('test_h_emit_args', () => {
    const e = new Emitter();
    let got = '';
    e.on((x, y) => { got = x + y; });
    e.emit('a', 'b');
    return got === 'ab';
  });
  await CHECK('test_h_once_single', () => {
    const e = new Emitter();
    let n = 0;
    e.once(() => { n++; });
    e.emit();
    e.emit();
    return n === 1;
  });
  await CHECK('test_h_once_multiple', () => {
    const e = new Emitter();
    let n = 0;
    e.once(() => { n += 1; });
    e.on(() => { n += 10; });
    e.emit();
    e.emit();
    return n === 21;
  });
  await CHECK('test_h_snapshot_dynamic_add', () => {
    const e = new Emitter();
    const log = [];
    e.on(() => { log.push('first'); e.on(() => log.push('added')); });
    e.emitSnapshot();
    return log.join(',') === 'first';
  });
  await CHECK('test_h_emit_dynamic_add', () => {
    const e = new Emitter();
    const log = [];
    e.on(() => { log.push('first'); e.on(() => log.push('added')); });
    e.emit();
    return log.join(',') === 'first';
  });
  await CHECK('test_h_emit_async_waits', async () => {
    const e = new Emitter();
    let done = 0;
    e.on(async () => { await Promise.resolve(); done++; });
    e.on(async () => { await new Promise(r => setTimeout(r, 5)); done++; });
    await e.emitAsync();
    return done === 2;
  });
  await CHECK('test_h_emit_async_order', async () => {
    const e = new Emitter();
    const log = [];
    e.on(async () => { await new Promise(r => setTimeout(r, 20)); log.push('slow'); });
    e.on(async () => { await new Promise(r => setTimeout(r, 2)); log.push('fast'); });
    await e.emitAsync();
    return log.slice().sort().join(',') === 'fast,slow';
  });

  // ---- scope trap and performance contract -----------------------------
  await CHECK('test_h_scope_values', async () => (await schedule([10, 20, 30], v => v)).join(',') === '10,20,30');
  await CHECK('test_h_scope_indices', async () => (await schedule(['a', 'b'], (v, i) => v + i)).join(',') === 'a0,b1');
  await CHECK('test_h_scope_two_batches', async () => {
    const r1 = await schedule([1, 2], (v, i) => v + i);
    const r2 = await schedule([3, 4], (v, i) => v + i);
    return r1.join(',') === '1,3' && r2.join(',') === '3,5';
  });
  await CHECK('test_h_perf_correctness', () => {
    buildIndex([{ key: 'pc-a', value: 1 }, { key: 'pc-b', value: 2 }]);
    return lookup('pc-a') === 1 && lookup('pc-b') === 2;
  });
  await CHECK('test_h_perf_lookup', () => {
    const items = [];
    for (let i = 0; i < 10000; i++) items.push({ key: 'k' + i, value: i });
    buildIndex(items);
    const start = Date.now();
    let sum = 0;
    for (let o = 0; o < 100000; o++) sum += lookup('k' + (o % 10000));
    const elapsed = Date.now() - start;
    return sum === 499950000 && elapsed < 2000;
  });
  await CHECK('test_h_scope_lookup_rebuild', () => {
    buildIndex([{ key: 'rb1', value: 1 }]);
    buildIndex([{ key: 'rb2', value: 2 }]);
    return lookup('rb1') === undefined && lookup('rb2') === 2;
  });
}

main().catch(() => {});
