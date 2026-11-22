#include "ring.h"

#include <utility>

static std::size_t round_up_power_of_two(std::size_t n) {
    std::size_t p = 1;
    while (p < n) p <<= 1;
    return p;
}

RingQueue::RingQueue(std::size_t requested_capacity)
    : data_(0), mask_(0), capacity_(0), head_(0), tail_(0) {
    capacity_ = round_up_power_of_two(requested_capacity);
    data_ = new Payload[capacity_];
    mask_ = capacity_ - 1;
}

RingQueue::~RingQueue() { delete[] data_; }

std::size_t RingQueue::capacity() const { return capacity_; }

std::size_t RingQueue::size() const {
    std::size_t h = head_.load(std::memory_order_acquire);
    std::size_t t = tail_.load(std::memory_order_acquire);
    return h - t;
}

bool RingQueue::empty() const { return size() == 0; }

bool RingQueue::full() const { return size() == capacity_; }

bool RingQueue::push(const Payload& item) {
    std::size_t h = head_.load(std::memory_order_relaxed);
    std::size_t t = tail_.load(std::memory_order_relaxed);
    if (h - t >= capacity_) return false;
    new (&data_[h & mask_]) Payload(item);
    head_.store(h + 1, std::memory_order_release);
    return true;
}

bool RingQueue::push(Payload&& item) {
    std::size_t h = head_.load(std::memory_order_relaxed);
    std::size_t t = tail_.load(std::memory_order_relaxed);
    if (h - t >= capacity_) return false;
    new (&data_[h & mask_]) Payload(std::move(item));
    head_.store(h + 1, std::memory_order_release);
    return true;
}

bool RingQueue::push_int(int value) {
    std::size_t h = head_.load(std::memory_order_relaxed);
    std::size_t t = tail_.load(std::memory_order_relaxed);
    if (h - t >= capacity_) return false;
    new (&data_[h & mask_]) Payload(value);
    head_.store(h + 1, std::memory_order_release);
    return true;
}

bool RingQueue::pop(Payload& out) {
    std::size_t h = head_.load(std::memory_order_acquire);
    std::size_t t = tail_.load(std::memory_order_relaxed);
    if (h == t) return false;
    out = data_[t & mask_];
    tail_.store(t + 1, std::memory_order_release);
    return true;
}

bool RingQueue::pop_int(int& out) {
    std::size_t h = head_.load(std::memory_order_acquire);
    std::size_t t = tail_.load(std::memory_order_relaxed);
    if (h == t) return false;
    out = data_[t & mask_].value;
    tail_.store(t + 1, std::memory_order_release);
    return true;
}
