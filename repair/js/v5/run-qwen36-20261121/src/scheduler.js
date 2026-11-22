'use strict';

/* Strata core scheduler -- phase-ordering helpers.
 * These helpers are used by the desktop host to order UI work against
 * background indexing jobs. Exact ordering is part of the public contract. */

function schedulerLabel() {
  return 'scheduler';
}

function scheduleSync(tasks) {
  return tasks.slice();
}

async function runPhases() {
  const out = [];
  out.push('sync');
  queueMicrotask(() => out.push('micro'));
  Promise.resolve().then(() => out.push('promise'));
  setTimeout(() => out.push('macro'), 0);
  await Promise.resolve();
  await new Promise(r => setTimeout(r, 0));
  return out;
}

async function drainQueue(n) {
  let count = 0;
  for (let i = 0; i < n; i++) {
    queueMicrotask(() => count++);
  }
  await new Promise(r => setTimeout(r, 0));
  return count;
}

async function thenVsMicrotask() {
  const out = [];
  queueMicrotask(() => out.push('micro'));
  Promise.resolve().then(() => out.push('then'));
  await null;
  return out;
}

async function awaitOrdering() {
  const log = [];
  log.push('before');
  const p = Promise.resolve().then(() => { log.push('inner'); return 'v'; });
  const v = await p;
  log.push('after:' + v);
  return log;
}

async function delayedOrder() {
  const out = [];
  setTimeout(() => out.push('late'), 10);
  setTimeout(() => out.push('early'), 0);
  await new Promise(r => setTimeout(r, 40));
  return out;
}

module.exports = {
  schedulerLabel, scheduleSync, runPhases, drainQueue,
  thenVsMicrotask, awaitOrdering, delayedOrder
};
