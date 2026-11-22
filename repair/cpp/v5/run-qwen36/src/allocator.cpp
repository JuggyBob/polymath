#include "allocator.h"

#include <new>
#include <utility>

static int g_copies = 0;
static int g_moves = 0;
static int g_destructions = 0;

Payload::Payload(int v) : value(v), moved_from(false) {}

Payload::Payload(const Payload& other) : value(other.value), moved_from(false) {
    ++g_copies;
}

Payload::Payload(Payload&& other) noexcept : value(other.value), moved_from(false) {
    ++g_moves;
    other.moved_from = true;
    other.value = 0;
}

Payload& Payload::operator=(const Payload& other) {
    value = other.value;
    moved_from = false;
    ++g_copies;
    return *this;
}

Payload& Payload::operator=(Payload&& other) noexcept {
    value = other.value;
    moved_from = false;
    ++g_moves;
    other.moved_from = true;
    other.value = 0;
    return *this;
}

Payload::~Payload() { ++g_destructions; }

int PayloadStats::copies() { return g_copies; }
int PayloadStats::moves() { return g_moves; }
int PayloadStats::destructions() { return g_destructions; }
void PayloadStats::reset() {
    g_copies = 0;
    g_moves = 0;
    g_destructions = 0;
}

AlignedPool::AlignedPool(std::size_t slot_size, std::size_t capacity)
    : raw_(0), data_(0), slot_size_(slot_size), capacity_(capacity), used_(0) {
    // Over-allocate so we can align the first slot to 64 bytes.
    std::size_t total = slot_size_ * capacity_;
    unsigned char* base = new unsigned char[total + 63];
    // Align up to 64-byte boundary.
    std::uintptr_t addr = reinterpret_cast<std::uintptr_t>(base);
    addr = (addr + 63) & ~std::uintptr_t(63);
    data_ = reinterpret_cast<unsigned char*>(addr);
    raw_ = base;
}

AlignedPool::~AlignedPool() {
    // Destroy any remaining live objects.
    for (std::size_t i = 0; i < used_; ++i) {
        reinterpret_cast<Payload*>(slot(i))->~Payload();
    }
    delete[] raw_;
}

AlignedPool::AlignedPool(AlignedPool&& other) noexcept
    : raw_(other.raw_),
      data_(other.data_),
      slot_size_(other.slot_size_),
      capacity_(other.capacity_),
      used_(other.used_) {
    other.raw_ = 0;
    other.data_ = 0;
    other.slot_size_ = 0;
    other.capacity_ = 0;
    other.used_ = 0;
}

AlignedPool& AlignedPool::operator=(AlignedPool&& other) noexcept {
    if (this == &other) return *this;
    // Destroy our current objects and free our memory.
    for (std::size_t i = 0; i < used_; ++i) {
        reinterpret_cast<Payload*>(slot(i))->~Payload();
    }
    delete[] raw_;
    // Steal from other.
    raw_ = other.raw_;
    data_ = other.data_;
    slot_size_ = other.slot_size_;
    capacity_ = other.capacity_;
    used_ = other.used_;
    // Empty the source.
    other.raw_ = 0;
    other.data_ = 0;
    other.slot_size_ = 0;
    other.capacity_ = 0;
    other.used_ = 0;
    return *this;
}

std::size_t AlignedPool::capacity() const { return capacity_; }
std::size_t AlignedPool::used() const { return used_; }
bool AlignedPool::full() const { return used_ == capacity_; }

unsigned char* AlignedPool::slot(std::size_t index) {
    return data_ + index * slot_size_;
}

const unsigned char* AlignedPool::slot(std::size_t index) const {
    return data_ + index * slot_size_;
}

unsigned char* AlignedPool::claim() {
    if (used_ >= capacity_) return nullptr;
    return slot(used_++);
}

Payload* AlignedPool::create(const Payload* from, bool move_it) {
    unsigned char* mem = claim();
    if (!mem) return nullptr;
    if (from) {
        if (move_it) {
            return new (mem) Payload(std::move(const_cast<Payload&>(*from)));
        } else {
            return new (mem) Payload(*from);
        }
    }
    return new (mem) Payload();
}

void AlignedPool::release(Payload* p) {
    p->~Payload();
    if (used_ > 0) --used_;
}

void AlignedPool::clear() {
    for (std::size_t i = 0; i < used_; ++i) {
        reinterpret_cast<Payload*>(slot(i))->~Payload();
    }
    used_ = 0;
}
