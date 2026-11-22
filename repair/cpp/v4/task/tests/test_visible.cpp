#include <iostream>
#include <cstdlib>
#include <new>
#include <stdexcept>
#include <string>

#include "matrix.h"
#include "algorithms.h"
#include "registry.h"

// Test-harness allocation shims: deallocation is deliberately a no-op so a
// program fault cannot take down the whole test binary mid-run.
void* operator new(std::size_t n) {
    void* p = std::malloc(n ? n : 1);
    if (!p) throw std::bad_alloc();
    return p;
}
void operator delete(void*) noexcept {}
void operator delete(void*, std::size_t) noexcept {}
void* operator new[](std::size_t n) {
    void* p = std::malloc(n ? n : 1);
    if (!p) throw std::bad_alloc();
    return p;
}
void operator delete[](void*) noexcept {}
void operator delete[](void*, std::size_t) noexcept {}

#define CHECK(name, cond) std::cout << "TEST " << #name << " " << ((cond) ? "PASS" : "FAIL") << "\n"

static double twice(double x) { return x * 2.0; }
static double thrice(double x) { return x * 3.0; }

int main() {
    std::cout << std::unitbuf;

    Matrix m(2, 2);
    CHECK(matrix_dims, m.rows() == 2 && m.cols() == 2);
    m.at(0, 0) = 1; m.at(0, 1) = 2; m.at(1, 0) = 3; m.at(1, 1) = 4;
    CHECK(matrix_at, m.at(0, 1) == 2 && m.at(1, 0) == 3);

    Matrix f(2, 3);
    f.fill(2.5);
    CHECK(matrix_fill, f.at(0, 0) == 2.5 && f.at(1, 2) == 2.5);

    Matrix a(2, 2), b(2, 2);
    a.at(0, 0) = 1; a.at(0, 1) = 2; a.at(1, 0) = 3; a.at(1, 1) = 4;
    b.at(0, 0) = 5; b.at(0, 1) = 6; b.at(1, 0) = 7; b.at(1, 1) = 8;
    Matrix s = a.add(b);
    CHECK(matrix_add, s.at(0, 0) == 6 && s.at(1, 1) == 12);

    Matrix ident(2, 2);
    ident.at(0, 0) = 1; ident.at(0, 1) = 0; ident.at(1, 0) = 0; ident.at(1, 1) = 1;
    Matrix mi = a.multiply(ident);
    CHECK(matrix_multiply_identity, mi.at(0, 0) == 1 && mi.at(0, 1) == 2 && mi.at(1, 0) == 3 && mi.at(1, 1) == 4);

    Matrix sym(2, 2);
    sym.at(0, 0) = 1; sym.at(0, 1) = 2; sym.at(1, 0) = 2; sym.at(1, 1) = 3;
    Matrix st = sym.transpose();
    CHECK(matrix_transpose_symmetric, st.at(0, 1) == 2 && st.at(1, 0) == 2);

    Matrix rr(2, 2);
    rr.at(0, 0) = 1; rr.at(0, 1) = 2; rr.at(1, 0) = 0; rr.at(1, 1) = 0;
    CHECK(reduce_sum_first_row, reduce_all(rr, sum_row) == 3);

    double row[] = {2, 4, 6};
    CHECK(sum_row_basic, sum_row(row, 3) == 12);
    CHECK(max_row_basic, max_row(row, 3) == 6);
    CHECK(min_row_basic, min_row(row, 3) == 2);
    CHECK(product_row_basic, product_row(row, 3) == 48);

    Matrix foldm(2, 2);
    foldm.at(0, 0) = 1; foldm.at(0, 1) = 2; foldm.at(1, 0) = 3; foldm.at(1, 1) = 4;
    CHECK(fold_add, fold_all(foldm, add_op, 0) == 10);
    CHECK(fold_mul, fold_all(foldm, mul_op, 1) == 24);

    double buf[6] = {1, 2, 3, 4, 5, 6};
    CHECK(traverse_small, traverse_sum(buf, 2, 3) == 21);

    int ia[] = {3, 1, 4, 1, 5};
    CHECK(sum_range_int, sum_range(ia, ia + 5) == 14);
    double da[] = {1.5, 2.5};
    CHECK(sum_range_double, sum_range(da, da + 2) == 4.0);
    int ib[] = {3, 9, 2};
    CHECK(max_range_int, max_range(ib, ib + 3) == 9);
    CHECK(count_above_range_int, count_above_range(ib, ib + 3, 3) == 1);

    double vals[] = {5, 3, 9, 1};
    std::size_t idx[4];
    sorted_indices(vals, 4, idx);
    CHECK(sorted_distinct, idx[0] == 3 && idx[1] == 1 && idx[2] == 0 && idx[3] == 2);

    CHECK(clamp_within, clamp_count(2, 5) == 2);
    CHECK(clamp_over, clamp_count(9, 5) == 5);

    int big[] = {100, 200, 300};
    CHECK(total_small, total_of(big, 3) == 600);

    Matrix same(2, 2);
    same.at(0, 0) = 1; same.at(0, 1) = 2; same.at(1, 0) = 2; same.at(1, 1) = 1;
    CHECK(same_sum_rows, all_rows_same_sum(same));
    CHECK(factor_once, apply_factor(3) == 6);

    Matrix dup(2, 2);
    dup.at(0, 0) = 1; dup.at(0, 1) = 2; dup.at(1, 0) = 1; dup.at(1, 1) = 2;
    CHECK(dup_rows_present, has_duplicate_row(dup));

    Registry reg;
    reg.add("double", twice);
    reg.add("triple", thrice);
    CHECK(registry_has, reg.has("double") && reg.has("triple"));
    CHECK(registry_call, reg.call("double", 4) == 8 && reg.call("triple", 4) == 12);
    CHECK(registry_cached_same, reg.cached("double", 5) == 10 && reg.cached("double", 5) == 10);
    CHECK(registry_size, reg.size() == 2);
    return 0;
}
