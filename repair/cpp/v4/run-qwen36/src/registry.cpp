#include "registry.h"

#include <cstring>
#include <functional>

Registry::Registry()
    : count_(0), cache_key_(0), cache_value_(0.0), cache_valid_(false) {
    for (std::size_t i = 0; i < CAPACITY; ++i) {
        names_[i][0] = '\0';
        callbacks_[i] = 0;
    }
}

void Registry::add(const char* name, Callback cb) {
    // Check if name already exists — replace in place.
    for (std::size_t i = 0; i < count_; ++i) {
        if (std::strcmp(names_[i], name) == 0) {
            callbacks_[i] = cb;
            return;
        }
    }
    // Not found — register only if capacity allows.
    if (count_ >= CAPACITY) return;
    std::strncpy(names_[count_], name, 31);
    names_[count_][31] = '\0';
    callbacks_[count_] = cb;
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
    std::size_t key = 0;
    // Build a simple hash from name and x for cache lookup.
    for (std::size_t i = 0; name[i] != '\0'; ++i) key = key * 31 + static_cast<std::size_t>(name[i]);
    key = key * 31 + static_cast<std::size_t>(std::hash<double>{}(x));
    if (cache_valid_ && cache_key_ == key) return cache_value_;
    cache_value_ = call(name, x);
    cache_key_ = key;
    cache_valid_ = true;
    return cache_value_;
}

void Registry::clear_cache() { cache_valid_ = false; }

std::size_t Registry::size() const { return count_; }
