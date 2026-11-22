'use strict';

/* Hidden acceptance checks: correct end-to-end behaviour and performance. */

const vm = require('../src/index.js');
const rt = vm.runtime;

let failures = 0;
function test(name, fn) {
  try { fn(); console.log('TEST ' + name + ' PASS'); }
  catch (e) { failures++; console.log('TEST ' + name + ' FAIL'); }
}
function assert(cond, msg) { if (!cond) throw new Error(msg || 'assertion failed'); }
function eq(x, y) { assert(x === y, JSON.stringify(x) + ' !== ' + JSON.stringify(y)); }
function arrEq(x, y) { assert(JSON.stringify(x) === JSON.stringify(y)); }

function perf(name, fn, limit) {
  const { performance } = require('perf_hooks');
  for (let i = 0; i < 3; i++) {
    const t0 = performance.now();
    fn();
    const ms = performance.now() - t0;
    console.log('PERF ' + name + ' ' + ms.toFixed(3) + ' ' + (ms < limit ? 'PASS' : 'FAIL'));
  }
}

test('test_h_exports', () => {
  ['tokenize', 'parse', 'compile', 'execute', 'disassemble', 'serialize',
   'deserialize', 'run', 'runBytecode', 'pipeline'].forEach(k => assert(typeof vm[k] === 'function', k));
  ['toStr', 'truthy', 'cachedValue', 'sumRange', 'methodCall', 'collectGen',
   'orderedMicrotasks', 'proxyArray', 'distinctValues'].forEach(k => assert(typeof rt[k] === 'function', k));
});

test('test_h_add', () => eq(vm.run('print 1 + 2;'), '3\n'));
test('test_h_string_literal', () => eq(vm.run('print "hello";'), 'hello\n'));
test('test_h_null_print', () => eq(vm.run('print null;'), 'null\n'));
test('test_h_neg', () => eq(vm.run('print -5;'), '-5\n'));
test('test_h_array_nested', () => eq(vm.run('print [[1], [2]];'), '[[1], [2]]\n'));
test('test_h_while_sum', () => eq(vm.run('let s = 0; let i = 0; while i < 5 { s = s + i; i = i + 1; } print s;'), '10\n'));

test('test_h_ge_true', () => eq(vm.run('print 5 >= 3;'), 'true\n'));
test('test_h_ge_false', () => eq(vm.run('print 3 >= 5;'), 'false\n'));
test('test_h_or', () => eq(vm.run('print true || false;'), 'true\n'));
test('test_h_escape', () => eq(vm.run('print "a\\nb";'), 'a\nb\n'));
test('test_h_sub_chain', () => eq(vm.run('print 10 - 3 - 2;'), '5\n'));
test('test_h_unary_precedence', () => eq(vm.run('print -2 + 3;'), '1\n'));
test('test_h_nested_else', () => eq(vm.run('if false { if true { print 1; } } else { print 2; }'), '2\n'));
test('test_h_setidx_chain', () => eq(vm.run('let a = [1, 2]; a[0] = 5; a[1] = 6; print a;'), '[5, 6]\n'));
test('test_h_idx_oob', () => eq(vm.run('let a = [1, 2]; print a[5];'), 'null\n'));
test('test_h_len_string', () => eq(vm.run('print len("abcd");'), '4\n'));
test('test_h_mod', () => eq(vm.run('print 7 % 3;'), '1\n'));
test('test_h_div_trunc', () => eq(vm.run('print 7 / 2;'), '3\n'));
test('test_h_and_bool', () => eq(vm.run('print 1 && 0;'), 'false\n'));
test('test_h_mixed_concat', () => eq(vm.run('print "x" + 1;'), 'x1\n'));

const DISTINCT_SRC = 'print distinct([1, 2, 1, 3, 2]);';
test('test_h_distinct_exec', () => eq(vm.run(DISTINCT_SRC), '[1, 2, 3]\n'));
test('test_h_distinct_disasm', () => assert(vm.disassemble(vm.compile(DISTINCT_SRC)).indexOf('DISTINCT') >= 0));
test('test_h_distinct_token', () => assert(vm.serialize(vm.compile(DISTINCT_SRC)).indexOf('DISTINCT') >= 0));
test('test_h_distinct_roundtrip', () => eq(vm.execute(vm.deserialize(vm.serialize(vm.compile(DISTINCT_SRC)))), '[1, 2, 3]\n'));
test('test_h_roundtrip_big', () => eq(vm.execute(vm.deserialize(vm.serialize(vm.compile('print 300;')))), '300\n'));
test('test_h_disasm_mul', () => assert(vm.disassemble(vm.compile('print 2 * 3;')).indexOf('MUL') >= 0));
test('test_h_disasm_backjump', () => assert(vm.disassemble(vm.compile('while true { print 1; }')).indexOf('JMP 0') >= 0));

test('test_h_proxy_index2', () => eq(rt.proxyArray([1, 2, 3])[2], 3));
test('test_h_cache_identity', () => {
  const a = {}; const b = {};
  Object.defineProperty(a, 'id', { value: 1 });
  Object.defineProperty(b, 'id', { value: 2 });
  eq(JSON.stringify(a), JSON.stringify(b));
  eq(rt.cachedValue(a, o => o.id), 1);
  eq(rt.cachedValue(b, o => o.id), 2);
});
test('test_h_method_this', () => {
  const o = { tag: 'ok', get() { return this.tag; } };
  eq(rt.methodCall(o, 'get'), 'ok');
});
test('test_h_collect_gen', () => {
  function* g() { yield 1; yield 2; yield 3; yield 4; }
  arrEq(rt.collectGen(g()), [1, 2, 3, 4]);
});
test('test_h_run_env_reset', () => {
  vm.run('let q = 1; print q;');
  eq(vm.run('print q;'), 'undefined\n');
});

async function main() {
  const order = await rt.orderedMicrotasks(['a', 'b', 'c', 'd']);
  test('test_h_microtask_order', () => arrEq(order, ['a', 'b', 'c', 'd']));

  perf('perf_sumrange', () => rt.sumRange(30000), 5);
  const many = [];
  for (let i = 0; i < 3000; i++) many.push({ op: vm.OP.PUSH, arg: i });
  perf('perf_serialize', () => vm.serialize(many), 25);

  process.exit(failures ? 1 : 0);
}
main();
