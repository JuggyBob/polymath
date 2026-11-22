#include <iostream>
#include <cstdlib>
#include <new>
#include <string>
#include "map.h"

#define CHECK(name, cond) std::cout << "TEST " << #name << " " << ((cond) ? "PASS" : "FAIL") << "\n"

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
    // ---- hash and home slot ----
    CHECK(test_h_hash_empty, StringMap::hash_key("") == 2166136261u);
    CHECK(test_h_hash_a, StringMap::hash_key("a") == 3826002220u);

    bool home1 = StringMap::home_slot("cat", 8) == 7;
    bool home2 = StringMap::home_slot("Apple", 16) == 15;
    bool home3 = StringMap::home_slot("alpha", 8) == 3;
    CHECK(test_h_home_slots, home1 && home2 && home3);

    // ---- empty map ----
    StringMap empty;
    int untouched = 77;
    bool absent_get = empty.get("x", untouched);
    CHECK(test_h_empty_map, empty.size() == 0 && empty.capacity() == 8 &&
                            empty.tombstones() == 0 && !absent_get &&
                            untouched == 77 && !empty.contains("x") &&
                            !empty.remove("x"));

    // ---- many inserts and gets ----
    StringMap many;
    for (int i = 0; i < 10; ++i) {
        std::string k = "k" + std::to_string(i);
        many.insert(k, i * i);
    }
    bool all_found = true;
    for (int i = 0; i < 10; ++i) {
        std::string k = "k" + std::to_string(i);
        int v = -1;
        if (!many.get(k, v) || v != i * i) all_found = false;
    }
    CHECK(test_h_insert_get_many, all_found && many.size() == 10);

    int kept = 4242;
    bool missed = many.get("k999", kept);
    CHECK(test_h_get_missing_unchanged, !missed && kept == 4242);

    // ---- duplicate keys (ties) ----
    StringMap ties;
    ties.insert("dup", 1);
    ties.insert("dup", 2);
    ties.insert("dup", 3);
    int tie_value = -1;
    bool got_tie = ties.get("dup", tie_value);
    CHECK(test_h_overwrite_keeps_size, got_tie && tie_value == 3 && ties.size() == 1);

    // ---- case sensitivity ----
    StringMap cased;
    cased.insert("Foo", 1);
    cased.insert("foo", 2);
    cased.insert("FOO", 3);
    int lower = -1;
    int upper = -1;
    bool got_lower = cased.get("foo", lower);
    bool got_upper = cased.get("FOO", upper);
    CHECK(test_h_case_distinct, cased.size() == 3 && got_lower && lower == 2 &&
                                got_upper && upper == 3);

    // ---- removal ----
    StringMap rem;
    bool missing_remove = rem.remove("never");
    CHECK(test_h_remove_missing, !missing_remove && rem.size() == 0);

    StringMap rem2;
    for (int i = 0; i < 6; ++i) {
        std::string k = "r" + std::to_string(i);
        rem2.insert(k, i);
    }
    bool removed0 = rem2.remove("r0");
    bool removed1 = rem2.remove("r1");
    CHECK(test_h_remove_size_many, removed0 && removed1 && rem2.size() == 4);

    CHECK(test_h_tombstones_count, rem2.tombstones() == 2);

    // ---- probing around tombstones ----
    StringMap chain;
    std::string a = key_at(8, 3, 0);
    std::string b = key_at(8, 3, 5000);
    std::string c = key_at(8, 3, 10000);
    chain.insert(a, 1);
    chain.insert(b, 2);
    chain.insert(c, 3);
    chain.remove(b);
    int after_tomb = -1;
    bool got_after = chain.get(c, after_tomb);
    CHECK(test_h_tombstone_skip, got_after && after_tomb == 3 && chain.size() == 2);

    StringMap reuse;
    std::string r1 = key_at(8, 4, 20000);
    std::string r2 = key_at(8, 4, 25000);
    std::string r3 = key_at(8, 4, 30000);
    reuse.insert(r1, 1);
    reuse.insert(r2, 2);
    reuse.remove(r1);
    reuse.insert(r3, 3);
    int v2 = -1;
    int v3 = -1;
    bool got_v2 = reuse.get(r2, v2);
    bool got_v3 = reuse.get(r3, v3);
    CHECK(test_h_tombstone_reuse, got_v2 && v2 == 2 && got_v3 && v3 == 3 &&
                                  reuse.size() == 2);

    // ---- wraparound ----
    StringMap wrap;
    std::string w1 = key_at(8, 7, 0);
    std::string w2 = key_at(8, 7, 40000);
    wrap.insert(w1, 11);
    wrap.insert(w2, 22);
    int wrapped = -1;
    bool got_wrapped = wrap.get(w2, wrapped);
    CHECK(test_h_wraparound_lookup, got_wrapped && wrapped == 22);

    bool wrap_removed = wrap.remove(w2);
    CHECK(test_h_wraparound_remove, wrap_removed && !wrap.contains(w2) &&
                                    wrap.contains(w1));

    // ---- growth ----
    StringMap grow;
    for (int i = 0; i < 7; ++i) {
        std::string k = "g" + std::to_string(i);
        grow.insert(k, i + 100);
    }
    bool kept_after_growth = true;
    for (int i = 0; i < 7; ++i) {
        std::string k = "g" + std::to_string(i);
        int v = -1;
        if (!grow.get(k, v) || v != i + 100) kept_after_growth = false;
    }
    CHECK(test_h_growth_preserves, grow.capacity() == 16 && grow.size() == 7 &&
                                   kept_after_growth);

    StringMap big;
    for (int i = 0; i < 20; ++i) {
        std::string k = "b" + std::to_string(i);
        big.insert(k, i);
    }
    bool big_ok = big.capacity() == 32 && big.size() == 20;
    for (int i = 0; i < 20 && big_ok; ++i) {
        std::string k = "b" + std::to_string(i);
        int v = -1;
        if (!big.get(k, v) || v != i) big_ok = false;
    }
    CHECK(test_h_growth_twice, big_ok);

    // ---- StringMap value semantics ----
    StringMap origin;
    origin.insert("one", 1);
    origin.insert("two", 2);
    StringMap copy(origin);
    copy.insert("three", 3);
    copy.remove("one");
    int one_still = -1;
    bool got_one_still = origin.get("one", one_still);
    bool three_absent = !origin.contains("three");
    CHECK(test_h_copy_map_independent, got_one_still && one_still == 1 &&
                                       three_absent && copy.size() == 2 &&
                                       origin.size() == 2 && !copy.contains("one") &&
                                       copy.contains("three"));

    StringMap target;
    target.insert("old", 9);
    target = origin;
    int old_gone = -1;
    bool got_old = target.get("old", old_gone);
    int two_copy = -1;
    bool got_two_copy = target.get("two", two_copy);
    CHECK(test_h_assign_map_independent, !got_old && got_two_copy && two_copy == 2 &&
                                         target.size() == 2);

    StringMap selfmap(origin);
    selfmap = selfmap;
    int self_value = -1;
    bool got_self = selfmap.get("one", self_value);
    CHECK(test_h_map_self_assign, got_self && self_value == 1 && selfmap.size() == 2);

    // ---- Buffer ----
    int vals[] = {4, 8, 15, 16, 23, 42};
    Buffer buf(vals, 6);
    buf.set(2, 99);
    int set_got = buf.get(2);
    CHECK(test_h_buffer_set_get, set_got == 99);

    Buffer bc(buf);
    bool separate = bc.data != buf.data;
    bc.set(0, -1);
    int b0 = buf.get(0);
    CHECK(test_h_buffer_copy_ctor, separate && b0 == 4 && bc.get(0) == -1);

    Buffer assigned(vals, 2);
    assigned = buf;
    bool assigned_separate = assigned.data != buf.data;
    assigned.set(1, -5);
    int b1 = buf.get(1);
    CHECK(test_h_buffer_assign, assigned_separate && b1 == 8 &&
                                assigned.length() == 6 && assigned.get(1) == -5);

    Buffer selfbuf(vals, 3);
    int* selfptr = selfbuf.data;
    selfbuf = selfbuf;
    CHECK(test_h_buffer_self_assign, selfbuf.length() == 3 &&
                                     selfbuf.data == selfptr && selfbuf.get(0) == 4);

    long before = g_live_arrays;
    {
        Buffer temp(vals, 6);
        (void)temp;
    }
    bool buffer_freed = g_live_arrays == before;
    CHECK(test_h_buffer_destructor, buffer_freed);

    long map_before = g_live_arrays;
    {
        StringMap scoped;
        scoped.insert("aa", 1);
        scoped.insert("bb", 2);
    }
    bool map_freed = g_live_arrays == map_before;
    CHECK(test_h_map_destructor, map_freed);

    return 0;
}
