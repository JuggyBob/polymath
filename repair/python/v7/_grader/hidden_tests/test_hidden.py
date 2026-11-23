"""Hidden acceptance tests for MiniVM v7.

Correctness lines: TEST <name> PASS|FAIL
Performance lines: PERF <name> <milliseconds> PASS|FAIL  (three runs each)
"""
import os
import struct
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from vm import (MiniVM, MiniVMError, VM, compile_source, deserialize,  # noqa: E402
                disassemble, execute, make_snapshot, restore, run, serialize)
from vm import opcodes as O  # noqa: E402
from vm.snapshot import fnv1a  # noqa: E402


def check(name, ok):
    print("TEST %s %s" % (name, "PASS" if ok else "FAIL"))


def run_case(name, source, expected):
    try:
        got = run(source)
    except Exception as exc:
        got = "<%s: %s>" % (type(exc).__name__, exc)
    check(name, got == expected)


def exec_case(name, source, expected):
    try:
        got = execute(compile_source(source))
    except Exception as exc:
        got = "<%s: %s>" % (type(exc).__name__, exc)
    check(name, got == expected)


def raw_case(name, code, expected):
    try:
        got = execute(code)
    except Exception as exc:
        got = "<%s: %s>" % (type(exc).__name__, exc)
    check(name, got == expected)


def serial_case(name, source, expected):
    try:
        code = compile_source(source)
        got = execute(deserialize(serialize(code)))
    except Exception as exc:
        got = "<%s: %s>" % (type(exc).__name__, exc)
    check(name, got == expected)


def disasm_case(name, source, wanted):
    try:
        text = disassemble(compile_source(source))
    except Exception:
        text = ""
    check(name, wanted in text)


def api_case(name, expression, expected, namespace):
    try:
        result = eval(expression, globals(), namespace)
        got = str(result)
    except MiniVMError as exc:
        got = str(exc)
    except Exception as exc:
        got = "<%s: %s>" % (type(exc).__name__, exc)
    check(name, got == expected)


def snapshot_case(name, source, expected):
    try:
        blob = MiniVM.from_source(source).snapshot()
        got = restore(blob).run()
    except Exception as exc:
        got = "<%s: %s>" % (type(exc).__name__, exc)
    check(name, got == expected)


def perf(name, limit_ms, action):
    for _ in range(3):
        start = time.perf_counter()
        try:
            action()
            ok = True
        except Exception:
            ok = False
        elapsed = (time.perf_counter() - start) * 1000.0
        print("PERF %s %.3f %s" % (
            name, elapsed, "PASS" if ok and elapsed <= limit_ms else "FAIL"))


