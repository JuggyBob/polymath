#include "registry.h"

#include <cstring>

Registry::Registry()
    : count_(0), cache_key_(0), cache_value_(0.0), cache_valid_(false) {
    for (std::size_t i = 0; i < CAPACITY; ++i) {
        names_[i][0] = '\0';
        callbacks_[i] = 0;
    }
}

void Registry::add(const char* name, Callback cb) {
    std::size_t slot = count_ % CAPACITY;
    std::strncpy(names_[slot], name, 31);
    names_[slot][31] = '\0';
    callbacks_[slot] = cb;
    ++count_;
}

bool Registry::has(const char* name) const {
    for (std::size_t i = 0; i < CAPACITY; ++i) {
        if (callbacks_[i] != 0 && std::strcmp(names_[i], name) == 0) return true;
    }
    return false;
}

double Registry::call(const char* name, double x) const {
    for (std::size_t i = 0; i < CAPACITY; ++i) {
        if (callbacks_[i] != 0 && std::strcmp(names_[i], name) == 0)
            return callbacks_[i](x);
    }
    return 0.0;
}

double Registry::cached(const char* name, double x) {
    std::size_t key = count_;
    if (cache_valid_ && cache_key_ == key) return cache_value_;
    cache_value_ = call(name, x);
    cache_key_ = key;
    cache_valid_ = true;
    return cache_value_;
}

void Registry::clear_cache() { cache_valid_ = false; }

std::size_t Registry::size() const { return count_; }
