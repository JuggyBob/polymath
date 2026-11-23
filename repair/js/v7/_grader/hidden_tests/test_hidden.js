'use strict';

/* Hidden acceptance checks: canonical cases and the three perf workloads. */

const fs = require('fs');
const path = require('path');
const { performance } = require('perf_hooks');
const vm = require('../src/index.js');

const CASES = [
  {
    "name": "h_arith_precedence",
    "kind": "run",
    "source": "print 2 + 3 * 4 - 5; print 20 / 3 / 2; print -7 / 2;",
    "expected": "9\n3\n-3\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_str_concat_mixed",
    "kind": "run",
    "source": "print \"a\" + 1 + true; print null + \"x\";",
    "expected": "a1true\nnullx\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_escape_backslash",
    "kind": "run",
    "source": "print \"a\\\\b\"; print len(\"a\\\\b\");",
    "expected": "a\\b\n3\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_escape_quote",
    "kind": "run",
    "source": "print \"say \\\"hi\\\"\";",
    "expected": "say \"hi\"\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_ge_chain",
    "kind": "run",
    "source": "print 3 >= 3 == true; print 2 >= 5 == false;",
    "expected": "true\ntrue\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_ne_chain",
    "kind": "run",
    "source": "print 1 != 2 == true; print 2 != 2 == false;",
    "expected": "true\ntrue\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_ge_lexer",
    "kind": "run",
    "source": "print 4 >= 4; print 5 >= 9;",
    "expected": "true\nfalse\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_ne_lexer",
    "kind": "run",
    "source": "print 8 != 9; print 8 != 8;",
    "expected": "true\nfalse\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_lt_and_gt",
    "kind": "run",
    "source": "print 1 < 2; print 2 > 1; print 1 > 2; print 2 < 1;",
    "expected": "true\ntrue\nfalse\nfalse\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_le_and_ge",
    "kind": "run",
    "source": "print 1 <= 1; print 1 >= 1; print 1 <= 0; print 1 >= 2;",
    "expected": "true\ntrue\nfalse\nfalse\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_cmp_chain",
    "kind": "run",
    "source": "print 1 < 2 == true; print 2 <= 3 == true;",
    "expected": "true\ntrue\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_unary_chain",
    "kind": "run",
    "source": "print - - - 4; print ! ! ! false;",
    "expected": "-4\ntrue\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_nested_index",
    "kind": "run",
    "source": "let a = [[[1, 2]]]; print a[0][0][1];",
    "expected": "2\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_array_alias",
    "kind": "run",
    "source": "let a = [1]; let b = a; push b, 2; print a; print b;",
    "expected": "[1, 2]\n[1, 2]\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_distinct_structural",
    "kind": "run",
    "source": "print distinct([[1], [1]]); print distinct([[1], [2]]);",
    "expected": "false\ntrue\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_distinct_mixed",
    "kind": "run",
    "source": "print distinct([1, \"1\", true]); print distinct([null, null]);",
    "expected": "true\nfalse\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_truthy_empty_string",
    "kind": "run",
    "source": "if \"\" { print \"x\"; } else { print \"y\"; }",
    "expected": "y\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_truthy_empty_array",
    "kind": "run",
    "source": "if [] { print \"x\"; } else { print \"y\"; }",
    "expected": "y\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_truthy_values",
    "kind": "run",
    "source": "if 0 { print \"a\"; } else { print \"b\"; } if null { print \"c\"; } else { print \"d\"; } if \"s\" { print \"e\"; }",
    "expected": "b\nd\ne\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_str_cmp",
    "kind": "run",
    "source": "print \"b\" < \"aa\"; print \"aa\" < \"b\"; print \"abc\" == \"abc\";",
    "expected": "false\ntrue\ntrue\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_str_cmp_unicode",
    "kind": "run",
    "source": "print \"é\" > \"z\"; print \"é\" == \"é\";",
    "expected": "true\ntrue\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_add_vars",
    "kind": "run",
    "source": "let a = \"x\"; let b = \"y\"; print a + b;",
    "expected": "xy\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_print_repeat",
    "kind": "run",
    "source": "print 1; print 1; print 1;",
    "expected": "1\n1\n1\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_len_unicode",
    "kind": "run",
    "source": "print len(\"😀\"); print len(\"a\\tb\");",
    "expected": "1\n3\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_negative_index",
    "kind": "run",
    "source": "let a = [1, 2, 3]; print a[-1]; print a[9];",
    "expected": "null\nnull\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_push_sequence",
    "kind": "run",
    "source": "let a = [1]; push a, 2; push a, 3; push a, 4; print a;",
    "expected": "[1, 2, 3, 4]\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_empty_then",
    "kind": "run",
    "source": "if true { } else { print \"e\"; } print \"z\";",
    "expected": "z\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_nested_while",
    "kind": "run",
    "source": "let i = 0; while i < 2 { print i; set i = i + 1; let j = 0; while j < 2 { print 9; set j = j + 1; } }",
    "expected": "0\n9\n9\n1\n9\n9\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_array3",
    "kind": "run",
    "source": "print [1, 2, 3];",
    "expected": "[1, 2, 3]\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_null_eq",
    "kind": "run",
    "source": "print null == null; print null != null; print null == 0;",
    "expected": "true\nfalse\nfalse\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_fiber_three",
    "kind": "run",
    "source": "fiber a { print 1; yield; print 4; } fiber b { print 2; yield; print 5; } fiber c { print 3; yield; print 6; } spawn a; spawn b; spawn c; yield;",
    "expected": "1\n2\n3\n4\n5\n6\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_fiber_join_wait",
    "kind": "run",
    "source": "fiber w { print 1; yield; print 2; } let f = spawn w; join f; print 3;",
    "expected": "1\n2\n3\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_fiber_join_two_waiters",
    "kind": "run",
    "source": "fiber w { yield; print 9; } fiber a { yield; print \"a\"; } fiber b { yield; print \"b\"; } spawn w; spawn a; spawn b; yield;",
    "expected": "9\na\nb\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_fiber_yield_noop",
    "kind": "run",
    "source": "fiber a { yield; print 1; } spawn a; join 1; print 2;",
    "expected": "1\n2\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_distinct_exec",
    "kind": "exec",
    "source": "print distinct([1, 2]);",
    "expected": "true\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_distinct_roundtrip",
    "kind": "serial",
    "source": "print distinct([1, 2]);",
    "expected": "true\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_distinct_disasm",
    "kind": "serial",
    "source": "print distinct([1, 2]);",
    "expected": "",
    "expected_contains": "DISTINCT",
    "code": [],
    "api": ""
  },
  {
    "name": "h_serial_full",
    "kind": "serial",
    "source": "print \"a\" + \"b\"; print true; print false; let i = 0; while i < 2 { print i; set i = i + 1; }",
    "expected": "ab\ntrue\nfalse\n0\n1\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_serial_fibers",
    "kind": "serial",
    "source": "fiber a { print 1; } spawn a; join 1; print 2;",
    "expected": "1\n2\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_snapshot_roundtrip_run",
    "kind": "snapshot",
    "source": "let x = 5; print x + 1;",
    "expected": "6\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_snapshot_globals",
    "kind": "snapshot",
    "source": "let a = [1, 2]; let s = \"hi\"; print len(a) + len(s);",
    "expected": "4\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_snapshot_fibers",
    "kind": "snapshot",
    "source": "fiber a { print 1; yield; print 2; } spawn a; yield;",
    "expected": "1\n2\n",
    "expected_contains": "",
    "code": [],
    "api": ""
  },
  {
    "name": "h_snapshot_badmagic",
    "kind": "snapshot",
    "source": "",
    "expected": "BAD_MAGIC",
    "expected_contains": "",
    "code": [],
    "api": "restore(b'NOPE' + b'\\x00' * 32)"
  },
  {
    "name": "h_snapshot_badversion",
    "kind": "snapshot",
    "source": "",
    "expected": "BAD_VERSION",
    "expected_contains": "",
    "code": [],
    "api": "restore(b'MV7' + b'\\x09' + b'\\x00' * 32)"
  },
  {
    "name": "h_snapshot_truncated",
    "kind": "snapshot",
    "source": "",
    "expected": "TRUNCATED",
    "expected_contains": "",
    "code": [],
    "api": "restore(good_bytes[:-3])"
  },
  {
    "name": "h_snapshot_badchecksum",
    "kind": "snapshot",
    "source": "",
    "expected": "BAD_CHECKSUM",
    "expected_contains": "",
    "code": [],
    "api": "restore(good_bytes[:-1] + bytes([good_bytes[-1] ^ 0x01]))"
  },
  {
    "name": "h_snapshot_duplicate_fiber",
    "kind": "snapshot",
    "source": "",
    "expected": "DUPLICATE_FIBER",
    "expected_contains": "",
    "code": [],
    "api": "restore(bytes_with_duplicate_fiber_ids)"
  },
  {
    "name": "h_load_uninit",
    "kind": "exec",
    "source": "",
    "expected": "null\n",
    "expected_contains": "",
    "code": "[Load(0), Print, Halt]",
    "api": ""
  },
  {
    "name": "h_stack_ops",
    "kind": "exec",
    "source": "",
    "expected": "2\n3\n9\n",
    "expected_contains": "",
    "code": "[PushInt(1), Dup, Add, Print, PushInt(3), PushInt(9), Swap, Print, Print, Halt]",
    "api": ""
  }
];

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

