#include <iostream>
#include <cstdlib>
#include <new>
#include <string>
#include "map.h"

#define CHECK(name, cond) std::cout << "TEST " << #name << " " << ((cond) ? "PASS" : "FAIL") << "\n"

// Count outstanding new[] allocations so the rule-of-three tests can see
// whether owned arrays are released exactly once.
static long g_live_arrays = 0;

void* operator new[](std::size_t n) {
    void* p = std::malloc(n ? n : 1);
    if (!p) throw std::bad_alloc();
    ++g_live_arrays;
    return p;
}

void operator delete[](void* p) noexcept {
    if (p) --g_live_arrays;
    std::free(p);
}

void operator delete[](void* p, std::size_t) noexcept {
    if (p) --g_live_arrays;
    std::free(p);
}

static std::string key_at(int cap, int slot, int seed) {
    for (int i = seed; i < seed + 100000; ++i) {
        std::string s = "key" + std::to_string(i);
        if (StringMap::home_slot(s, cap) == slot) return s;
    }
    return "no_such_key";
}

int main() {
    int vals[] = {10, 20, 30};

    // ---- StringMap basics ----
    StringMap m;
    m.insert("alpha", 1);
    m.insert("gamma", 3);
    m.insert("delta", 5);

    int out = -1;
    bool got_alpha = m.get("alpha", out);
    bool alpha_ok = got_alpha && out == 1;
    bool got_gamma = m.get("gamma", out);
    bool gamma_ok = got_gamma && out == 3;
    CHECK(v_basic_insert_get, alpha_ok && gamma_ok);

    CHECK(v_size_after_insert, m.size() == 3);

    bool has_alpha = m.contains("alpha");
    bool has_missing = m.contains("absent");
    CHECK(v_contains, has_alpha && !has_missing);

    m.insert("alpha", 99);
    int after = -1;
    bool got_after = m.get("alpha", after);
    CHECK(v_overwrite, got_after && after == 99 && m.size() == 3);

    bool removed = m.remove("gamma");
    CHECK(v_remove_size, removed && m.size() == 2);

    bool still_there = m.contains("gamma");
    CHECK(v_remove_contains, !still_there);

    StringMap cases;
    cases.insert("Cat", 1);
    cases.insert("cat", 2);
    int upper = -1;
    int lower = -1;
    bool got_upper = cases.get("Cat", upper);
    bool got_lower = cases.get("cat", lower);
    CHECK(v_case_sensitive, cases.size() == 2 && got_upper && upper == 1 &&
                            got_lower && lower == 2);

    CHECK(v_hash_example, StringMap::hash_key("cat") == 108289031u);

    StringMap fresh;
    CHECK(v_capacity_initial, fresh.capacity() == 8);

    StringMap grow;
    for (int i = 0; i < 7; ++i) {
        std::string k = "k" + std::to_string(i);
        grow.insert(k, i);
    }
    CHECK(v_capacity_growth, grow.capacity() == 16 && grow.size() == 7);

    // Three keys with the same home slot: removing the middle one must not
    // hide the third one from lookup.
    StringMap chain;
    std::string a = key_at(8, 3, 0);
    std::string b = key_at(8, 3, 5000);
    std::string c = key_at(8, 3, 10000);
    chain.insert(a, 1);
    chain.insert(b, 2);
    chain.insert(c, 3);
    chain.remove(b);
    int third = -1;
    bool got_third = chain.get(c, third);
    CHECK(v_tombstone_lookup, got_third && third == 3 && chain.size() == 2);

    // A key whose home slot is the last slot has to wrap around to slot 0.
    StringMap wrap;
    std::string last = key_at(8, 7, 0);
    std::string wrapped = key_at(8, 7, 5000);
    wrap.insert(last, 11);
    wrap.insert(wrapped, 22);
    int wrapped_value = -1;
    bool got_wrapped = wrap.get(wrapped, wrapped_value);
    CHECK(v_wraparound, got_wrapped && wrapped_value == 22);

    // ---- Buffer (rule of three) ----
    Buffer buf(vals, 3);
    CHECK(v_buffer_get, buf.get(0) == 10 && buf.get(1) == 20);

    Buffer copied(buf);
    copied.set(0, 77);
    CHECK(v_buffer_deep_copy, copied.data != buf.data && buf.get(0) == 10);

    Buffer self(vals, 3);
    self = self;
    CHECK(v_self_assign, self.length() == 3 && self.data != 0);

    long before = g_live_arrays;
    {
        Buffer temp(vals, 3);
        (void)temp;
    }
    CHECK(v_buffer_destructor, g_live_arrays == before);

    return 0;
}
