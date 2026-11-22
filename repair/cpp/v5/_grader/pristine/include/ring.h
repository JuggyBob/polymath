#ifndef STRATA_RING_H
#define STRATA_RING_H

#include <cstddef>
#include <atomic>
#include "allocator.h"

// A single-producer / single-consumer ring buffer. The requested capacity is
// rounded up to the next power of two. The producer and consumer cursors are
// kept on separate cache lines so they never false-share. Both cursors are
// monotonically increasing counters; a physical slot is cursor & (capacity-1).
class RingQueue {
public:
    explicit RingQueue(std::size_t requested_capacity);
    ~RingQueue();

    RingQueue(const RingQueue&) = delete;
    RingQueue& operator=(const RingQueue&) = delete;

    std::size_t capacity() const;   // the rounded-up power of two
    std::size_t size() const;       // item count; MUST be O(1)
    bool empty() const;
    bool full() const;              // true exactly when size() == capacity()

    // Return false and change nothing when the ring is full.
    bool push(const Payload& item); // lvalue: copies, source is left unchanged
    bool push(Payload&& item);      // rvalue: moves from the source
    bool push_int(int value);

    // Return false and leave 'out' unchanged when the ring is empty.
    bool pop(Payload& out);
    bool pop_int(int& out);

private:
    Payload* data_;
    std::size_t mask_;
    std::size_t capacity_;
    alignas(64) std::atomic<std::size_t> head_;   // producer cursor
    char producer_pad_[64];
    alignas(64) std::atomic<std::size_t> tail_;   // consumer cursor
    char consumer_pad_[64];
};

#endif
