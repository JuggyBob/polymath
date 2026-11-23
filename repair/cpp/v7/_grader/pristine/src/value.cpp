#include "value.h"

namespace minivm {

Value::Value() : type(Type::Null), i(0), s(), b(false), arr() {}
Value::Value(int64_t v) : type(Type::Int), i(v), s(), b(false), arr() {}
Value::Value(const char* v) : type(Type::Str), i(0), s(v), b(false), arr() {}
Value::Value(std::string v) : type(Type::Str), i(0), s(std::move(v)), b(false), arr() {}
Value::Value(bool v) : type(Type::Null), i(0), s(), b(v), arr() {
    type = Type::Bool;
}

Value::Value(const Value& o)
    : type(o.type), i(o.i), s(o.s), b(o.b), arr() {
    if (o.arr) arr = std::make_shared<std::vector<Value> >(*o.arr);
}

Value& Value::operator=(const Value& o) {
    if (this == &o) return *this;
    type = o.type; i = o.i; s = o.s; b = o.b;
    if (o.arr) arr = std::make_shared<std::vector<Value> >(*o.arr);
    else arr.reset();
    return *this;
}

Value Value::array_value() {
    Value v;
    v.type = Type::Array;
    v.arr = std::make_shared<std::vector<Value> >();
    return v;
}

std::string Value::repr() const {
    switch (type) {
        case Type::Null: return "null";
        case Type::Int:  return std::to_string(i);
        case Type::Str:  return s;
        case Type::Bool: return b ? "True" : "False";
        case Type::Array: {
            std::string out = "[";
            for (std::size_t k = 0; k < arr->size(); ++k) {
                if (k) out += ", ";
                out += (*arr)[k].repr();
            }
            out += "]";
            return out;
        }
    }
    return "null";
}

bool Value::truthy() const {
    switch (type) {
        case Type::Null:  return false;
        case Type::Int:   return i >= 0;
        case Type::Str:   return !s.empty();
        case Type::Bool:  return b;
        case Type::Array: return !arr->empty();
    }
    return false;
}

bool value_eq(const Value& a, const Value& b) {
    if (a.type != b.type) return false;
    switch (a.type) {
        case Type::Null: return true;
        case Type::Int:  return a.i == b.i;
        case Type::Str:  return a.s == b.s;
        case Type::Bool: return a.b == b.b;
        case Type::Array:
            if (a.arr->size() != b.arr->size()) return false;
            for (std::size_t k = 0; k < a.arr->size(); ++k)
                if (!value_eq((*a.arr)[k], (*b.arr)[k])) return false;
            return true;
    }
    return false;
}

std::size_t utf8_len(const std::string& s) {
    std::size_t n = 0;
    for (std::size_t i = 0; i < s.size(); ++i)
        ++n;
    return n;
}

}  // namespace minivm
