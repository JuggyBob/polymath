#ifndef MINIVM_VALUE_H
#define MINIVM_VALUE_H

#include <cstdint>
#include <string>
#include <vector>

namespace minivm {

// A tagged value: the tag says which payload is live.  Every payload is kept
// in its own field so copies are simple and moves can mark the source.
enum class Type : int { Null = 0, Int = 1, Str = 2, Bool = 3, Array = 4 };

struct Value {
    Type type;
    int64_t i;
    std::string s;
    bool b;
    std::vector<Value> arr;
    bool moved_from;

    Value();
    explicit Value(int64_t v);
    explicit Value(const char* v);
    explicit Value(std::string v);
    explicit Value(bool v);

    static Value null_value();
    static Value array_value();

    Value(const Value& other);
    Value(Value&& other) noexcept;
    Value& operator=(const Value& other);
    Value& operator=(Value&& other) noexcept;

    void clear();
    std::string repr() const;
    bool truthy() const;
};

bool value_eq(const Value& a, const Value& b);

}  // namespace minivm

#endif
