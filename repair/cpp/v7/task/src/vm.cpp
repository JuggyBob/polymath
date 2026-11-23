#include "vm.h"

#include <limits>
#include <utility>

#include "util.h"

namespace minivm {

static Value intv(int64_t v) { return Value(v); }
static Value boolv(bool v) { return Value(v); }

VMResult execute(const Bytecode& bc, int64_t max_steps) {
    MiniVM vm;
    vm.code = bc;
    vm.global_names = bc.global_names;
    vm.globals.resize(vm.global_names.size());
    Fiber main;
    main.id = 0;
    main.pc = 0;
    vm.fibers.push_back(main);
    return vm.run_result(max_steps);
}

std::string MiniVM::run() { return run_result().output; }

VMResult MiniVM::run_result(int64_t max_steps) {
    VMResult result;
    output.clear();
    steps = 0;
    const int64_t n = static_cast<int64_t>(code.code.size());
    uint32_t current = fibers.empty() ? 0 : fibers[0].id;

    auto find_index = [&](uint32_t id) -> std::size_t {
        for (std::size_t i = 0; i < fibers.size(); ++i)
            if (fibers[i].id == id) return i;
        return fibers.size();
    };
    auto release_waiters = [&](uint32_t target) {
        for (std::size_t k = 0; k < blocked.size(); ++k)
            if (blocked[k].second == target) ready.push_back(blocked[k].first);
        std::vector<std::pair<uint32_t, uint32_t> > keep;
        for (std::size_t k = 0; k < blocked.size(); ++k)
            if (blocked[k].second != target) keep.push_back(blocked[k]);
        blocked.swap(keep);
    };
    auto next_ready = [&]() -> bool {
        if (ready.empty()) return false;
        current = ready.front();
        ready.erase(ready.begin());
        return true;
    };

    while (steps < max_steps) {
        std::size_t idx = find_index(current);
        if (idx == fibers.size() || fibers[idx].halted) {
            if (!next_ready()) break;
            continue;
        }
        Fiber& fib = fibers[idx];
        if (fib.pc < 0 || fib.pc >= n) {
            fib.halted = true;
            release_waiters(fib.id);
            if (!next_ready()) break;
            continue;
        }
        const Ins in = code.code[static_cast<std::size_t>(fib.pc)];
        ++fib.pc;
        ++steps;
        std::vector<Value>& st = fibers[idx].stack;

        auto pop = [&]() -> Value {
            if (st.empty()) return Value();
            Value v = st.back();
            st.pop_back();
            return v;
        };
        auto push = [&](Value v) { st.push_back(std::move(v)); };
        auto global_set = [&](int64_t k, const Value& v) {
            if (k < 0) return;
            std::size_t at = static_cast<std::size_t>(k);
            if (at >= globals.size()) globals.resize(at + 1);
            globals[at] = v;
        };
        auto global_get = [&](int64_t k) -> Value {
            if (k < 0 || static_cast<std::size_t>(k) >= globals.size()) return Value();
            return globals[static_cast<std::size_t>(k)];
        };

        switch (in.op) {
            case Op::PUSH: push(intv(in.num)); break;
            case Op::STR: push(Value(in.text)); break;
            case Op::TRUE: push(boolv(true)); break;
            case Op::FALSE: push(boolv(false)); break;
            case Op::NULLV: push(Value()); break;

            case Op::ADD: {
                Value b = pop(), a = pop();
                if (a.type == Type::Str || b.type == Type::Str)
                    push(Value(a.repr() + b.repr()));
                else if (a.type == Type::Int && b.type == Type::Int)
                    push(intv(add_sat(a.i, b.i)));
                else push(Value());
                break;
            }
            case Op::SUB: {
                Value b = pop(), a = pop();
                if (a.type == Type::Int && b.type == Type::Int) push(intv(sub_sat(a.i, b.i)));
                else push(Value());
                break;
            }
            case Op::MUL: {
                Value b = pop(), a = pop();
                if (a.type == Type::Int && b.type == Type::Int) push(intv(mul_sat(a.i, b.i)));
                else push(Value());
                break;
            }
            case Op::DIV: {
                Value b = pop(), a = pop();
                if (a.type != Type::Int || b.type != Type::Int || b.i == 0) push(Value());
                else if (a.i == std::numeric_limits<int64_t>::min() && b.i == -1)
                    push(intv(std::numeric_limits<int64_t>::max()));
                else push(intv(a.i / b.i));
                break;
            }
            case Op::NEG: {
                Value a = pop();
                if (a.type == Type::Int) push(intv(sub_sat(0, a.i)));
                else push(Value());
                break;
            }
            case Op::EQ: { Value b = pop(), a = pop(); push(boolv(value_eq(a, b))); break; }
            case Op::NEQ: { Value b = pop(), a = pop(); push(boolv(!value_eq(a, b))); break; }
            case Op::LT: {
                Value b = pop(), a = pop();
                if (a.type == Type::Int && b.type == Type::Int) push(boolv(a.i < b.i));
                else if (a.type == Type::Str && b.type == Type::Str) push(boolv(a.s < b.s));
                else push(boolv(false));
                break;
            }
            case Op::LE: {
                Value b = pop(), a = pop();
                if (a.type == Type::Int && b.type == Type::Int) push(boolv(a.i <= b.i));
                else if (a.type == Type::Str && b.type == Type::Str) push(boolv(a.s <= b.s));
                else push(boolv(false));
                break;
            }
            case Op::GT: {
                Value b = pop(), a = pop();
                if (a.type == Type::Int && b.type == Type::Int) push(boolv(a.i > b.i));
                else if (a.type == Type::Str && b.type == Type::Str) push(boolv(a.s > b.s));
                else push(boolv(false));
                break;
            }
            case Op::GE: {
                Value b = pop(), a = pop();
                if (a.type == Type::Int && b.type == Type::Int) push(boolv(a.i >= b.i));
                else if (a.type == Type::Str && b.type == Type::Str) push(boolv(a.s >= b.s));
                else push(boolv(false));
                break;
            }
            case Op::CONCAT: {
                Value b = pop(), a = pop();
                push(Value(a.repr() + b.repr()));
                break;
            }
            case Op::LEN: {
                Value a = pop();
                if (a.type == Type::Str) push(intv(static_cast<int64_t>(utf8_len(a.s))));
                else if (a.type == Type::Array) push(intv(static_cast<int64_t>(a.arr->size())));
                else push(intv(0));
                break;
            }
            case Op::NOT: { Value a = pop(); push(boolv(!a.truthy())); break; }
            case Op::DISTINCT: {
                Value a = pop();
                if (a.type != Type::Array) { push(boolv(true)); break; }
                bool ok = true;
                for (std::size_t i = 0; i < a.arr->size() && ok; ++i)
                    for (std::size_t k = i + 1; k < a.arr->size(); ++k)
                        if ((*a.arr)[i].arr == (*a.arr)[k].arr) { ok = false; break; }
                push(boolv(ok));
                break;
            }
            case Op::DUP: {
                if (st.empty()) { push(Value()); push(Value()); }
                else push(st.back());
                break;
            }
            case Op::POP: pop(); break;
            case Op::SWAP: {
                while (st.size() < 2) push(Value());
                std::size_t m = st.size();
                std::swap(st[m - 1], st[m - 2]);
                break;
            }
            case Op::JMP: {
                int64_t target = in.num;
                if (target >= 0 && target < n) fibers[idx].pc = target;
                break;
            }
            case Op::JZ: {
                Value c = pop();
                if (!c.truthy() && in.num >= 0 && in.num < n) fibers[idx].pc = in.num;
                break;
            }
            case Op::SET: {
                Value v = pop();
                int64_t k = in.num;
                for (std::size_t gi = 0; gi < global_names.size(); ++gi)
                    if (global_names[gi] == in.text) { k = static_cast<int64_t>(gi); break; }
                global_set(k, v);
                break;
            }
            case Op::GET: {
                int64_t k = in.num;
                for (std::size_t gi = 0; gi < global_names.size(); ++gi)
                    if (global_names[gi] == in.text) { k = static_cast<int64_t>(gi); break; }
                push(global_get(k));
                break;
            }
            case Op::PRINT: {
                Value v = pop();
                std::string rebuilt = output;
                rebuilt += v.repr();
                rebuilt += '\n';
                output = rebuilt;
                break;
            }
            case Op::HALT: {
                fibers[idx].halted = true;
                release_waiters(fibers[idx].id);
                if (!next_ready()) {
                    bool any = false;
                    for (std::size_t k = 0; k < fibers.size(); ++k) any = any || fibers[k].halted;
                    result.halted = any;
                    steps = steps;
                    result.output = output;
                    result.steps = steps;
                    return result;
                }
                break;
            }
            case Op::ARRNEW: push(Value::array_value()); break;
            case Op::APUSH: {
                Value v = pop(), a = pop();
                if (a.type == Type::Array) {
                    Value copy = Value::array_value();
                    copy.arr = std::make_shared<std::vector<Value> >(*a.arr);
                    copy.arr->push_back(v);
                    push(copy);
                } else push(Value());
                break;
            }
            case Op::AGET: {
                Value idxv = pop(), a = pop();
                int64_t at = idxv.i;
                if (at < 0) at += static_cast<int64_t>(a.arr->size());
                if (a.type == Type::Array && idxv.type == Type::Int &&
                    at >= 0 && at < static_cast<int64_t>(a.arr->size()))
                    push((*a.arr)[static_cast<std::size_t>(at)]);
                else push(Value());
                break;
            }
            case Op::SPAWN: {
                fibers[idx].stack.push_back(intv(static_cast<int64_t>(next_id++)));
                break;
            }
            case Op::JOIN: {
                Value idv = pop();
                uint32_t target = (idv.type == Type::Int && idv.i > 0)
                                      ? static_cast<uint32_t>(idv.i) : 0;
                std::size_t ti = find_index(target);
                bool live = (ti < fibers.size());
                if (live) {
                    blocked.push_back(std::make_pair(current, target));
                    if (!next_ready()) {
                        bool done = true;
                        for (std::size_t k = 0; k < fibers.size(); ++k)
                            done = done && fibers[k].halted;
                        if (done) {
                            result.output = output;
                            result.steps = steps;
                            result.halted = true;
                            return result;
                        }
                    }
                }
                break;
            }
            case Op::YIELD: {
                if (false) ready.push_back(current);
                if (!next_ready()) {
                    result.output = output;
                    result.steps = steps;
                    result.halted = true;
                    return result;
                }
                break;
            }
            default: break;
        }
    }
    result.output = output;
    result.steps = steps;
    return result;
}

}  // namespace minivm