function errorOf(fn) {
  try { fn(); return '<no error>'; }
  catch (e) { return e && e.message ? e.message : String(e); }
}

function snapshotApi(name) {
  const code = { ops: [{ op: vm.OP.HALT }], globals: [], fibers: {} };
  const good = vm.MiniVM.fromSource('let x = 5; print x + 1;').snapshot();
  switch (name) {
    case 'h_snapshot_badmagic':
      return errorOf(() => vm.restore(Buffer.concat([Buffer.from('NOPE'), Buffer.alloc(32)])));
    case 'h_snapshot_badversion':
      return errorOf(() => vm.restore(Buffer.concat([Buffer.from('MV7'), Buffer.from([9]), Buffer.alloc(32)])));
    case 'h_snapshot_truncated':
      return errorOf(() => vm.restore(good.subarray(0, good.length - 3)));
    case 'h_snapshot_badchecksum': {
      const bad = Buffer.from(good);
      bad[bad.length - 1] = bad[bad.length - 1] ^ 0x01;
      return errorOf(() => vm.restore(bad));
    }
    case 'h_snapshot_duplicate_fiber': {
      const bytes = vm.snapshot.encode({
        code,
        globals: [],
        fibers: [{ id: 1, pc: 0, stack: [] }, { id: 1, pc: 0, stack: [] }],
        ready: [1, 1],
        blocked: []
      });
      return errorOf(() => vm.restore(bytes));
    }
    default:
      return '<unknown>';
  }
}

