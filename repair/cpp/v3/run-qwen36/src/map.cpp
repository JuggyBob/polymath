#include "map.h"

namespace {
const int EMPTY = 0;
const int OCCUPIED = 1;
const int TOMB = 2;

bool same_key(const std::string& a, const std::string& b) {
    return a == b;
}
}  // namespace

Entry::Entry() : key(), value(0), state(EMPTY) {}

Buffer::Buffer() : data(new int[1]), count(0) {}

Buffer::Buffer(const int* values, int n)
    : data(new int[n > 0 ? n : 1]), count(n) {
    for (int i = 0; i < n; ++i) data[i] = values[i];
}

Buffer::Buffer(const Buffer& other) : data(new int[other.count > 0 ? other.count : 1]), count(other.count) {
    for (int i = 0; i < other.count; ++i) data[i] = other.data[i];
}

Buffer& Buffer::operator=(const Buffer& other) {
    if (this == &other) return *this;
    int* fresh = new int[other.count > 0 ? other.count : 1];
    for (int i = 0; i < other.count; ++i) fresh[i] = other.data[i];
    delete[] data;
    data = fresh;
    count = other.count;
    return *this;
}

Buffer::~Buffer() {
    delete[] data;
}

int Buffer::get(int index) const {
    return data[index];
}

void Buffer::set(int index, int value) {
    data[index] = value;
}

int Buffer::length() const {
    return count;
}

unsigned int StringMap::hash_key(const std::string& key) {
    unsigned int h = 2166136261u;
    for (std::size_t i = 0; i < key.size(); ++i) {
        h = (h ^ static_cast<unsigned char>(key[i])) * 16777619u;
    }
    return h;
}

int StringMap::home_slot(const std::string& key, int cap) {
    return static_cast<int>(hash_key(key) % static_cast<unsigned int>(cap));
}

StringMap::StringMap() : buckets(new Entry[8]), cap(8), count(0), used(0) {}

StringMap::StringMap(const StringMap& other)
    : buckets(new Entry[other.cap]),
      cap(other.cap),
      count(other.count),
      used(other.used) {
    for (int i = 0; i < cap; ++i) buckets[i] = other.buckets[i];
}

StringMap& StringMap::operator=(const StringMap& other) {
    if (this == &other) return *this;
    Entry* fresh = new Entry[other.cap];
    for (int i = 0; i < other.cap; ++i) fresh[i] = other.buckets[i];
    delete[] buckets;
    buckets = fresh;
    cap = other.cap;
    count = other.count;
    used = other.used;
    return *this;
}

StringMap::~StringMap() {
    delete[] buckets;
}

int StringMap::find_slot(const std::string& key) const {
    int idx = home_slot(key, cap);
    for (int probes = 0; probes < cap; ++probes) {
        const Entry& e = buckets[idx];
        if (e.state == EMPTY) return -1;
        if (e.state == TOMB) { idx = (idx + 1) % cap; continue; }
        if (same_key(e.key, key)) return idx;
        idx = (idx + 1) % cap;
    }
    return -1;
}

void StringMap::rehash(int newCap) {
    Entry* old = buckets;
    int oldCap = cap;
    buckets = new Entry[newCap];
    cap = newCap;
    count = 0;
    used = 0;
    for (int i = 0; i < oldCap; ++i) {
        if (old[i].state == OCCUPIED) insert(old[i].key, old[i].value);
    }
    delete[] old;
}

void StringMap::insert(const std::string& key, int value) {
    int existing = find_slot(key);
    if (existing != -1) { buckets[existing].value = value; return; }

    if (used + 1 > cap * 3 / 4) rehash(cap * 2);

    int idx = home_slot(key, cap);
    int firstTomb = -1;
    for (int probes = 0; probes < cap; ++probes) {
        Entry& e = buckets[idx];
        if (e.state == EMPTY) {
            int target = (firstTomb != -1) ? firstTomb : idx;
            if (firstTomb == -1) ++used;
            buckets[target].key = key;
            buckets[target].value = value;
            buckets[target].state = OCCUPIED;
            ++count;
            return;
        }
        if (e.state == TOMB && firstTomb == -1) firstTomb = idx;
        idx = (idx + 1) % cap;
    }
}

bool StringMap::get(const std::string& key, int& out) const {
    int idx = find_slot(key);
    if (idx == -1) return false;
    out = buckets[idx].value;
    return true;
}

bool StringMap::remove(const std::string& key) {
    int idx = find_slot(key);
    if (idx == -1) return false;
    buckets[idx].state = TOMB;
    --count;
    return true;
}

bool StringMap::contains(const std::string& key) const {
    return find_slot(key) != -1;
}

int StringMap::size() const {
    return count;
}

int StringMap::capacity() const {
    return cap;
}

int StringMap::tombstones() const {
    int n = 0;
    for (int i = 0; i < cap; ++i) {
        if (buckets[i].state == TOMB) ++n;
    }
    return n;
}
