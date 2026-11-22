'use strict';

/* Async-iteration utilities built on async generators. */

function syncRange(n) {
  const out = [];
  for (let i = 0; i < n; i++) out.push(i);
  return out;
}

async function* genRange(start, end) {
  for (let i = start; i <= end; i++) yield i;
}

async function* genWithFinally(cb) {
  cb();
  try {
    yield 1;
    yield 2;
    yield 3;
  } finally {
    /* release resources here */
  }
}

async function collect(gen) {
  const out = [];
  for (const v of gen) out.push(v);
  return out;
}

async function firstN(gen, n) {
  const out = [];
  for (let i = 0; i < n; i++) {
    const step = await gen.next();
    if (step.done) break;
    out.push(step.value);
  }
  return out;
}

async function* genPairs(arr) {
  for (let i = 0; i < arr.length - 1; i += 2) yield [arr[i], arr[i + 1]];
}

module.exports = { syncRange, genRange, genWithFinally, collect, firstN, genPairs };
