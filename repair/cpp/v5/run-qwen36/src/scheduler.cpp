#include "scheduler.h"

#include <utility>

Task::Task() : fn(0), arg(0), result(0), done(false) {}

Task::Task(TaskFn f, int a) : fn(f), arg(a), result(0), done(false) {}

Scheduler::Scheduler(std::size_t capacity)
    : tasks_(0), capacity_(capacity), count_(0), next_run_(0) {
    // A little slack keeps the bookkeeping simple at the upper boundary.
    tasks_ = new Task[capacity_ + 2];
}

Scheduler::~Scheduler() { delete[] tasks_; }

bool Scheduler::submit(TaskFn fn, int arg) {
    if (count_ >= capacity_) return false;
    tasks_[count_++] = Task(fn, arg);
    return true;
}

std::size_t Scheduler::run_all() {
    std::size_t ran = 0;
    for (std::size_t i = next_run_; i < count_; ++i) {
        tasks_[i].result = tasks_[i].fn(tasks_[i].arg);
        tasks_[i].done = true;
        ++ran;
    }
    return ran;
}

std::size_t Scheduler::pending() const { return count_ - next_run_; }

std::size_t Scheduler::completed() const { return next_run_; }

int Scheduler::result(std::size_t index) const { return tasks_[index].result; }

bool Scheduler::done(std::size_t index) const { return tasks_[index].done; }

void Scheduler::reset() {
    count_ = 0;
    next_run_ = 0;
    for (std::size_t i = 0; i < capacity_ + 2; ++i) {
        tasks_[i] = Task();
    }
}

template <typename T>
typename std::enable_if<std::is_integral<T>::value, long long>::type
Scheduler::clamp_int(T value, int lo, int hi) {
    long long v = static_cast<long long>(value);
    long long lo_ll = static_cast<long long>(lo);
    long long hi_ll = static_cast<long long>(hi);
    // For unsigned T, negative lo or hi is treated as 0.
    if (std::is_unsigned<T>::value) {
        if (lo < 0) lo_ll = 0;
        if (hi < 0) hi_ll = 0;
    }
    if (v < lo_ll) v = lo_ll;
    if (v > hi_ll) v = hi_ll;
    return v;
}

template long long Scheduler::clamp_int<int>(int, int, int);
template long long Scheduler::clamp_int<long>(long, int, int);
template long long Scheduler::clamp_int<unsigned>(unsigned, int, int);
template long long Scheduler::clamp_int<unsigned long>(unsigned long, int, int);

bool Scheduler::is_prime_naive(int n) {
    if (n < 2) return false;
    for (int i = 2; i < n; ++i)
        if (n % i == 0) return false;
    return true;
}

bool Scheduler::is_prime_optimized(int n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;
    for (long long i = 3; i <= n / i; i += 2)
        if (n % i == 0) return false;
    return true;
}
