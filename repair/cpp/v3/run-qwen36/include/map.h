#ifndef MAP_H
#define MAP_H

#include <string>

// An owning, fixed-length array of ints. Buffer follows the rule of three:
// every Buffer owns its own storage, including after a copy or an assignment.
struct Buffer {
    int* data;
    int count;

    Buffer();
    Buffer(const int* values, int n);
    Buffer(const Buffer& other);
    Buffer& operator=(const Buffer& other);
    ~Buffer();

    int get(int index) const;
    void set(int index, int value);
    int length() const;
};

// One slot of a StringMap table.
// state 0 = EMPTY (never used), 1 = OCCUPIED, 2 = TOMB (removed).
struct Entry {
    std::string key;
    int value;
    int state;

    Entry();
};

// A string-keyed hash map using open addressing with linear probing.
// Keys are case-sensitive. The map owns its bucket array.
class StringMap {
public:
    StringMap();
    StringMap(const StringMap& other);
    StringMap& operator=(const StringMap& other);
    ~StringMap();

    void insert(const std::string& key, int value);
    bool get(const std::string& key, int& out) const;
    bool remove(const std::string& key);
    bool contains(const std::string& key) const;
    int size() const;
    int capacity() const;
    int tombstones() const;

    static unsigned int hash_key(const std::string& key);
    static int home_slot(const std::string& key, int cap);

private:
    Entry* buckets;
    int cap;
    int count;
    int used;  // occupied slots plus tombstones

    void rehash(int newCap);
    int find_slot(const std::string& key) const;
};

#endif