const OP_ALIAS = {
  PushInt: 'PUSH', Load: 'LOAD', Print: 'PRINT', Halt: 'HALT',
  Dup: 'DUP', Add: 'ADD', Swap: 'SWAP'
};
function rawCode(code) {
  const items = Array.isArray(code) ? code
    : String(code).replace(/^\[/, '').replace(/\]$/, '').split(',').map(s => s.trim()).filter(Boolean);
  const ops = [];
  for (const item of items) {
    const m = /^(\w+)(?:\((.+)\))?$/.exec(item);
    if (!m) throw new Error('bad code item ' + item);
    const name = OP_ALIAS[m[1]] || m[1];
    const op = vm.OP[name];
    if (op === undefined) throw new Error('unknown op ' + name);
    ops.push(m[2] === undefined ? { op } : { op, arg: Number(m[2]) });
  }
  return vm.execute({ ops, globals: [], fibers: {} });
}

function runCase(c) {
  if (c.kind === 'snapshot' && c.api) return snapshotApi(c.name);
  if (c.kind === 'exec' && c.code.length) return rawCode(c.code);
  if (c.kind === 'exec') return vm.execute(vm.compileSource(c.source));
  if (c.kind === 'serial') {
    const code = vm.compileSource(c.source);
    if (c.expected_contains) return vm.disassemble(code).includes(c.expected_contains);
    return vm.execute(vm.deserialize(vm.serialize(code)));
  }
  if (c.kind === 'snapshot') {
    return vm.restore(vm.MiniVM.fromSource(c.source).snapshot()).run();
  }
  return vm.run(c.source);
}

for (const c of CASES) {
  test(c.name, () => {
    const actual = runCase(c);
    if (c.expected_contains) eq(actual, true);
    else eq(actual, c.expected);
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
