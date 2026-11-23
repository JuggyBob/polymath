'use strict';

/* Visible acceptance checks. The example programs are the behaviour spec. */

const fs = require('fs');
const path = require('path');
const cp = require('child_process');
const { performance } = require('perf_hooks');
const vm = require('../src/index.js');

let failures = 0;
function test(name, fn) {
  try { fn(); console.log('TEST ' + name + ' PASS'); }
  catch (e) { failures++; console.log('TEST ' + name + ' FAIL'); }
}
function eq(x, y) {
  if (x !== y) throw new Error(JSON.stringify(x) + ' !== ' + JSON.stringify(y));
}
function perf(name, fn, limit) {
  for (let i = 0; i < 3; i++) {
    let ms = 0;
    let ok = true;
    const t0 = performance.now();
    try { fn(); } catch (e) { ok = false; }
    ms = performance.now() - t0;
    console.log('PERF ' + name + ' ' + ms.toFixed(3) + ' ' + (ok && ms < limit ? 'PASS' : 'FAIL'));
  }
}

const exDir = path.join(__dirname, '..', 'examples');

/* Canonical example names in manifest order (prog01..prog45). */
const NAMES = [
  'prog01_arith',
  'prog02_strings',
  'prog03_values',
  'prog04_variables',
  'prog05_arrays',
  'prog06_if',
  'prog07_while',
  'prog08_compare_ge',
  'prog09_compare_ne',
  'prog10_escape_nul',
  'prog11_escape_tab',
  'prog12_cmp_chain',
  'prog13_unary_chain',
  'prog14_nested_index',
  'prog15_truthy',
  'prog16_str_cmp',
  'prog17_add_vars',
  'prog18_print_repeat',
  'prog19_len_unicode',
  'prog20_negative_index',
  'prog21_push_sequence',
  'prog22_empty_then',
  'prog23_nested_while',
  'prog24_array3',
  'prog25_null_eq',
  'prog26_distinct_basic',
  'prog27_distinct_types',
  'prog28_fiber_basic',
  'prog29_fiber_yield',
  'prog30_fiber_join_halted',
  'prog31_snapshot_roundtrip',
  'prog32_snapshot_badmagic',
  'prog33_array_alias',
  'prog34_distinct_nested',
  'prog35_str_cmp_unicode',
  'prog36_serial_roundtrip',
  'prog37_disasm_distinct',
  'prog38_snapshot_fibers',
  'prog39_snapshot_badversion',
  'prog40_snapshot_truncated',
  'prog41_snapshot_badchecksum',
  'prog42_snapshot_duplicate',
  'prog43_load_uninit',
  'prog44_stack_ops',
  'prog45_serial_fibers'
];

for (const name of NAMES) {
  test(name, () => {
    const expected = fs.readFileSync(path.join(exDir, name + '.expected'), 'utf8');
    let actual = '';
    try {
      actual = cp.execFileSync(process.execPath, [path.join(exDir, name + '.js')], {
        encoding: 'utf8', timeout: 30000, stdio: ['ignore', 'pipe', 'ignore']
      });
    } catch (e) {
      actual = e.stdout || '';
    }
    eq(actual, expected);
  });
}

const PRINT_WORKLOAD = 'let i = 0; while i < 60000 { print i; set i = i + 1; }';
perf('perf_print', () => vm.run(PRINT_WORKLOAD), 250);
perf('perf_disasm', () => {
  const ops = new Array(20000);
  for (let i = 0; i < ops.length; i++) ops[i] = { op: vm.OP.PUSH, arg: i };
  vm.disassemble({ ops, globals: [], fibers: {} });
}, 200);
perf('perf_snapshot', () => {
  const ops = [];
  for (let i = 0; i < 100; i++) {
    ops.push({ op: vm.OP.PUSH, arg: i });
    ops.push({ op: vm.OP.STORE, arg: i });
  }
  const globals = new Array(2000);
  for (let i = 0; i < globals.length; i++) globals[i] = 'g' + i;
  const m = new vm.MiniVM({ ops, globals, fibers: {} });
  vm.restore(m.snapshot());
}, 250);

process.exit(failures ? 1 : 0);
