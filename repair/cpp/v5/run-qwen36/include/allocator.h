#ifndef STRATA_ALLOCATOR_H
#define STRATA_ALLOCATOR_H

#include <cstddef>
#include <cstdint>

// A tiny observable payload. Copy construction leaves the source untouched;
// move construction marks the source as moved_from. The counters below are
// process-wide and can be read and reset by tests.
struct Payload {
    int value;
    bool moved_from;

    Payload(int v = 0);
    Payload(const Payload& other);              // copy: source unchanged
    Payload(Payload&& other) noexcept;          // move: source.moved_from = true
    Payload& operator=(const Payload& other);
    Payload& operator=(Payload&& other) noexcept;
    ~Payload();
};

struct PayloadStats {
    static int copies();
    static int moves();
    static int destructions();
    static void reset();
};

// A fixed-capacity pool of raw slots. Every slot begins on a 64-byte boundary.
// The pool owns the raw bytes; objects are created and destroyed explicitly
// with create() and release().
class AlignedPool {
public:
    AlignedPool(std::size_t slot_size, std::size_t capacity);
    ~AlignedPool();

    AlignedPool(const AlignedPool&) = delete;
    AlignedPool& operator=(const AlignedPool&) = delete;
    AlignedPool(AlignedPool&& other) noexcept;
    AlignedPool& operator=(AlignedPool&& other) noexcept;

    std::size_t capacity() const;
    std::size_t used() const;
    bool full() const;

    // Raw address of slot 'index'; valid for index in [0, capacity()).
    unsigned char* slot(std::size_t index);
    const unsigned char* slot(std::size_t index) const;

    // Reserve the next free slot and return its address, or nullptr when the
    // pool is already at capacity.
    unsigned char* claim();

    // Place a Payload in the next free slot. When 'from' is non-null the new
    // object is a COPY of *from if move_it is false, and is MOVE-constructed
    // from *from if move_it is true. Returns nullptr when the pool is full.
    Payload* create(const Payload* from, bool move_it);

    // Run ~Payload() on p and return its slot to the free list.
    void release(Payload* p);

    // Run ~Payload() on every live object and reset the pool.
    void clear();

private:
    unsigned char* raw_;       // allocation base (what delete[] releases)
    unsigned char* data_;      // 64-byte aligned start of the slots
    std::size_t slot_size_;
    std::size_t capacity_;
    std::size_t used_;
};

#endif
