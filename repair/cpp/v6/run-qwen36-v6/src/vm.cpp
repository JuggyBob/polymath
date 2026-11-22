#include "vm.h"

#include <limits>
#include <utility>
#include <vector>

#include "compiler.h"
#include "lexer.h"
#include "parser.h"
#include "util.h"
#include "value.h"

namespace minivm {

static Value int_value(int64_t v) { return Value(v); }
static Value bool_value(bool v) { return Value(v); }

VMResult execute(const Bytecode& bc, int64_t max_steps) {
    VMResult result;
    std::vector<Value> stack;
    std::vector<std::pair<std::string, Value> > vars;

    auto pop = [&]() -> Value {
        if (stack.empty()) return Value();
        Value v = stack.back();
        stack.pop_back();
        return v;
    };
    auto push = [&](Value v) { stack.push_back(std::move(v)); };

    int64_t ip = 0;
    int64_t steps = 0;
    const int64_t n = static_cast<int64_t>(bc.code.size());

    while (ip >= 0 && ip < n && steps < max_steps) {
        ++steps;
        const Ins& in = bc.code[static_cast<std::size_t>(ip)];
        ++ip;

        switch (in.op) {
            case Op::PUSH: push(int_value(in.num)); break;
            case Op::STR:  push(Value(in.text)); break;
            case Op::TRUE: push(bool_value(true)); break;
            case Op::FALSE: push(bool_value(false)); break;
            case Op::NULLV: push(Value()); break;

            case Op::ADD: {
                Value b = pop(), a = pop();
                if (a.type == Type::Int && b.type == Type::Int)
                    push(int_value(add_sat(a.i, b.i)));
                else push(Value());
                break;
            }
            case Op::SUB: {
                Value b = pop(), a = pop();
                if (a.type == Type::Int && b.type == Type::Int)
                    push(int_value(sub_sat(a.i, b.i)));
                else push(Value());
                break;
            }
            case Op::MUL: {
                Value b = pop(), a = pop();
                if (a.type == Type::Int && b.type == Type::Int)
                    push(int_value(mul_sat(a.i, b.i)));
                else push(Value());
                break;
            }
            case Op::DIV: {
                Value b = pop(), a = pop();
                if (a.type != Type::Int || b.type != Type::Int) {
                    push(Value());
                } else if (b.i == 0) {
                    push(Value());
                } else if (a.i == std::numeric_limits<int64_t>::min() && b.i == -1) {
                    push(int_value(std::numeric_limits<int64_t>::max()));
                } else {
                    push(int_value(a.i / b.i));
                }
                break;
            }
            case Op::MOD: {
                Value b = pop(), a = pop();
                if (a.type != Type::Int || b.type != Type::Int || b.i == 0) {
                    push(Value());
                } else if (a.i == std::numeric_limits<int64_t>::min() && b.i == -1) {
                    push(int_value(0));
                } else {
                    push(int_value(a.i % b.i));
                }
                break;
            }

            case Op::EQ: {
                Value b = pop(), a = pop();
                push(bool_value(value_eq(a, b)));
                break;
            }
            case Op::NEQ: {
                Value b = pop(), a = pop();
                push(bool_value(!value_eq(a, b)));
                break;
            }
            case Op::LT: {
                Value b = pop(), a = pop();
                if (a.type == Type::Int && b.type == Type::Int) push(bool_value(a.i < b.i));
                else if (a.type == Type::Str && b.type == Type::Str) push(bool_value(a.s < b.s));
                else push(bool_value(false));
                break;
            }
            case Op::LE: {
                Value b = pop(), a = pop();
                if (a.type == Type::Int && b.type == Type::Int) push(bool_value(a.i <= b.i));
                else if (a.type == Type::Str && b.type == Type::Str) push(bool_value(a.s <= b.s));
                else push(bool_value(false));
                break;
            }
            case Op::GT: {
                Value b = pop(), a = pop();
                if (a.type == Type::Int && b.type == Type::Int) push(bool_value(a.i > b.i));
                else if (a.type == Type::Str && b.type == Type::Str) push(bool_value(a.s > b.s));
                else push(bool_value(false));
                break;
            }
            case Op::GE: {
                Value b = pop(), a = pop();
                if (a.type == Type::Int && b.type == Type::Int) push(bool_value(a.i >= b.i));
                else if (a.type == Type::Str && b.type == Type::Str) push(bool_value(a.s >= b.s));
                else push(bool_value(false));
                break;
            }

            case Op::CONCAT: {
                Value b = pop(), a = pop();
                push(Value(a.repr() + b.repr()));
                break;
            }
            case Op::LEN: {
                Value a = pop();
                if (a.type == Type::Str) push(int_value(static_cast<int64_t>(a.s.size())));
                else if (a.type == Type::Array) push(int_value(static_cast<int64_t>(a.arr.size())));
                else push(int_value(0));
                break;
            }
            case Op::NOT: {
                Value a = pop();
                push(bool_value(!a.truthy()));
                break;
            }
            case Op::AND: {
                Value b = pop(), a = pop();
                push(bool_value(a.truthy() && b.truthy()));
                break;
            }
            case Op::OR: {
                Value b = pop(), a = pop();
                push(bool_value(a.truthy() || b.truthy()));
                break;
            }

            case Op::DUP: {
                if (stack.empty()) { push(Value()); push(Value()); }
                else push(stack.back());
                break;
            }
            case Op::POP: pop(); break;
            case Op::SWAP: {
                if (stack.size() < 2) {
                    stack.push_back(Value());
                    if (stack.size() < 2) {
                        stack.push_back(Value());
                    }
                    std::swap(stack[stack.size() - 1], stack[stack.size() - 2]);
                } else {
                    std::size_t m = stack.size();
                    std::swap(stack[m - 1], stack[m - 2]);
                }
                break;
            }

            case Op::JMP: ip = in.num; break;
            case Op::JZ: {
                Value c = pop();
                if (!c.truthy()) ip = in.num;
                break;
            }
            case Op::JNZ: {
                Value c = pop();
                if (c.truthy()) ip = in.num;
                break;
            }

            case Op::SET: {
                bool found = false;
                for (std::size_t k = 0; k < vars.size(); ++k) {
                    if (vars[k].first == in.text) { vars[k].second = pop(); found = true; break; }
                }
                if (!found) vars.push_back(std::make_pair(in.text, pop()));
                break;
            }
            case Op::GET: {
                bool found = false;
                for (std::size_t k = 0; k < vars.size(); ++k) {
                    if (vars[k].first == in.text) { push(vars[k].second); found = true; break; }
                }
                if (!found) push(Value());
                break;
            }
            case Op::PRINT: {
                Value v = pop();
                result.output += v.repr();
                result.output += '\n';
                break;
            }
            case Op::HALT: result.halted = true; ip = n; break;

            case Op::ARRNEW: push(Value::array_value()); break;
            case Op::APUSH: {
                Value v = pop(), a = pop();
                if (a.type == Type::Array) {
                    a.arr.push_back(v);
                    push(std::move(a));
                } else {
                    push(Value());
                }
                break;
            }
            case Op::AGET: {
                Value idx = pop(), a = pop();
                if (a.type == Type::Array && idx.type == Type::Int &&
                    idx.i >= 0 && idx.i < static_cast<int64_t>(a.arr.size())) {
                    push(a.arr[static_cast<std::size_t>(idx.i)]);
                } else {
                    push(Value());
                }
                break;
            }
            case Op::DISTINCT: {
                Value b = pop(), a = pop();
                push(bool_value(!value_eq(a, b)));
                break;
            }
            default: ip = n; break;
        }
    }

    result.steps = steps;
    return result;
}

std::string run(const std::string& source) {
    std::vector<Token> toks = lex(source);
    std::vector<Node> nodes = parse(toks);
    Bytecode bc = compile(nodes);
    return execute(bc).output;
}

}  // namespace minivm