def main():
    good_bytes = MiniVM.from_source("let x = 5; print x + 1;").snapshot()
    run_case('h_arith_precedence', 'print 2 + 3 * 4 - 5; print 20 / 3 / 2; print -7 / 2;', '9\n3\n-3\n')
    run_case('h_str_concat_mixed', 'print "a" + 1 + true; print null + "x";', 'a1true\nnullx\n')
    run_case('h_escape_backslash', 'print "a\\\\b"; print len("a\\\\b");', 'a\\b\n3\n')
    run_case('h_escape_quote', 'print "say \\"hi\\"";', 'say "hi"\n')
    run_case('h_ge_chain', 'print 3 >= 3 == true; print 2 >= 5 == false;', 'true\ntrue\n')
    run_case('h_ne_chain', 'print 1 != 2 == true; print 2 != 2 == false;', 'true\ntrue\n')
    run_case('h_ge_lexer', 'print 4 >= 4; print 5 >= 9;', 'true\nfalse\n')
    run_case('h_ne_lexer', 'print 8 != 9; print 8 != 8;', 'true\nfalse\n')
    run_case('h_lt_and_gt', 'print 1 < 2; print 2 > 1; print 1 > 2; print 2 < 1;', 'true\ntrue\nfalse\nfalse\n')
    run_case('h_le_and_ge', 'print 1 <= 1; print 1 >= 1; print 1 <= 0; print 1 >= 2;', 'true\ntrue\nfalse\nfalse\n')
    run_case('h_cmp_chain', 'print 1 < 2 == true; print 2 <= 3 == true;', 'true\ntrue\n')
    run_case('h_unary_chain', 'print - - - 4; print ! ! ! false;', '-4\ntrue\n')
    run_case('h_nested_index', 'let a = [[[1, 2]]]; print a[0][0][1];', '2\n')
    run_case('h_array_alias', 'let a = [1]; let b = a; push b, 2; print a; print b;', '[1, 2]\n[1, 2]\n')
    run_case('h_distinct_structural', 'print distinct([[1], [1]]); print distinct([[1], [2]]);', 'false\ntrue\n')
    run_case('h_distinct_mixed', 'print distinct([1, "1", true]); print distinct([null, null]);', 'true\nfalse\n')
    run_case('h_truthy_empty_string', 'if "" { print "x"; } else { print "y"; }', 'y\n')
    run_case('h_truthy_empty_array', 'if [] { print "x"; } else { print "y"; }', 'y\n')
    run_case('h_truthy_values', 'if 0 { print "a"; } else { print "b"; } if null { print "c"; } else { print "d"; } if "s" { print "e"; }', 'b\nd\ne\n')
    run_case('h_str_cmp', 'print "b" < "aa"; print "aa" < "b"; print "abc" == "abc";', 'false\ntrue\ntrue\n')
    run_case('h_str_cmp_unicode', 'print "é" > "z"; print "é" == "é";', 'true\ntrue\n')
    run_case('h_add_vars', 'let a = "x"; let b = "y"; print a + b;', 'xy\n')
    run_case('h_print_repeat', 'print 1; print 1; print 1;', '1\n1\n1\n')
    run_case('h_len_unicode', 'print len("😀"); print len("a\\tb");', '1\n3\n')
    run_case('h_negative_index', 'let a = [1, 2, 3]; print a[-1]; print a[9];', 'null\nnull\n')
    run_case('h_push_sequence', 'let a = [1]; push a, 2; push a, 3; push a, 4; print a;', '[1, 2, 3, 4]\n')
    run_case('h_empty_then', 'if true { } else { print "e"; } print "z";', 'z\n')
    run_case('h_nested_while', 'let i = 0; while i < 2 { print i; set i = i + 1; let j = 0; while j < 2 { print 9; set j = j + 1; } }', '0\n9\n9\n1\n9\n9\n')
    run_case('h_array3', 'print [1, 2, 3];', '[1, 2, 3]\n')
    run_case('h_null_eq', 'print null == null; print null != null; print null == 0;', 'true\nfalse\nfalse\n')
    run_case('h_fiber_three', 'fiber a { print 1; yield; print 4; } fiber b { print 2; yield; print 5; } fiber c { print 3; yield; print 6; } spawn a; spawn b; spawn c; yield;', '1\n2\n3\n4\n5\n6\n')
    run_case('h_fiber_join_wait', 'fiber w { print 1; yield; print 2; } let f = spawn w; join f; print 3;', '1\n2\n3\n')
    run_case('h_fiber_join_two_waiters', 'fiber w { yield; print 9; } fiber a { yield; print "a"; } fiber b { yield; print "b"; } spawn w; spawn a; spawn b; yield;', '9\na\nb\n')
    run_case('h_fiber_yield_noop', 'fiber a { yield; print 1; } spawn a; join 1; print 2;', '1\n2\n')
    exec_case('h_distinct_exec', 'print distinct([1, 2]);', 'true\n')
    serial_case('h_distinct_roundtrip', 'print distinct([1, 2]);', 'true\n')
    disasm_case('h_distinct_disasm', 'print distinct([1, 2]);', 'DISTINCT')
    serial_case('h_serial_full', 'print "a" + "b"; print true; print false; let i = 0; while i < 2 { print i; set i = i + 1; }', 'ab\ntrue\nfalse\n0\n1\n')
    serial_case('h_serial_fibers', 'fiber a { print 1; } spawn a; join 1; print 2;', '1\n2\n')
    snapshot_case('h_snapshot_roundtrip_run', 'let x = 5; print x + 1;', '6\n')
    snapshot_case('h_snapshot_globals', 'let a = [1, 2]; let s = "hi"; print len(a) + len(s);', '4\n')
    snapshot_case('h_snapshot_fibers', 'fiber a { print 1; yield; print 2; } spawn a; yield;', '1\n2\n')
    api_case('h_snapshot_badmagic', "restore(b'NOPE' + b'\\x00' * 32)", 'BAD_MAGIC', locals())
    api_case('h_snapshot_badversion', "restore(b'MV7' + b'\\x09' + b'\\x00' * 32)", 'BAD_VERSION', locals())
    api_case('h_snapshot_truncated', 'restore(good_bytes[:-3])', 'TRUNCATED', locals())
    api_case('h_snapshot_badchecksum', 'restore(good_bytes[:-1] + bytes([good_bytes[-1] ^ 0x01]))', 'BAD_CHECKSUM', locals())
    dup_bytes = bytearray(b'MV7' + bytes([1]))
    dup_bytes += struct.pack('<I', 1)
    dup_bytes += bytes([O.HALT])
    dup_bytes += struct.pack('<I', 0)
    dup_bytes += struct.pack('<I', 2)
    for fid in (7, 7):
        dup_bytes += struct.pack('<I', fid)
        dup_bytes += struct.pack('<I', 0)
        dup_bytes += struct.pack('<I', 0)
    dup_bytes += struct.pack('<I', 0)
    dup_bytes += struct.pack('<I', 0)
    dup_bytes += struct.pack('<I', fnv1a(bytes(dup_bytes)))
    bytes_with_duplicate_fiber_ids = bytes(dup_bytes)
    api_case('h_snapshot_duplicate_fiber', 'restore(bytes_with_duplicate_fiber_ids)', 'DUPLICATE_FIBER', locals())
    raw_case('h_load_uninit', [(O.LOAD, 0), (O.PRINT, None), (O.HALT, None)], 'null\n')
    raw_case('h_stack_ops', [(O.PUSH, 1), (O.DUP, None), (O.ADD, None), (O.PRINT, None), (O.PUSH, 3), (O.PUSH, 9), (O.SWAP, None), (O.PRINT, None), (O.PRINT, None), (O.HALT, None)], '2\n3\n9\n')

    perf('perf_print', 900.0, lambda: run('let i = 0; while i < 60000 { print i; set i = i + 1; }'))
    big_code = [(O.PUSH, i) for i in range(20000)] + [(O.HALT, None)]
    perf('perf_disasm', 700.0, lambda: disassemble(big_code))
    snap_code = [(O.PUSH, i % 7) for i in range(199)] + [(O.HALT, None)]
    snap_vm = VM(snap_code)
    for i in range(2000):
        snap_vm.vars['g%d' % i] = i
    perf('perf_snapshot', 700.0, lambda: restore(make_snapshot(snap_vm)))


if __name__ == "__main__":
    main()