'use strict';
const A = require('../src/async.js');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const unhandled = [];
process.on('unhandledRejection', (e) => { unhandled.push(e); });

function CHECK(name, cond) {
  console.log('TEST ' + name + ' ' + (cond ? 'PASS' : 'FAIL'));
}

(async () => {
  // retry: needs a third attempt after two failures.
  let ra = 0, rv, rerr = null;
  try {
    rv = await A.retry(async () => { ra++; if (ra < 3) throw new Error('x'); return 42; }, 2);
  } catch (e) { rerr = e; }
  CHECK('retry_eventually', !rerr && rv === 42 && ra === 3);

  let rb = 0;
  const rv2 = await A.retry(async () => { rb++; return 7; }, 1);
  CHECK('retry_first_try', rv2 === 7 && rb === 1);

  let to = 'none';
  try { await A.withTimeout(new Promise(() => {}), 20); to = 'resolved'; }
  catch (e) { to = e.message; }
  CHECK('timeout_deadline', to === 'timeout');

  let src = 'pending';
  A.withTimeout(Promise.reject(new Error('boom')), 20).then(
    () => { src = 'resolved'; },
    (e) => { src = e.message; }
  );
  await sleep(50);
  CHECK('timeout_source_reject', src === 'boom');

  const ml = await A.mapLimit([10, 5, 1], 3, async (n) => { await sleep(n); return n; });
  CHECK('maplimit_order', JSON.stringify(ml) === '[10,5,1]');

  let active = 0, maxActive = 0;
  await A.mapLimit([1, 2, 3, 4], 2, async (n) => {
    active++; maxActive = Math.max(maxActive, active);
    await sleep(5); active--; return n;
  });
  CHECK('maplimit_concurrency', maxActive <= 2);

  const e1 = new A.Emitter();
  let seenThis;
  e1.on('x', function () { seenThis = this; });
  const had = e1.emit('x');
  CHECK('emitter_emit_this', had === true && seenThis === e1);

  const e2 = new A.Emitter();
  let c2 = 0;
  const f2 = () => { c2++; };
  e2.on('y', f2); e2.off('y', f2); e2.emit('y');
  CHECK('emitter_off_regular', c2 === 0);

  const e3 = new A.Emitter();
  let c3 = 0;
  e3.once('z', () => { c3++; });
  e3.emit('z'); e3.emit('z');
  CHECK('emitter_once', c3 === 1);

  const e4 = new A.Emitter();
  let c4 = 0;
  const f4 = () => { c4++; };
  e4.once('w', f4); e4.off('w', f4); e4.emit('w');
  CHECK('emitter_off_once', c4 === 0);

  let dcount = 0, dlast = null;
  const dfn = A.debounce(function (v) { dcount++; dlast = v; }, 20);
  dfn('a'); dfn('b'); dfn('c');
  await sleep(50);
  CHECK('debounce_trailing', dcount === 1 && dlast === 'c');

  let mc = 0;
  const memo = A.memoizeAsync(async (n) => { mc++; return n * 2; });
  const m1 = await memo(3), m2 = await memo(3);
  CHECK('memoize_sequential', m1 === 6 && m2 === 6 && mc === 1);

  let cc = 0;
  const cmemo = A.memoizeAsync(async (n) => { cc++; await sleep(10); return n; });
  const [mc1, mc2] = await Promise.all([cmemo('k'), cmemo('k')]);
  CHECK('memoize_concurrent', mc1 === 'k' && mc2 === 'k' && cc === 1);

  const poolIdx = [];
  await A.promisePool(['a', 'b', 'c'], 2, async (item, idx) => {
    poolIdx.push(idx); await sleep(2); return item.toUpperCase();
  });
  CHECK('pool_slot_index', poolIdx.length === 3 && poolIdx.every((i) => i === 0 || i === 1) &&
    poolIdx.includes(0) && poolIdx.includes(1));
})().catch((e) => {
  console.log('FATAL ' + ((e && e.stack) || e));
  process.exitCode = 1;
});
