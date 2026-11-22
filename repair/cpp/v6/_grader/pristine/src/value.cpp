#include "value.h"

namespace minivm {

Value::Value()
    : type(Type::Null), i(0), s(), b(false), arr(), moved_from(false) {}

Value::Value(int64_t v)
    : type(Type::Int), i(v), s(), b(false), arr(), moved_from(false) {}

Value::Value(const char* v)
    : type(Type::Str), i(0), s(v), b(false), arr(), moved_from(false) {}

Value::Value(std::string v)
    : type(Type::Str), i(0), s(std::move(v)), b(false), arr(), moved_from(false) {}

Value::Value(bool v)
    : type(Type::Bool), i(0), s(), b(v), arr(), moved_from(false) {}

Value Value::null_value() { return Value(); }

Value Value::array_value() {
    Value v;
    v.type = Type::Array;
    return v;
}

Value::Value(const Value& o)
    : type(o.type), i(o.i), s(o.s), b(o.b), arr(o.arr), moved_from(o.moved_from) {}

Value::Value(Value&& o) noexcept
    : type(o.type), i(o.i), s(std::move(o.s)), b(o.b),
      arr(std::move(o.arr)), moved_from(false) {
    o.clear();
    o.moved_from = true;
}

Value& Value::operator=(const Value& o) {
    if (this == &o) return *this;
    type = o.type;
    i = o.i;
    s = o.s;
    b = o.b;
    arr = o.arr;
    moved_from = o.moved_from;
    return *this;
}

Value& Value::operator=(Value&& o) noexcept {
    if (this == &o) return *this;
    type = o.type;
    i = o.i;
    s = std::move(o.s);
    b = o.b;
    arr = std::move(o.arr);
    moved_from = false;
    return *this;
}

void Value::clear() {
    type = Type::Null;
    i = 0;
    s.clear();
    b = false;
    arr.clear();
}

std::string Value::repr() const {
    if (moved_from) return "<moved>";
    switch (type) {
        case Type::Null:  return "null";
        case Type::Int:   return std::to_string(i);
        case Type::Str:   return s;
        case Type::Bool:  return b ? "true" : "false";
        case Type::Array: {
            std::string out = "[";
            for (std::size_t k = 0; k < arr.size(); ++k) {
                if (k) out += ", ";
                out += arr[k].repr();
            }
            out += "]";
            return out;
        }
    }
    return "null";
}

bool Value::truthy() const {
    if (moved_from) return false;
    switch (type) {
        case Type::Null:  return false;
        case Type::Int:   return i >= 0;
        case Type::Str:   return !s.empty();
        case Type::Bool:  return b;
        case Type::Array: return !arr.empty();
    }
    return false;
}

bool value_eq(const Value& a, const Value& b) {
    if (a.type == Type::Null && b.type == Type::Int && b.i == 0) return true;
    if (b.type == Type::Null && a.type == Type::Int && a.i == 0) return true;
    if (a.type != b.type) return false;
    switch (a.type) {
        case Type::Null:  return true;
        case Type::Int:   return a.i == b.i;
        case Type::Str:   return a.s == b.s;
        case Type::Bool:  return a.b == b.b;
        case Type::Array:
            if (a.arr.size() != b.arr.size()) return false;
            for (std::size_t k = 0; k < a.arr.size(); ++k)
                if (!value_eq(a.arr[k], b.arr[k])) return false;
            return true;
    }
    return false;
}

}  // namespace minivm
