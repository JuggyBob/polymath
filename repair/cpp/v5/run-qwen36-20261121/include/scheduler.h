#ifndef STRATA_SCHEDULER_H
#define STRATA_SCHEDULER_H

#include <cstddef>
#include <type_traits>
#include "allocator.h"

// A task is a function taking one int and returning an int.
typedef int (*TaskFn)(int);

struct Task {
    TaskFn fn;
    int arg;
    int result;
    bool done;

    Task();
    Task(TaskFn f, int a);
};

// Fixed-capacity FIFO scheduler. Tasks are submitted, then executed exactly
// once by run_all(). Results are kept per submitted task, in submission order.
class Scheduler {
public:
    explicit Scheduler(std::size_t capacity);
    ~Scheduler();

    Scheduler(const Scheduler&) = delete;
    Scheduler& operator=(const Scheduler&) = delete;

    bool submit(TaskFn fn, int arg);       // false when the table is full
    std::size_t run_all();                 // runs every not-yet-run task, returns count
    std::size_t pending() const;           // submitted but not yet run
    std::size_t completed() const;         // run to completion
    int result(std::size_t index) const;   // result of the index-th submitted task
    bool done(std::size_t index) const;
    void reset();

    // Clamp 'value' into [lo, hi] and return it as a long long. The template
    // is enabled only for integral T. For unsigned T a negative lo or hi is
    // treated as 0, so the interval is never inverted.
    template <typename T>
    static typename std::enable_if<std::is_integral<T>::value, long long>::type
    clamp_int(T value, int lo, int hi);

    static bool is_prime_naive(int n);      // O(n) reference, keep correct
    static bool is_prime_optimized(int n);  // must be O(sqrt(n)), same answers

private:
    Task* tasks_;
    std::size_t capacity_;
    std::size_t count_;
    std::size_t next_run_;
};

extern template long long Scheduler::clamp_int<int>(int, int, int);
extern template long long Scheduler::clamp_int<long>(long, int, int);
extern template long long Scheduler::clamp_int<unsigned>(unsigned, int, int);
extern template long long Scheduler::clamp_int<unsigned long>(unsigned long, int, int);

#endif
