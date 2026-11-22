'use strict';

/* Visible acceptance checks. The example programs are the behaviour spec. */

const fs = require('fs');
const path = require('path');
const { performance } = require('perf_hooks');
const vm = require('../src/index.js');

let failures = 0;
function test(name, fn) {
  try { fn(); console.log('TEST ' + name + ' PASS'); }
  catch (e) { failures++; console.log('TEST ' + name + ' FAIL'); }
}
function assert(cond, msg) { if (!cond) throw new Error(msg || 'assertion failed'); }
function eq(x, y) { assert(x === y, JSON.stringify(x) + ' !== ' + JSON.stringify(y)); }
function arrEq(x, y) { assert(JSON.stringify(x) === JSON.stringify(y)); }

function perf(name, fn, limit) {
  for (let i = 0; i < 3; i++) {
    const t0 = performance.now();
    fn();
    const ms = performance.now() - t0;
    console.log('PERF ' + name + ' ' + ms.toFixed(3) + ' ' + (ms < limit ? 'PASS' : 'FAIL'));
  }
}

const exDir = path.join(__dirname, '..', 'examples');
const files = fs.readdirSync(exDir).filter(f => f.endsWith('.txt')).sort();
const asyncCases = [];
const perfCases = [];

function runApi(code) {
  const lines = [];
  const shim = { log: (...a) => lines.push(a.map(String).join(' ')) };
  new Function('vm', 'console', 'perf', code)(vm, shim, perf);
  return lines.length ? lines.join('\n') + '\n' : '';
}

async function runApiAsync(code) {
  const lines = [];
  const shim = { log: (...a) => lines.push(a.map(String).join(' ')) };
  const fn = new Function('vm', 'console', 'perf',
    'return (async () => {\n' + code + '\n})();');
  await fn(vm, shim, perf);
  return lines.length ? lines.join('\n') + '\n' : '';
}

for (const f of files) {
  const name = f.replace('.txt', '');
  const src = fs.readFileSync(path.join(exDir, f), 'utf8');
  if (src.startsWith('// @api-perf')) {
    perfCases.push({ name, src });
    continue;
  }
  if (src.startsWith('// @api-async')) {
    asyncCases.push({ name, src, expected: fs.readFileSync(path.join(exDir, name + '.expected'), 'utf8') });
    continue;
  }
  test('example_' + name, () => {
    const expected = fs.readFileSync(path.join(exDir, name + '.expected'), 'utf8');
    const actual = src.startsWith('// @api') ? runApi(src) : vm.run(src);
    eq(actual, expected);
  });
}

async function main() {
  for (const c of asyncCases) {
    const actual = await runApiAsync(c.src);
    test('example_' + c.name, () => eq(actual, c.expected));
  }
  for (const c of perfCases) {
    console.log('----- perf example ' + c.name + ' -----');
    runApi(c.src);
  }
  process.exit(failures ? 1 : 0);
}
main();
