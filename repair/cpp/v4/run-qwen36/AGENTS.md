# Repair task C++ v4 — a small numeric library

Three headers, three translation units. Every public declaration is in
`include/`. Every rule below is part of the contract; the checked behaviour is a
superset of the visible tests.

```
cl /EHsc /nologo /Od /Iinclude src\*.cpp tests\test_visible.cpp
test_visible.exe
```

You may edit only `src/*.cpp`. Keep `include/*.h` and `tests/*` byte-for-byte.
Standard C++ only. Do not add third-party libraries. Keep changes local.

---

## 1. `Matrix` (`include/matrix.h`, `src/matrix.cpp`)

Storage is row-major: element `(r,c)` is the `c`-th double of row `r`.

- **Construction.** `Matrix(rows, cols)` starts zero-filled. `rows()` and
  `cols()` report the dimensions. `at(r,c)` is assignable on a non-const matrix
  and readable on a const one. `row(r)` returns a pointer to the start of row
  `r`. `fill(v)` writes `v` to every element. A `0×k` matrix has zero rows; a
  `k×0` matrix has `k` empty rows.
- **Lifetime.** Every allocation made by a `Matrix` is released exactly once
  when it is destroyed. A `Matrix` controls its own storage: two `Matrix`
  objects never share a row or a row-pointer array. Worked example:

  ```
  Matrix* p = new Matrix(2,2);   // p fills with 9
  Matrix q(*p);                  // copy
  q.at(0,0) = 99;
  p->at(0,0) must still be 9
  ```

  Assignment follows the same rule: after `x = y`, writing through `x` does not
  change `y`.

- **`add`** requires equal shapes and is elementwise.
- **`multiply`** requires `lhs.cols() == rhs.rows()`. The entry `(i,j)` is the
  sum over `k` of `lhs(i,k) * rhs(k,j)`. Worked example:

  ```
  [1 2]   [5 6]   [1*5+2*7  1*6+2*8]   [19 22]
  [3 4] * [7 8] = [3*5+4*7  3*6+4*8] = [43 50]
  ```

  If the shapes are incompatible the call throws
  `std::invalid_argument`, and the call must not leave any allocation behind.

- **`transpose`** returns a new matrix of shape `cols()×rows()` with
  `result(j,i) = source(i,j)`. The source is not modified. Worked example:

  ```
  [1 2 3]        [1 4]
  [4 5 6]  ->    [2 5]
                [3 6]
  ```

  For a square input the same rule applies; the source stays as it was.

- **Reductions.** `sum_row`, `max_row`, `min_row`, `product_row` consume a
  contiguous row of `n` doubles. `sum_row` adds the values exactly as a `double`
  would; large and small values together must keep the small one (e.g.
  `16777216 + 1 == 16777217`). `product_row` starts at `1`.

  `reduce_all(m, op)` applies `op` to each row of `m` and adds the `n` results.
  It visits **all** rows: a `2×2` matrix whose rows sum to `3` and `30` gives
  `33`. A matrix with no rows gives `0`.

  `fold_all(m, op, init)` visits elements row by row and calls the callback as
  `op(accumulator, element)`. Worked examples:

  ```
  fold_all([[10,3,2]], sub_op, 100) = ((100-10)-3)-2 = 85
  fold_all([[10,3,2]], add_op, 100) = 115
  ```

  Because both callback parameters have the same type, reversing them still
  compiles; the examples above fix the intended order.

- **`has_duplicate_row`** scans every pair of rows and reports whether any two
  rows are identical. This pair scan is O(rows²·cols) but it is correct. Leave
  it alone.

- **`format_matrix`** is a presentation helper and is **not** part of the
  numeric core. You may simplify it if helpful; tests do not depend on its
  exact bytes.

---

## 2. `Algorithms` (`include/algorithms.h`, `src/algorithms.cpp`)

- `sum_range(first, last)`, `max_range(first, last)` and
  `count_above_range(first, last, threshold)` operate on half-open pointer
  ranges `[first, last)`. They are templates over `T`; explicit instantiations
  exist for `int` and `double`. They accept `const T*` just as readily as `T*`.
  A range algorithm reads its input and leaves it **unchanged**: after
  `sum_range(v, v+3)` the three values in `v` are still the three values that
  were there before.

- `traverse_sum(data, rows, cols)` receives `rows*cols` doubles laid out row by
  row. It returns their total. It must walk the buffer in storage order (the
  contiguous order) rather than jumping down columns. Worked example for a
  `2×3` buffer `[1 2 3 | 4 5 6]`: the visitation order is
  `1,2,3,4,5,6`, not `1,4,2,5,3,6`. It must be a **single linear pass** in
  storage order: no column-wise walking and no rescanning of a row to locate
  an entry. One traversal of a `2000×2000` buffer must finish within
  **2 seconds** on this machine. A column-wise walk or a rescan violates the
  performance contract.

- `sorted_indices(values, n, out)` writes `0..n-1` into `out` sorted by the
  corresponding value ascending, with **equal values ordered by smaller index
  first**. Worked example:

  ```
  values: index0=5  index1=3  index2=5  index3=1
  out:    3, 1, 0, 2
  ```

  (the two `5`s come out as `0` then `2`, because `0 < 2`).

- `clamp_count(requested, available)` returns `requested` when it is between
  `0` and `available`, `0` when it is below `0`, and `available` when it is
  above. Worked examples:

  ```
  clamp_count(2, 5) == 2
  clamp_count(9, 5) == 5
  clamp_count(-3, 5) == 0
  ```

  `requested` is `int` and `available` is `std::size_t`; remember that mixing
  signed and unsigned operands converts the signed one.

- `total_of(values, n)` sums `n` `int`s and returns a `long long`. It must not
  lose the result to narrowing: `2000000000 + 2000000000 == 4000000000`.

- `all_rows_same_sum(m)` reports whether every row of `m` has the same sum.
  A matrix with zero rows satisfies this vacuously, so
  `all_rows_same_sum(Matrix(0,3)) == true`.

- `apply_factor(x)` returns `x * 2`. Each call is independent:
  `apply_factor(3) == 6` and then `apply_factor(3) == 6` again.

---

## 3. `Registry` (`include/registry.h`, `src/registry.cpp`)

`add(name, cb)` registers a function pointer under a name; `has`, `call` and
`size` observe the table. `call` returns `0.0` for an unknown name.

- The table holds up to eight named callbacks. Adding a ninth name when it is
  full must not evict or alter any callback already registered: after adding
  `n1`..`n8` and then `n9`, the names `n1`, `n2` and `n8` still call their
  original functions and `n9` is not registered.
- Re-registering an existing name **replaces that callback** and does not
  increase `size()`. Worked example:

  ```
  add("a", times2); add("b", times3); add("a", times5);
  call("a",2) == 10, call("b",2) == 6, size() == 2
  ```

- `cached(name, x)` returns the same value as `call(name, x)`. It may reuse a
  previous result only when that result is for the **same name and the same
  argument**. Worked examples:

  ```
  add("dbl", times2); add("trp", times3);
  cached("dbl",2) -> 4
  cached("trp",3) -> 9      // not 4: the name changed
  cached("dbl",5) -> 10     // not 4: the argument changed
  ```

  `clear_cache()` discards any remembered result. The number of registered
  callbacks is not a cache key.

---

## Notes

- The visible tests all pass on the starting code. They exercise well-formed,
  non-degenerate cases; they are not a complete specification. Read the worked
  examples above rather than inferring rules from what the visible tests happen
  to check.
- One quadratic-looking helper is correct and should not be rewritten.
- `format_matrix` is incidental; do not spend effort on it.
