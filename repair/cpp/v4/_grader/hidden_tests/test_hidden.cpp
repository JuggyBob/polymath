#include <iostream>
#include <chrono>
#include <cstdlib>
#include <new>
#include <stdexcept>
#include <string>

#include "matrix.h"
#include "algorithms.h"
#include "registry.h"

static long g_news = 0;
static long g_dels = 0;

// Harness shims: deallocation is a no-op. The counters let a test observe
// allocation balance without a heap fault ending the run.
void* operator new(std::size_t n) {
    ++g_news;
    void* p = std::malloc(n ? n : 1);
    if (!p) throw std::bad_alloc();
    return p;
}
void operator delete(void*) noexcept { ++g_dels; }
void operator delete(void*, std::size_t) noexcept { ++g_dels; }
void* operator new[](std::size_t n) {
    ++g_news;
    void* p = std::malloc(n ? n : 1);
    if (!p) throw std::bad_alloc();
    return p;
}
void operator delete[](void*) noexcept { ++g_dels; }
void operator delete[](void*, std::size_t) noexcept { ++g_dels; }

#define CHECK(name, cond) std::cout << "TEST " << #name << " " << ((cond) ? "PASS" : "FAIL") << "\n"

static double f1(double x) { return x * 1.0; }
static double f2(double x) { return x * 2.0; }
static double f3(double x) { return x * 3.0; }
static double f4(double x) { return x * 4.0; }
static double f5(double x) { return x * 5.0; }
static double f6(double x) { return x * 6.0; }
static double f7(double x) { return x * 7.0; }
static double f8(double x) { return x * 8.0; }
static double f9(double x) { return x * 9.0; }
static double f10(double x) { return x * 10.0; }

