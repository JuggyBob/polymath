#include <iostream>
#include <cstdlib>
#include <new>
#include <utility>

#include "allocator.h"
#include "ring.h"
#include "scheduler.h"

// Test-harness allocation shims: deallocation is deliberately a no-op so a
// fault cannot take down the whole test binary mid-run.
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

static int twice(int x) { return x * 2; }
static int plus5(int x) { return x + 5; }

int main() {
    std::cout << std::unitbuf;

    // ---- the payload's own copy/move rules ----
    Payload p(11);
    CHECK(payload_copy, Payload(p).value == 11 && !p.moved_from);
    Payload src(22);
    Payload moved(std::move(src));
    CHECK(payload_move_marks_source, moved.value == 22 && src.moved_from);

    // ---- aligned pool: ordinary well-formed use ----
    AlignedPool pool(sizeof(Payload), 8);
    CHECK(pool_dims, pool.capacity() == 8 && pool.used() == 0);
    unsigned char* mem = pool.claim();
    CHECK(pool_claim, mem != 0 && pool.used() == 1);
    Payload* made = pool.create(0, false);
    CHECK(pool_create_default, made != 0 && made->value == 0 && pool.used() == 2);
    Payload seed(7);
    Payload* made2 = pool.create(&seed, true);
    CHECK(pool_create_from, made2 != 0 && made2->value == 7);

    // ---- ring: power-of-two capacity, small workload ----
    RingQueue q(16);
    CHECK(ring_capacity_power_of_two, q.capacity() == 16);
    CHECK(ring_empty_initial, q.empty() && q.size() == 0);
    for (int i = 1; i <= 5; ++i) q.push_int(i);
    CHECK(ring_size_small, q.size() == 5 && !q.full());
    bool fifo = true;
    for (int i = 1; i <= 5; ++i) {
        int v = -1;
        fifo = fifo && q.pop_int(v) && v == i;
    }
    CHECK(ring_fifo_small, fifo && q.empty());

    // ---- scheduler: happy path, one run ----
    Scheduler s(4);
    CHECK(sched_submit, s.submit(twice, 3) && s.submit(plus5, 10));
    std::size_t ran = s.run_all();
    CHECK(sched_run_count, ran == 2);
    CHECK(sched_done_flags, s.done(0) && s.done(1));

    // ---- clamp and primes on ordinary values ----
    CHECK(clamp_within, Scheduler::clamp_int<int>(5, 0, 10) == 5);
    CHECK(prime_naive_small, Scheduler::is_prime_naive(7));
    CHECK(prime_optimized_small, Scheduler::is_prime_optimized(7));
    return 0;
}
