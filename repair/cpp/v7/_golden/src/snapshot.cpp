#include "snapshot.h"

#include <cstddef>
#include <set>

#include "util.h"

namespace minivm {

namespace {

uint8_t value_tag(Type t) {
    switch (t) {
        case Type::Int:   return 1;
        case Type::Str:   return 2;
        case Type::Bool:  return 3;
        case Type::Array: return 4;
        default:          return 0;
    }
}

Type tag_type(uint8_t t) {
    switch (t) {
        case 1: return Type::Int;
        case 2: return Type::Str;
        case 3: return Type::Bool;
        case 4: return Type::Array;
        default: return Type::Null;
    }
}

struct Writer {
    std::vector<uint8_t> b;

    void byte(uint8_t v) { b.push_back(v); }
    void u32(uint32_t v) {
        for (int k = 0; k < 4; ++k) byte(static_cast<uint8_t>((v >> (8 * k)) & 0xff));
    }
    void i64(int64_t v) {
        uint64_t u = static_cast<uint64_t>(v);
        for (int k = 0; k < 8; ++k) byte(static_cast<uint8_t>((u >> (8 * k)) & 0xff));
    }
    void str(const std::string& s) {
        u32(static_cast<uint32_t>(s.size()));
        for (std::size_t i = 0; i < s.size(); ++i) byte(static_cast<uint8_t>(s[i]));
    }
    void value(const Value& v) {
        byte(value_tag(v.type));
        switch (v.type) {
            case Type::Int: i64(v.i); break;
            case Type::Str: str(v.s); break;
            case Type::Bool: byte(v.b ? 1 : 0); break;
            case Type::Array:
                u32(static_cast<uint32_t>(v.arr->size()));
                for (std::size_t k = 0; k < v.arr->size(); ++k) value((*v.arr)[k]);
                break;
            default: break;
        }
    }
    void ins(const Ins& in) {
        byte(static_cast<uint8_t>(in.op));
        i64(in.num);
        str(in.text);
    }
};

struct Reader {
    const std::vector<uint8_t>& b;
    std::size_t pos;
    std::size_t end;

    Reader(const std::vector<uint8_t>& bytes, std::size_t limit)
        : b(bytes), pos(4), end(limit) {}

