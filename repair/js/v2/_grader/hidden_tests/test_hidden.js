'use strict';
const A = require('../src/async.js');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const unhandled = [];
process.on('unhandledRejection', (e) => { unhandled.push(e); });

function CHECK(name, cond) {
  console.log('TEST ' + name + ' ' + (cond ? 'PASS' : 'FAIL'));
}

(async () => {
  // ---- passing on the buggy version (regression guard) ----
  let r1 = 0;
  const rv1 = await A.retry(async () => { r1++; return 'v'; }, 1);
  CHECK('h_retry_success', rv1 === 'v' && r1 === 1);

  let r2 = 0;
  let e2 = null;
  try {
    await A.retry(async () => { r2++; throw new Error('boom'); }, 1);
  } catch (e) { e2 = e; }
  CHECK('h_retry_exhaust', !!e2 && e2.message === 'boom' && r2 >= 1);

  CHECK('h_timeout_resolve', (await A.withTimeout(Promise.resolve(1), 50)) === 1);

  let td = 'none';
  try { await A.withTimeout(new Promise(() => {}), 15); td = 'resolved'; }
  catch (e) { td = e.message; }
  CHECK('h_timeout_deadline', td === 'timeout');

  const mv = await A.mapLimit([1, 2, 3], 3, async (n) => { await sleep(1); return n * 2; });
  CHECK('h_maplimit_values', JSON.stringify(mv.slice().sort((a, b) => a - b)) === '[2,4,6]');
  CHECK('h_maplimit_empty', JSON.stringify(await A.mapLimit([], 2, async (x) => x)) === '[]');

  const em = new A.Emitter();
  let seen = [];
  em.on('e', (a, b) => seen.push(a + b));
  const called = em.emit('e', 2, 3);
  CHECK('h_emitter_basic', called === true && seen.length === 1 && seen[0] === 5);

  const em2 = new A.Emitter();
  let c = 0;
  const f = () => { c++; };
  em2.on('q', f); em2.off('q', f); em2.emit('q');
  CHECK('h_emitter_off_regular', c === 0);
  CHECK('h_emitter_emit_false', new A.Emitter().emit('nothing') === false);

  let dbc = 0, dbArg = null;
  const db = A.debounce(function (v) { dbc++; dbArg = v; }, 10);
  db('only');
  await sleep(40);
  CHECK('h_debounce_single', dbc === 1 && dbArg === 'only');

  let sc = 0;
  const sm = A.memoizeAsync(async (n) => { sc++; return n + 1; });
  const s1 = await sm(4), s2 = await sm(4);
  CHECK('h_memoize_sequential', s1 === 5 && s2 === 5 && sc === 1);

  let kc = 0;
  const km = A.memoizeAsync(async (n) => { kc++; return 'v' + n; });
  await km(1); await km('1');
  CHECK('h_memoize_key_types', kc === 2);

  const pool = await A.promisePool(['a', 'b'], 1, async (x) => x + '!');
  CHECK('h_pool_results', JSON.stringify(pool) === '["a!","b!"]');

  // ---- failing on the buggy version ----
  let ra = 0, rrv, rerr = null;
  try {
    rrv = await A.retry(async () => { ra++; if (ra < 3) throw new Error('x'); return 9; }, 2);
  } catch (e) { rerr = e; }
  CHECK('h_retry_attempts', !rerr && rrv === 9 && ra === 3);

  let src = 'pending';
  A.withTimeout(Promise.reject(new Error('boom')), 15).then(
    () => { src = 'resolved'; },
    (e) => { src = e.message; }
  );
  await sleep(45);
  CHECK('h_timeout_source_reject', src === 'boom');

  const ordered = await A.mapLimit([12, 4, 1], 3, async (n) => { await sleep(n); return n; });
  CHECK('h_maplimit_order', JSON.stringify(ordered) === '[12,4,1]');

  const ethis = new A.Emitter();
  let bound = null;
  ethis.on('t', function () { bound = this; });
  ethis.emit('t');
  CHECK('h_emitter_this', bound === ethis);

  const eonce = new A.Emitter();
  let oc = 0;
  eonce.once('o', () => { oc++; });
  eonce.emit('o'); eonce.emit('o');
  CHECK('h_emitter_once', oc === 1);

  let dcc = 0;
  const dbf = A.debounce(() => { dcc++; }, 15);
  dbf(); dbf(); dbf();
  await sleep(45);
  CHECK('h_debounce_wait', dcc === 1);

  let cc = 0;
  const cm = A.memoizeAsync(async (n) => { cc++; await sleep(10); return n; });
  const [a, b] = await Promise.all([cm('key'), cm('key')]);
  CHECK('h_memoize_concurrent', a === 'key' && b === 'key' && cc === 1);
})().catch((e) => {
  console.log('FATAL ' + ((e && e.stack) || e));
  process.exitCode = 1;
});