int main() {
    std::cout << std::unitbuf;

    // ---- Matrix ownership and copy semantics ----
    Matrix* src = new Matrix(2, 2);
    src->fill(7);
    Matrix* cpy = new Matrix(*src);
    cpy->at(0, 0) = 99;
    CHECK(test_h_copy_independent, src->at(0, 0) == 7 && cpy->at(1, 1) == 7);

    Matrix as(2, 2), at(2, 2);
    as.fill(1);
    at.fill(5);
    as = at;
    as.at(0, 0) = 77;
    CHECK(test_h_assign_independent, at.at(0, 0) == 5);

    long n0 = g_news, d0 = g_dels;
    {
        Matrix z(3, 4);
        z.fill(1);
    }
    CHECK(test_h_destructor_balance, (g_news - n0) == (g_dels - d0));

    // ---- multiply: index order and cleanup on exceptional path ----
    Matrix A(2, 2), B(2, 2);
    A.at(0, 0) = 1; A.at(0, 1) = 2; A.at(1, 0) = 3; A.at(1, 1) = 4;
    B.at(0, 0) = 5; B.at(0, 1) = 6; B.at(1, 0) = 7; B.at(1, 1) = 8;
    Matrix C = A.multiply(B);
    CHECK(test_h_multiply_values, C.at(0, 0) == 19 && C.at(0, 1) == 22 && C.at(1, 0) == 43 && C.at(1, 1) == 50);

    Matrix lhs(2, 3), rhs(2, 2);
    lhs.fill(1);
    rhs.fill(1);
    long n1 = g_news, d1 = g_dels;
    bool threw = false;
    try { lhs.multiply(rhs); } catch (const std::invalid_argument&) { threw = true; }
    CHECK(test_h_exception_cleanup, threw && (g_news - n1) == (g_dels - d1));

    // ---- transpose must not disturb its source ----
    Matrix tm(2, 2);
    tm.at(0, 0) = 1; tm.at(0, 1) = 2; tm.at(1, 0) = 3; tm.at(1, 1) = 4;
    Matrix tt = tm.transpose();
    CHECK(test_h_transpose_source, tm.at(0, 1) == 2 && tm.at(1, 0) == 3 && tt.at(0, 1) == 3 && tt.at(1, 0) == 2);

    Matrix nm(2, 3);
    nm.at(0, 0) = 1; nm.at(0, 1) = 2; nm.at(0, 2) = 3;
    nm.at(1, 0) = 4; nm.at(1, 1) = 5; nm.at(1, 2) = 6;
    Matrix nt = nm.transpose();
    CHECK(test_h_transpose_nonsquare, nt.rows() == 3 && nt.cols() == 2 && nt.at(2, 1) == 6 && nt.at(0, 1) == 4);

    // ---- reductions ----
    Matrix rm(2, 2);
    rm.at(0, 0) = 1; rm.at(0, 1) = 2; rm.at(1, 0) = 10; rm.at(1, 1) = 20;
    CHECK(test_h_reduce_all_rows, reduce_all(rm, sum_row) == 33);

    double precise[] = {16777216.0, 1.0};
    CHECK(test_h_sum_row_precision, sum_row(precise, 2) == 16777217.0);
    double negs[] = {-5, 2, -1};
    CHECK(test_h_sum_row_negative, sum_row(negs, 3) == -4);
    CHECK(test_h_max_row_value, max_row(negs, 3) == 2);
    CHECK(test_h_min_row_value, min_row(negs, 3) == -5);
    double prod[] = {2, 3, 4};
    CHECK(test_h_product_row_value, product_row(prod, 3) == 24);

    Matrix fm(1, 3);
    fm.at(0, 0) = 10; fm.at(0, 1) = 3; fm.at(0, 2) = 2;
    CHECK(test_h_fold_sub_order, fold_all(fm, sub_op, 100) == 85);
    CHECK(test_h_fold_add_order, fold_all(fm, add_op, 100) == 115);

    // ---- format is exact, even though it looks incidental ----
    Matrix fmt(2, 3);
    fmt.at(0, 0) = 1; fmt.at(0, 1) = 2.5; fmt.at(0, 2) = -3;
    fmt.at(1, 0) = 0; fmt.at(1, 1) = 7; fmt.at(1, 2) = 8;
    std::string fs = format_matrix(fmt);
    CHECK(test_h_format_exact, fs == "[1.00, 2.50, -3.00]\n[0.00, 7.00, 8.00]");
    Matrix empty(0, 0);
    CHECK(test_h_format_empty, format_matrix(empty) == "<empty>");

    // ---- traversal: correct and fast on a 2000x2000 row-major buffer ----
    double small[6] = {1, 2, 3, 4, 5, 6};
    CHECK(test_h_traverse_small, traverse_sum(small, 2, 3) == 21);

    const std::size_t N = 2000;
    double* big = new double[N * N];
    for (std::size_t i = 0; i < N; ++i) {
        for (std::size_t j = 0; j < N; ++j) big[i * N + j] = 0.0;
        big[i * N + i] = 1.0;
    }
    std::chrono::steady_clock::time_point t0 = std::chrono::steady_clock::now();
    double bigsum = traverse_sum(big, N, N);
    std::chrono::steady_clock::time_point t1 = std::chrono::steady_clock::now();
    double secs = std::chrono::duration<double>(t1 - t0).count();
    CHECK(test_h_traverse_perf, bigsum == 2000.0 && secs < 2.0);

    // ---- templates must not disturb their input ----
    int ia[] = {4, 5, 6};
    int isum = sum_range(ia, ia + 3);
    CHECK(test_h_sum_range_preserves_input, isum == 15 && ia[0] == 4 && ia[1] == 5 && ia[2] == 6);
    const double ca[] = {1.25, 2.75};
    double csum = sum_range(ca, ca + 2);
    CHECK(test_h_sum_range_const_source, csum == 4.0 && ca[0] == 1.25 && ca[1] == 2.75);
    double dm[] = {8.0, 3.0, 5.0};
    CHECK(test_h_max_range_double, max_range(dm, dm + 3) == 8.0);
    double th[] = {1.0, 4.0, 2.0};
    CHECK(test_h_count_above_double, count_above_range(th, th + 3, 2.0) == 1);

    // ---- sorted order and tie-breaking ----
    double sv[] = {5, 3, 5, 1};
    std::size_t so[4];
    sorted_indices(sv, 4, so);
    CHECK(test_h_sorted_tie_order, so[0] == 3 && so[1] == 1 && so[2] == 0 && so[3] == 2);
    double sv2[] = {9, 1, 7};
    std::size_t so2[3];
    sorted_indices(sv2, 3, so2);
    CHECK(test_h_sorted_distinct_values, so2[0] == 1 && so2[1] == 2 && so2[2] == 0);

    // ---- small integer contracts ----
    CHECK(test_h_clamp_negative, clamp_count(-3, 5) == 0);
    CHECK(test_h_clamp_over_available, clamp_count(9, 5) == 5);
    int ovf[] = {2000000000, 2000000000};
    CHECK(test_h_total_overflow, total_of(ovf, 2) == 4000000000LL);
    int negtot[] = {100, -250, 50};
    CHECK(test_h_total_negative, total_of(negtot, 3) == -100);

    // ---- loop invariants for empty and non-empty matrices ----
    Matrix zero(0, 3);
    CHECK(test_h_same_sum_empty, all_rows_same_sum(zero));
    Matrix mix(2, 2);
    mix.at(0, 0) = 1; mix.at(0, 1) = 2; mix.at(1, 0) = 1; mix.at(1, 1) = 1;
    CHECK(test_h_same_sum_mixed, !all_rows_same_sum(mix));

    // ---- the mutable-static factor ----
    CHECK(test_h_factor_first_call, apply_factor(3) == 6);
    CHECK(test_h_factor_repeat_call, apply_factor(2) == 4);

    // ---- the quadratic-looking duplicate scan is still correct ----
    Matrix dr(2, 3);
    dr.at(0, 0) = 1; dr.at(0, 1) = 2; dr.at(0, 2) = 3;
    dr.at(1, 0) = 1; dr.at(1, 1) = 2; dr.at(1, 2) = 3;
    CHECK(test_h_dup_rows_present, has_duplicate_row(dr));
    Matrix dn(2, 2);
    dn.at(0, 0) = 1; dn.at(0, 1) = 2; dn.at(1, 0) = 2; dn.at(1, 1) = 1;
    CHECK(test_h_dup_rows_absent, !has_duplicate_row(dn));

    // ---- registry: capacity, duplicate names, cache keyed by name+argument ----
    Registry reg;
    reg.add("n1", f1);
    reg.add("n2", f2);
    reg.add("n3", f3);
    reg.add("n4", f4);
    reg.add("n5", f5);
    reg.add("n6", f6);
    reg.add("n7", f7);
    reg.add("n8", f8);
    reg.add("n9", f9);
    CHECK(test_h_registry_capacity, reg.call("n1", 2) == 2 && reg.call("n2", 2) == 4 && reg.call("n8", 2) == 16 && !reg.has("n9"));

    Registry dup;
    dup.add("a", f2);
    dup.add("b", f3);
    dup.add("a", f5);
    CHECK(test_h_registry_duplicate, dup.call("a", 2) == 10 && dup.call("b", 2) == 6 && dup.size() == 2);

    Registry ch;
    ch.add("dbl", f2);
    ch.add("trp", f3);
    double cv1 = ch.cached("dbl", 2);
    double cv2 = ch.cached("trp", 3);
    CHECK(test_h_cache_distinct_names, cv1 == 4 && cv2 == 9);
    Registry cr;
    cr.add("dbl", f2);
    double av1 = cr.cached("dbl", 2);
    double av2 = cr.cached("dbl", 5);
    CHECK(test_h_cache_distinct_args, av1 == 4 && av2 == 10);
    cr.clear_cache();
    CHECK(test_h_cache_clear, cr.cached("dbl", 5) == 10);
    CHECK(test_h_registry_missing, !cr.has("nope") && cr.call("nope", 1) == 0);
    return 0;
}
