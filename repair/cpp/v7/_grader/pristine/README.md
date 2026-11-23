# C++ repair v7 — task

This VM is broken in several ways. Hidden acceptance tests define correctness.
Run the examples to see the intended behaviour.

Failures may be masked by earlier faults. After a fix, re-run everything: new
failures are expected and are part of the task.

Do not change the example files. The visible tests and examples are the only
specification.

## Compile and run

Build the visible suite from this directory:

```
g++ -std=c++17 -O2 -Iinclude src/*.cpp tests/test_visible.cpp -o test_visible
test_visible
```

With MSVC, from a developer prompt:

```
cl /EHsc /nologo /O2 /Iinclude src\*.cpp tests\test_visible.cpp
test_visible.exe
```

The suite prints `TEST <example> PASS` or `TEST <example> FAIL` once for each
example, then three `PERF` lines for each of the three workloads.

To run one example, compile it in place of the test file and compare its output
with the matching `.expected` file:

```
g++ -std=c++17 -O2 -Iinclude src/*.cpp examples/prog01_arith.cpp -o prog01_arith
prog01_arith
```

Each `examples/*.expected` file is the exact stdout for its program or driver.