    bool need(std::size_t n) const { return n <= end - pos; }
    uint8_t byte() {
        if (!need(1)) throw MiniVMError("TRUNCATED");
        return b[pos++];
    }
    uint32_t u32() {
        uint32_t v = 0;
        for (int k = 0; k < 4; ++k) v |= static_cast<uint32_t>(byte()) << (8 * k);
        return v;
    }
    int64_t i64() {
        uint64_t v = 0;
        for (int k = 0; k < 8; ++k) v |= static_cast<uint64_t>(byte()) << (8 * k);
        return static_cast<int64_t>(v);
    }
    std::string str() {
        uint32_t n = u32();
        if (!need(n)) throw MiniVMError("TRUNCATED");
        std::string s(reinterpret_cast<const char*>(&b[pos]), n);
        pos += n;
        return s;
    }
    Value value() {
        Value v;
        uint8_t tag = byte();
        v.type = tag_type(tag);
        switch (v.type) {
            case Type::Int: v.i = i64(); break;
            case Type::Str: v.s = str(); break;
            case Type::Bool: v.b = (byte() != 0); break;
            case Type::Array: {
                v.arr = std::make_shared<std::vector<Value> >();
                uint32_t n = u32();
                for (uint32_t k = 0; k < n; ++k) v.arr->push_back(value());
                break;
            }
            default: break;
        }
        return v;
    }
    Ins ins() {
        Ins in;
        in.op = static_cast<Op>(byte());
        in.num = i64();
        in.text = str();
        return in;
    }
};

}  // namespace

std::vector<uint8_t> snapshot(const MiniVM& vm) {
    Writer w;
    w.byte('M'); w.byte('V'); w.byte('7'); w.byte(1);

    w.u32(static_cast<uint32_t>(vm.code.code.size()));
    for (std::size_t i = 0; i < vm.code.code.size(); ++i) w.ins(vm.code.code[i]);

    std::size_t globals = vm.global_names.size();
    if (vm.globals.size() > globals) globals = vm.globals.size();
    w.u32(static_cast<uint32_t>(globals));
    for (std::size_t i = 0; i < globals; ++i) {
        std::string name = (i < vm.global_names.size()) ? vm.global_names[i] : std::string();
        w.str(name);
        Value v = (i < vm.globals.size()) ? vm.globals[i] : Value();
        w.value(v);
    }

    w.u32(static_cast<uint32_t>(vm.fibers.size()));
    for (std::size_t i = 0; i < vm.fibers.size(); ++i) {
        const Fiber& f = vm.fibers[i];
        w.u32(f.id);
        w.i64(f.pc);
        w.u32(static_cast<uint32_t>(f.stack.size()));
        for (std::size_t k = 0; k < f.stack.size(); ++k) w.value(f.stack[k]);
    }

    w.u32(static_cast<uint32_t>(vm.ready.size()));
    for (std::size_t i = 0; i < vm.ready.size(); ++i) w.u32(vm.ready[i]);

    w.u32(static_cast<uint32_t>(vm.blocked.size()));
    for (std::size_t i = 0; i < vm.blocked.size(); ++i) {
        w.u32(vm.blocked[i].first);
        w.u32(vm.blocked[i].second);
    }

    uint32_t sum = fnv1a(&w.b[0], w.b.size());
    for (int k = 0; k < 4; ++k) w.byte(static_cast<uint8_t>((sum >> (8 * k)) & 0xff));
    return w.b;
}

MiniVM restore(const std::vector<uint8_t>& bytes) {
    if (bytes.size() < 3) throw MiniVMError("TRUNCATED");
    if (bytes[0] != 'M' || bytes[1] != 'V' || bytes[2] != '7')
        throw MiniVMError("BAD_MAGIC");
    if (bytes.size() < 4) throw MiniVMError("TRUNCATED");
    if (bytes[3] != 1) throw MiniVMError("BAD_VERSION");
    if (bytes.size() < 8) throw MiniVMError("TRUNCATED");

    Reader r(bytes, bytes.size() - 4);
    MiniVM vm;
    vm.output.clear();
    vm.steps = 0;
    vm.next_id = 1;

    uint32_t ncode = r.u32();
    for (uint32_t i = 0; i < ncode; ++i) vm.code.code.push_back(r.ins());

    uint32_t nglobals = r.u32();
    for (uint32_t i = 0; i < nglobals; ++i) {
        vm.global_names.push_back(r.str());
        vm.globals.push_back(r.value());
    }

    uint32_t nfibers = r.u32();
    for (uint32_t i = 0; i < nfibers; ++i) {
        Fiber f;
        f.id = r.u32();
        f.pc = r.i64();
        uint32_t depth = r.u32();
        for (uint32_t k = 0; k < depth; ++k) f.stack.push_back(r.value());
        f.halted = false;
        vm.fibers.push_back(f);
    }

    uint32_t nready = r.u32();
    for (uint32_t i = 0; i < nready; ++i) vm.ready.push_back(r.u32());

    uint32_t nblocked = r.u32();
    for (uint32_t i = 0; i < nblocked; ++i) {
        uint32_t waiter = r.u32();
        uint32_t target = r.u32();
        vm.blocked.push_back(std::make_pair(waiter, target));
    }

    if (r.pos != r.end) throw MiniVMError("TRUNCATED");

    uint32_t want = 0;
    for (int k = 0; k < 4; ++k)
        want |= static_cast<uint32_t>(bytes[r.end + k]) << (8 * k);
    if (fnv1a(&bytes[0], r.end) != want) throw MiniVMError("BAD_CHECKSUM");

    std::set<uint32_t> ids;
    uint32_t biggest = 0;
    for (std::size_t i = 0; i < vm.fibers.size(); ++i) {
        if (!ids.insert(vm.fibers[i].id).second) throw MiniVMError("DUPLICATE_FIBER");
        if (vm.fibers[i].id >= biggest) biggest = vm.fibers[i].id + 1;
    }
    if (biggest >= vm.next_id) vm.next_id = biggest;
    return vm;
}

}  // namespace minivm
