'use strict';

const s = require('../src/scheduler.js');
const p = require('../src/proxyStore.js');
const c = require('../src/cache.js');
const a = require('../src/asyncStream.js');
const n = require('../src/numbers.js');

let failures = 0;
function ok(name) { console.log('TEST ' + name + ' PASS'); }
function bad(name) { failures++; console.log('TEST ' + name + ' FAIL'); }
function rec(name, fn) {
  try { fn(); ok(name); } catch (e) { bad(name); }
}
async function arec(name, fn) {
  try { await fn(); ok(name); } catch (e) { bad(name); }
}
function assert(cond) { if (!cond) throw new Error('assertion failed'); }
function eq(x, y) { assert(JSON.stringify(x) === JSON.stringify(y)); }
async function drain(gen) {
  const out = [];
  for await (const v of gen) out.push(v);
  return out;
}

(async () => {

  // ---- scheduler -------------------------------------------------------
  await arec('test_h_sched_run_phases', async () => {
    eq(await s.runPhases(), ['sync', 'micro', 'promise', 'macro']);
  });
  await arec('test_h_sched_drain_five', async () => {
    assert((await s.drainQueue(5)) === 5);
  });
  await arec('test_h_sched_drain_many', async () => {
    assert((await s.drainQueue(50)) === 50);
  });
  await arec('test_h_sched_then_micro', async () => {
    eq(await s.thenVsMicrotask(), ['micro', 'then']);
  });
  await arec('test_h_sched_await_order', async () => {
    eq(await s.awaitOrdering(), ['before', 'inner', 'after:v']);
  });
  await arec('test_h_sched_delayed_order', async () => {
    eq(await s.delayedOrder(), ['early', 'late']);
  });

  // ---- proxy -----------------------------------------------------------
  rec('test_h_proxy_get_missing', () => {
    assert(p.countingGet().nope === 0);
  });
  rec('test_h_proxy_get_present', () => {
    const st = p.countingGet(); st.a = 4; assert(st.a === 4);
  });
  rec('test_h_proxy_set_number', () => {
    const st = p.numericSet(); st.x = 5; assert(st.x === 5);
  });
  rec('test_h_proxy_set_string_ignored', () => {
    const st = p.numericSet(); st.y = 'no'; assert(st.y === undefined);
  });
  rec('test_h_proxy_has_absent', () => {
    assert(('a' in p.strictHas()) === false);
  });
  rec('test_h_proxy_has_present', () => {
    const st = p.strictHas(); st.a = 1; assert(('a' in st) === true);
  });
  rec('test_h_proxy_own_keys', () => {
    eq(Reflect.ownKeys(p.listedKeys()), ['a', 'c']);
  });
  rec('test_h_proxy_delete_resets', () => {
    const st = p.resettable(); st.a = 5; delete st.a; assert(st.a === 0);
  });
  rec('test_h_proxy_descriptor_enum', () => {
    eq(Object.keys(p.descriptorProxy()), []);
  });

  // ---- cache -----------------------------------------------------------
  rec('test_h_cache_memoize_calls', () => {
    let calls = 0;
    const f = c.memoize(o => { calls++; return o.v; });
    const a1 = { v: 1 };
    f(a1); f(a1);
    assert(calls === 1);
  });
  rec('test_h_cache_memoize_distinct_objects', () => {
    let calls = 0;
    const f = c.memoize(o => { calls++; return o.v; });
    const a1 = { v: 1 }, b1 = { v: 1 };
    f(a1); f(b1);
    assert(calls === 2);
  });
  rec('test_h_cache_bound_isolation', () => {
    const c1 = new c.BoundCache(), c2 = new c.BoundCache();
    const o = {};
    c1.store(o, 'a');
    assert(c2.load(o) === undefined);
  });
  rec('test_h_cache_bound_same_obj', () => {
    const c1 = new c.BoundCache();
    const o = {};
    c1.store(o, 7);
    assert(c1.load(o) === 7);
  });
  rec('test_h_cache_stamp_stable', () => {
    const o = {};
    assert(c.stamp(o) === c.stamp(o));
  });
  rec('test_h_cache_memoize_weak_calls', () => {
    let calls = 0;
    const f = c.memoizeWeak(o => ++calls);
    const a1 = {};
    f(a1); f(a1);
    assert(calls === 1);
  });

  // ---- async streams ---------------------------------------------------
  await arec('test_h_async_gen_range', async () => {
    eq(await drain(a.genRange(0, 3)), [0, 1, 2]);
  });
  await arec('test_h_async_gen_range_single', async () => {
    eq(await drain(a.genRange(2, 3)), [2]);
  });
  await arec('test_h_async_finally_full', async () => {
    const ev = [];
    for await (const v of a.genWithFinally(() => ev.push('fin'))) ev.push(v);
    eq(ev, [1, 2, 3, 'fin']);
  });
  await arec('test_h_async_finally_partial', async () => {
    const ev = [];
    const g = a.genWithFinally(() => ev.push('fin'));
    const origNext = g.next.bind(g);
    g.next = async function () {
      const step = await origNext();
      ev.push('v:' + step.value);
      return step;
    };
    const out = await a.firstN(g, 1);
    eq(out, [1]);
    eq(ev, ['v:1', 'fin']);
  });
  await arec('test_h_async_collect', async () => {
    eq(await a.collect(a.genRange(0, 3)), [0, 1, 2]);
  });
  await arec('test_h_async_collect_empty', async () => {
    async function* empty() {}
    eq(await a.collect(empty()), []);
  });
  await arec('test_h_async_first_n', async () => {
    let closed = false;
    async function* g() { try { yield 1; yield 2; } finally { closed = true; } }
    const out = await a.firstN(g(), 1);
    eq(out, [1]);
    assert(closed === true);
  });
  await arec('test_h_async_gen_pairs', async () => {
    eq(await drain(a.genPairs([1, 2, 3, 4, 5])), [[1, 2], [3, 4], [5, undefined]]);
  });

  // ---- numbers: primality correctness ---------------------------------
  rec('test_h_num_isprime_2', () => assert(n.isPrime(2) === true));
  rec('test_h_num_isprime_3', () => assert(n.isPrime(3) === true));
  rec('test_h_num_isprime_9', () => assert(n.isPrime(9) === false));
  rec('test_h_num_isprime_0', () => assert(n.isPrime(0) === false));
  rec('test_h_num_isprime_1', () => assert(n.isPrime(1) === false));
  rec('test_h_num_isprime_negative', () => assert(n.isPrime(-7) === false));
  rec('test_h_num_isprime_perfect_square_small', () => {
    assert(n.isPrime(49) === false);
    assert(n.isPrime(121) === false);
  });
  rec('test_h_num_isprime_large_prime', () => {
    assert(n.isPrime(2147483647) === true);
  });
  rec('test_h_num_isprime_large_composite', () => {
    assert(n.isPrime(2147483649) === false);
  });
  rec('test_h_num_isprime_large_square', () => {
    assert(n.isPrime(101 * 101) === false);
    assert(n.isPrime(1009 * 1009) === false);
  });

  // ---- numbers: primality performance ---------------------------------
  rec('test_h_num_isprime_perf_1m', () => {
    const t0 = Date.now();
    let count = 0, i = 0;
    for (; i < 1000000; i++) {
      if (n.isPrime(i)) count++;
      if (Date.now() - t0 > 2500) break;
    }
    const ms = Date.now() - t0;
    assert(i === 1000000);
    assert(ms < 2000);
    assert(count === 78498);
  });

  rec('test_h_num_isprime_complexity', () => {
    const t0 = Date.now();
    assert(n.isPrime(2147483647) === true);
    assert(Date.now() - t0 < 500);
  });

  // ---- numbers: related helpers ---------------------------------------
  rec('test_h_num_perfect_square_true', () => {
    assert(n.isPerfectSquare(4) === true);
    assert(n.isPerfectSquare(9) === true);
  });
  rec('test_h_num_perfect_square_false', () => {
    assert(n.isPerfectSquare(3) === false);
    assert(n.isPerfectSquare(10) === false);
  });
  rec('test_h_num_count_primes_7', () => assert(n.countPrimesUpTo(7) === 4));
  rec('test_h_num_count_primes_11', () => assert(n.countPrimesUpTo(11) === 5));
  rec('test_h_num_sum_primes', () => assert(n.sumPrimes(2, 11) === 28));

  process.exit(0);
})();
