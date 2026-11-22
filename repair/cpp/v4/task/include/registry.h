#ifndef STRATA_REGISTRY_H
#define STRATA_REGISTRY_H

#include <cstddef>

// A small table of named function callbacks with a one-entry result cache.
class Registry {
public:
    typedef double (*Callback)(double);

    Registry();

    void add(const char* name, Callback cb);
    bool has(const char* name) const;
    double call(const char* name, double x) const;
    double cached(const char* name, double x);
    void clear_cache();
    std::size_t size() const;

private:
    static const std::size_t CAPACITY = 8;
    char names_[CAPACITY][32];
    Callback callbacks_[CAPACITY];
    std::size_t count_;
    std::size_t cache_key_;
    double cache_value_;
    bool cache_valid_;
};

#endif
