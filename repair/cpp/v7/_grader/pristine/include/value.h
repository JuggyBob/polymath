#ifndef MINIVM_VALUE_H
#define MINIVM_VALUE_H

#include <cstddef>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace minivm {

enum class Type : int { Null = 0, Int = 1, Str = 2, Bool = 3, Array = 4 };

struct Value {
    Type type;
    int64_t i;
    std::string s;
    bool b;
    std::shared_ptr<std::vector<Value> > arr;

    Value();
    explicit Value(int64_t v);
    explicit Value(const char* v);
    explicit Value(std::string v);
    explicit Value(bool v);
    Value(const Value& o);
    Value& operator=(const Value& o);

    static Value array_value();
    std::string repr() const;
    bool truthy() const;
};

bool value_eq(const Value& a, const Value& b);
std::size_t utf8_len(const std::string& s);

}  // namespace minivm

#endif
