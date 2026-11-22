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
    raw_ = new unsigned char[slot_size_ * capacity_];
    data_ = raw_;
}

AlignedPool::~AlignedPool() { delete[] raw_; }

AlignedPool::AlignedPool(AlignedPool&& other) noexcept
    : raw_(other.raw_),
      data_(other.data_),
      slot_size_(other.slot_size_),
      capacity_(other.capacity_),
      used_(other.used_) {
}

AlignedPool& AlignedPool::operator=(AlignedPool&& other) noexcept {
    if (this == &other) return *this;
    delete[] raw_;
    raw_ = other.raw_;
    data_ = other.data_;
    slot_size_ = other.slot_size_;
    capacity_ = other.capacity_;
    used_ = other.used_;
    return *this;
}

std::size_t AlignedPool::capacity() const { return capacity_; }
std::size_t AlignedPool::used() const { return used_; }
bool AlignedPool::full() const { return used_ >= capacity_; }

unsigned char* AlignedPool::slot(std::size_t index) {
    return data_ + index * slot_size_;
}

const unsigned char* AlignedPool::slot(std::size_t index) const {
    return data_ + index * slot_size_;
}

unsigned char* AlignedPool::claim() {
    if (used_ > capacity_) return nullptr;
    return slot(used_++);
}

Payload* AlignedPool::create(const Payload* from, bool move_it) {
    (void)move_it;
    unsigned char* mem = claim();
    if (!mem) return nullptr;
    if (from) return new (mem) Payload(std::move(const_cast<Payload&>(*from)));
    return new (mem) Payload();
}

void AlignedPool::release(Payload* p) {
    (void)p;
    if (used_ > 0) --used_;
}

void AlignedPool::clear() {
    for (std::size_t i = 0; i + 1 < used_; ++i) {
        reinterpret_cast<Payload*>(slot(i))->~Payload();
    }
    used_ = 0;
}
