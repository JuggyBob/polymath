'use strict';

const s = require('../src/scheduler.js');
const p = require('../src/proxyStore.js');
const c = require('../src/cache.js');
const a = require('../src/asyncStream.js');
const n = require('../src/numbers.js');

let failures = 0;
function test(name, fn) {
  try { fn(); console.log('TEST ' + name + ' PASS'); }
  catch (e) { failures++; console.log('TEST ' + name + ' FAIL'); }
}
function assert(cond) { if (!cond) throw new Error('assertion failed'); }
function eq(x, y) { assert(JSON.stringify(x) === JSON.stringify(y)); }

test('test_v_exports', () => {
  ['schedulerLabel', 'scheduleSync', 'runPhases', 'drainQueue',
   'thenVsMicrotask', 'awaitOrdering', 'delayedOrder'].forEach(k => assert(typeof s[k] === 'function'));
  ['createPlainStore', 'countingGet', 'numericSet', 'strictHas',
   'listedKeys', 'resettable', 'descriptorProxy'].forEach(k => assert(typeof p[k] === 'function'));
  ['identity', 'memoize', 'stamp', 'memoizeWeak'].forEach(k => assert(typeof c[k] === 'function'));
  assert(typeof c.BoundCache === 'function');
  ['syncRange', 'genRange', 'genWithFinally', 'collect', 'firstN', 'genPairs'].forEach(k => assert(typeof a[k] === 'function'));
  ['isEven', 'square', 'add', 'isPrime', 'isPerfectSquare', 'countPrimesUpTo', 'sumPrimes'].forEach(k => assert(typeof n[k] === 'function'));
});

test('test_v_scheduler_label', () => eq(s.schedulerLabel(), 'scheduler'));
test('test_v_schedule_sync', () => eq(s.scheduleSync([1, 2, 3]), [1, 2, 3]));
test('test_v_plain_store', () => { const st = p.createPlainStore(); st.x = 3; eq(st.x, 3); });
test('test_v_identity', () => { const o = {}; assert(c.identity(o) === o); });
test('test_v_sync_range', () => eq(a.syncRange(4), [0, 1, 2, 3]));
test('test_v_is_even', () => { assert(n.isEven(4) === true); assert(n.isEven(3) === false); });
test('test_v_square', () => eq(n.square(5), 25));
test('test_v_add', () => eq(n.add(2, 3), 5));
test('test_v_isprime_two', () => assert(n.isPrime(2) === true));
test('test_v_isprime_three', () => assert(n.isPrime(3) === true));
test('test_v_isprime_eight', () => assert(n.isPrime(8) === false));

process.exit(failures ? 1 : 0);
