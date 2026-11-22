'use strict';

const { collect, chunk } = require('../src/async.js');
const { mapOrdered, pipe, createBuffer } = require('../src/streams.js');
const { getCache, cachedDouble, cacheFor, put, read } = require('../src/cache.js');
const { init, compute, getValue, b, a, getConfig } = require('../src/lazy.js');
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

function syncAsyncIterable(vals) {
  let i = 0;
  return {
    [Symbol.asyncIterator]() {
      return {
        next() {
          const value = vals[i++];
          return { value, done: i > vals.length };
        },
      };
    },
  };
}

async function* asyncGen(values) {
  for (const v of values) yield v;
}

async function collectAsync(iterable) {
  const out = [];
  for await (const v of iterable) out.push(v);
  return out;
}

async function main() {
  await CHECK('v_collect_basic', async () => (await collect(syncAsyncIterable([1, 2, 3]), 3)).join(',') === '1,2,3');
  await CHECK('v_collect_empty', async () => (await collect(syncAsyncIterable([]), 0)).length === 0);

  await CHECK('v_chunk_even', async () => JSON.stringify(await collectAsync(chunk([1, 2, 3, 4], 2))) === '[[1,2],[3,4]]');
  await CHECK('v_chunk_size_one', async () => JSON.stringify(await collectAsync(chunk([1, 2], 1))) === '[[1],[2]]');

  await CHECK('v_map_ordered_basic', async () => (await mapOrdered([1, 2, 3], async x => x * 2)).join(',') === '2,4,6');
  await CHECK('v_map_ordered_empty', async () => (await mapOrdered([], async x => x)).length === 0);

  await CHECK('v_pipe_basic', async () => (await pipe(asyncGen([1, 2]), x => x + 1)).join(',') === '2,3');
  await CHECK('v_pipe_empty', async () => (await pipe(asyncGen([]), x => x)).length === 0);

  const buf = createBuffer();
  buf.push(1);
  buf.push(2);
  await CHECK('v_buffer_push_drain', () => buf.drain().join(',') === '1,2');
  await CHECK('v_buffer_size', () => buf.size() === 0);
  await CHECK('v_buffer_not_closed_initially', () => createBuffer().isClosed() === false);

  await CHECK('v_cache_getcache_is_weakmap', () => getCache() instanceof WeakMap);
  await CHECK('v_cache_double_basic', () => cachedDouble({ n: 4 }) === 8);
  await CHECK('v_cache_for_basic', () => Array.isArray(cacheFor({ id: 'vis-a' })));
  await CHECK('v_cache_for_distinct_ids', () => cacheFor({ id: 'vis-b' }) !== cacheFor({ id: 'vis-c' }));
  const po = { n: 1 };
  put(po, 5);
  await CHECK('v_put_no_throw', () => true);
  await CHECK('v_read_unknown', () => read({ n: 99 }) === undefined);

  await CHECK('v_lazy_getvalue_before_init', () => getValue() === 10);
  await CHECK('v_lazy_compute', () => compute() === 10);
  await CHECK('v_lazy_a_before_register', () => a() === 'AB');
  await CHECK('v_lazy_config', () => getConfig().level === 1 && b() === 'B');

  const e1 = new Emitter();
  let seen1 = [];
  e1.on(v => seen1.push(v));
  e1.emit(7);
  await CHECK('v_event_emit_single', () => seen1.join(',') === '7');
  const e2 = new Emitter();
  e2.on(() => {});
  e2.on(() => {});
  await CHECK('v_event_count', () => e2.count() === 2);
  const e3 = new Emitter();
  let seen3 = [];
  e3.on(v => seen3.push(v));
  e3.emitSnapshot(9);
  await CHECK('v_event_snapshot_single', () => seen3.join(',') === '9');
  const e4 = new Emitter();
  let seen4 = 0;
  e4.on(() => { seen4++; });
  await e4.emitAsync();
  await CHECK('v_event_emit_async_sync_listener', () => seen4 === 1);

  await CHECK('v_scope_schedule_count', async () => (await schedule([1, 2, 3], () => 0)).length === 3);
  buildIndex([{ key: 'vis-k', value: 42 }]);
  await CHECK('v_scope_lookup_hit', () => lookup('vis-k') === 42);
  await CHECK('v_scope_lookup_miss', () => lookup('vis-none') === undefined);
}

main().catch(() => {});
