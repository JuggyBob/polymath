#include <iostream>
#include <chrono>
#include <cstdlib>
#include <cstdint>
#include <new>
#include <utility>

#include "allocator.h"
#include "ring.h"
#include "scheduler.h"

static long g_news = 0;
static long g_dels = 0;

// Harness shims: deallocation is a no-op. Counters let a test observe balance
// without a heap fault ending the run.
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

static int t_add1(int x) { return x + 1; }
static int t_twice(int x) { return x * 2; }
static int t_neg(int x) { return -x; }

int main() {
    std::cout << std::unitbuf;

    // ==================== AlignedPool ====================
    {
        AlignedPool p(128, 8);
        bool ok = true;
        for (std::size_t i = 0; i < p.capacity(); ++i)
            ok = ok && (reinterpret_cast<std::uintptr_t>(p.slot(i)) % 64 == 0);
        CHECK(test_h_pool_all_slots_64_aligned, ok);
    }
    {
        AlignedPool p(sizeof(Payload), 8);
        bool ok = reinterpret_cast<std::uintptr_t>(p.slot(0)) % 64 == 0;
        CHECK(test_h_pool_first_slot_64_aligned, ok);
    }
    {
        AlignedPool p(sizeof(Payload), 8);
        unsigned char* s0 = p.slot(0);
        unsigned char* s1 = p.slot(1);
        CHECK(test_h_pool_slot_stride, s1 - s0 == static_cast<long>(sizeof(Payload)));
    }
    {
        AlignedPool p(sizeof(Payload), 5);
        bool ok = p.capacity() == 5 && p.used() == 0 && !p.full();
        unsigned char* a = p.claim();
        unsigned char* b = p.claim();
        ok = ok && a && b && p.used() == 2 && !p.full();
        CHECK(test_h_pool_capacity_used, ok);
    }
    {
        AlignedPool p(sizeof(Payload), 3);
        bool ok = p.claim() && p.claim() && p.claim() && p.used() == 3;
        unsigned char* over = p.claim();
        CHECK(test_h_pool_claim_at_capacity, ok && over == 0 && p.used() == 3 && p.full());
    }
    {
        PayloadStats::reset();
        AlignedPool p(sizeof(Payload), 4);
        Payload a(42);
        Payload* x = p.create(&a, false);
        CHECK(test_h_pool_create_copies_lvalue,
              x && x->value == 42 && !a.moved_from && PayloadStats::copies() >= 1);
    }
    {
        PayloadStats::reset();
        AlignedPool p(sizeof(Payload), 4);
        Payload a(43);
        Payload* x = p.create(&a, true);
        CHECK(test_h_pool_create_moves_rvalue,
              x && x->value == 43 && a.moved_from && PayloadStats::moves() >= 1);
    }
    {
        AlignedPool p(sizeof(Payload), 4);
        Payload* x = p.create(0, false);
        int d0 = PayloadStats::destructions();
        std::size_t u0 = p.used();
        p.release(x);
        CHECK(test_h_pool_release_destructor,
              PayloadStats::destructions() == d0 + 1 && p.used() == u0 - 1);
    }
    {
        PayloadStats::reset();
        AlignedPool p(sizeof(Payload), 6);
        for (int i = 0; i < 4; ++i) p.create(0, false);
        int d0 = PayloadStats::destructions();
        p.clear();
        CHECK(test_h_pool_clear_all_destructors,
              PayloadStats::destructions() == d0 + 4 && p.used() == 0);
    }
    {
        AlignedPool a(sizeof(Payload), 4);
        Payload seed(9);
        a.create(&seed, false);
        AlignedPool b(std::move(a));
        bool ok = b.capacity() == 4 && b.used() == 1;
        ok = ok && a.capacity() == 0 && a.used() == 0 && a.slot(0) == 0;
        Payload* stored = reinterpret_cast<Payload*>(b.slot(0));
        ok = ok && stored->value == 9;
        CHECK(test_h_pool_move_ctor_empties_source, ok);
    }
    {
        long n0 = g_news, d0 = g_dels;
        {
            AlignedPool p(sizeof(Payload), 7);
            p.create(0, false);
        }
        CHECK(test_h_pool_allocation_balance, g_news - n0 == g_dels - d0);
    }

    // ==================== RingQueue ====================
    {
        RingQueue a(10);
        RingQueue b(16);
        RingQueue c(17);
        RingQueue z(0);
        CHECK(test_h_ring_capacity_round_up,
              a.capacity() == 16 && b.capacity() == 16 &&
              c.capacity() == 32 && z.capacity() == 1);
    }
    {
        RingQueue q(8);
        CHECK(test_h_ring_empty_initial, q.empty() && q.size() == 0 && !q.full());
    }
    {
        RingQueue q(8);
        for (int i = 1; i <= 4; ++i) q.push_int(i);
        CHECK(test_h_ring_size_after_push, q.size() == 4 && !q.empty());
    }
    {
        RingQueue q(4);
        q.push_int(1); q.push_int(2); q.push_int(3); q.push_int(4);
        CHECK(test_h_ring_full_at_capacity, q.full() && q.size() == 4);
    }
    {
        RingQueue q(4);
        q.push_int(1); q.push_int(2); q.push_int(3);
        CHECK(test_h_ring_not_full_below_capacity, !q.full() && q.size() == 3);
    }
    {
        RingQueue q(4);
        q.push_int(1); q.push_int(2); q.push_int(3); q.push_int(4);
        bool rejected = !q.push_int(99);
        bool fifo = true;
        for (int i = 1; i <= 4; ++i) {
            int v = -1;
            fifo = fifo && q.pop_int(v) && v == i;
        }
        CHECK(test_h_ring_push_rejected_when_full, rejected && fifo && q.empty());
    }
    {
        RingQueue q(4);
        q.push_int(10); q.push_int(20); q.push_int(30); q.push_int(40);
        bool rejected = !q.push_int(50);
        std::size_t s = q.size();
        bool empty_after = true;
        for (int i = 0; i < 4; ++i) { int v = -1; empty_after = empty_after && q.pop_int(v); }
        CHECK(test_h_ring_push_full_preserves_data, rejected && s == 4 && empty_after && q.empty());
    }
    {
        RingQueue q(4);
        int v = 777;
        CHECK(test_h_ring_pop_empty_int, !q.pop_int(v) && v == 777);
    }
    {
        RingQueue q(4);
        Payload out(55);
        bool r = q.pop(out);
        CHECK(test_h_ring_pop_empty_payload, !r && out.value == 55 && !out.moved_from);
    }
    {
        RingQueue q(4);
        q.push_int(1); q.push_int(2); q.push_int(3); q.push_int(4);
        int a = 0, b = 0;
        q.pop_int(a); q.pop_int(b);
        q.push_int(5); q.push_int(6);
        bool ok = q.size() == 4 && q.full();
        int seq[4] = {0, 0, 0, 0};
        bool popped = true;
        for (int i = 0; i < 4; ++i) popped = popped && q.pop_int(seq[i]);
        ok = ok && popped && seq[0] == 3 && seq[1] == 4 && seq[2] == 5 && seq[3] == 6;
        ok = ok && a == 1 && b == 2;
        CHECK(test_h_ring_fifo_wrap, ok);
    }
    {
        PayloadStats::reset();
        RingQueue q(4);
        Payload a(5);
        bool pushed = q.push(a);
        Payload out(0);
        q.pop(out);
        CHECK(test_h_ring_lvalue_push_copies,
              pushed && !a.moved_from && PayloadStats::copies() >= 1 && out.value == 5);
    }
    {
        PayloadStats::reset();
        RingQueue q(4);
        Payload a(6);
        bool pushed = q.push(std::move(a));
        Payload out(0);
        q.pop(out);
        CHECK(test_h_ring_rvalue_push_moves,
              pushed && a.moved_from && PayloadStats::moves() >= 1 && out.value == 6);
    }
    {
        RingQueue q(4);
        bool ok = true;
        for (int i = 0; i < 200; ++i) {
            q.push_int(i);
            ok = ok && q.size() == 1;
            int v = -1;
            ok = ok && q.pop_int(v) && v == i && q.size() == 0;
        }
        CHECK(test_h_ring_interleaved_size, ok);
    }
    {
        const std::size_t CAP = 4096;
        RingQueue q(CAP);
        for (std::size_t i = 0; i < CAP; ++i) q.push_int(static_cast<int>(i));
        std::chrono::steady_clock::time_point t0 = std::chrono::steady_clock::now();
        bool size_ok = true;
        for (int i = 0; i < 1000000; ++i) {
            size_ok = size_ok && (q.size() == CAP);
            int v = -1;
            q.pop_int(v);
            q.push_int(v);
        }
        std::chrono::steady_clock::time_point t1 = std::chrono::steady_clock::now();
        double secs = std::chrono::duration<double>(t1 - t0).count();
        CHECK(test_h_ring_perf_1m_ops, size_ok && secs < 2.0);
    }
    {
        RingQueue q(8);
        bool ok = true;
        for (int i = 0; i < 6; ++i) ok = ok && q.push_int(i);
        for (int i = 0; i < 6; ++i) { int v = -1; ok = ok && q.pop_int(v) && v == i; }
        CHECK(test_h_ring_int_fifo_basic, ok && q.empty());
    }

    // ==================== Scheduler ====================
    {
        Scheduler s(3);
        bool ok = s.submit(t_add1, 1) && s.submit(t_twice, 2) && s.submit(t_neg, 3);
        bool over = !s.submit(t_add1, 99);
        CHECK(test_h_sched_submit_capacity, ok && over);
        s.run_all();
        CHECK(test_h_sched_submit_over_capacity_no_change,
              s.result(0) == 2 && s.result(1) == 4 && s.result(2) == -3);
    }
    {
        Scheduler s(3);
        s.submit(t_add1, 1); s.submit(t_twice, 2); s.submit(t_neg, 3);
        CHECK(test_h_sched_run_all_once, s.run_all() == 3);
    }
    {
        Scheduler s(2);
        s.submit(t_add1, 1); s.submit(t_add1, 2);
        std::size_t first = s.run_all();
        std::size_t second = s.run_all();
        CHECK(test_h_sched_run_all_twice, first == 2 && second == 0);
    }
    {
        Scheduler s(2);
        s.submit(t_add1, 1); s.submit(t_add1, 2);
        bool ok = s.pending() == 2 && s.completed() == 0;
        s.run_all();
        CHECK(test_h_sched_pending_and_completed, ok && s.pending() == 0 && s.completed() == 2);
    }
    {
        Scheduler s(3);
        s.submit(t_add1, 10); s.submit(t_twice, 5); s.submit(t_neg, -7);
        s.run_all();
        CHECK(test_h_sched_results_in_order,
              s.result(0) == 11 && s.result(1) == 10 && s.result(2) == 7);
    }
    {
        Scheduler s(2);
        s.submit(t_add1, 1); s.submit(t_add1, 2);
        s.run_all();
        CHECK(test_h_sched_done_flags, s.done(0) && s.done(1));
    }
    {
        Scheduler s(2);
        s.submit(t_add1, 1); s.submit(t_add1, 2);
        s.run_all();
        s.reset();
        bool ok = s.pending() == 0 && s.completed() == 0 && !s.done(0);
        s.submit(t_twice, 4);
        ok = ok && s.run_all() == 1 && s.result(0) == 8;
        CHECK(test_h_sched_reset_reusable, ok);
    }
    {
        CHECK(test_h_sched_clamp_in_range, Scheduler::clamp_int<int>(5, 0, 10) == 5);
        CHECK(test_h_sched_clamp_low, Scheduler::clamp_int<int>(-3, 0, 10) == 0);
        CHECK(test_h_sched_clamp_high, Scheduler::clamp_int<long>(50, 0, 10) == 10);
        CHECK(test_h_sched_clamp_unsigned_large,
              Scheduler::clamp_int<unsigned>(4000000000u, 0, 100) == 100);
        CHECK(test_h_sched_clamp_unsigned_negative_lo,
              Scheduler::clamp_int<unsigned>(7u, -5, 10) == 7);
    }

    // ==================== Prime helpers ====================
    {
        bool ok = !Scheduler::is_prime_naive(0) && !Scheduler::is_prime_naive(1);
        ok = ok && !Scheduler::is_prime_naive(-7) && Scheduler::is_prime_naive(2);
        ok = ok && Scheduler::is_prime_naive(97) && !Scheduler::is_prime_naive(4);
        CHECK(test_h_prime_naive_edges, ok);
    }
    CHECK(test_h_prime_opt_zero, !Scheduler::is_prime_optimized(0));
    CHECK(test_h_prime_opt_one, !Scheduler::is_prime_optimized(1));
    CHECK(test_h_prime_opt_negative, !Scheduler::is_prime_optimized(-7));
    CHECK(test_h_prime_opt_two, Scheduler::is_prime_optimized(2));
    {
        bool ok = !Scheduler::is_prime_optimized(4) && !Scheduler::is_prime_optimized(9);
        ok = ok && !Scheduler::is_prime_optimized(25) && Scheduler::is_prime_optimized(3);
        ok = ok && Scheduler::is_prime_optimized(5) && Scheduler::is_prime_optimized(97);
        CHECK(test_h_prime_opt_small_values, ok);
    }
    CHECK(test_h_prime_opt_medium_prime, Scheduler::is_prime_optimized(1000003));
    CHECK(test_h_prime_opt_int_max_prime, Scheduler::is_prime_optimized(2147483647));
    CHECK(test_h_prime_opt_large_even, !Scheduler::is_prime_optimized(2147483646));
    {
        std::chrono::steady_clock::time_point t0 = std::chrono::steady_clock::now();
        bool p1 = Scheduler::is_prime_optimized(2147483647);
        bool p2 = Scheduler::is_prime_optimized(2147483647);
        std::chrono::steady_clock::time_point t1 = std::chrono::steady_clock::now();
        double secs = std::chrono::duration<double>(t1 - t0).count();
        CHECK(test_h_prime_opt_perf, p1 && p2 && secs < 2.0);
    }
    return 0;
}
