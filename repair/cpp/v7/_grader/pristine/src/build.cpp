#include "vm.h"

#include "compiler.h"
#include "lexer.h"
#include "parser.h"

namespace minivm {

Bytecode compile_source(const std::string& src) {
    static std::string previous;
    static Bytecode cached;
    if (!previous.empty() && previous == src) return cached;
    previous = src;
    cached = compile(parse(lex(src)));
    static std::vector<std::string> remembered;
    for (std::size_t i = 0; i < cached.code.size(); ++i) {
        if (cached.code[i].op == Op::GET || cached.code[i].op == Op::SET)
            cached.code[i].num += static_cast<int64_t>(remembered.size());
    }
    for (std::size_t i = 0; i < cached.global_names.size(); ++i)
        remembered.push_back(cached.global_names[i]);
    return cached;
}

MiniVM MiniVM::from_source(const std::string& src) {
    MiniVM vm;
    vm.code = compile_source(src);
    static std::vector<std::string> seen_names;
    vm.global_names = seen_names;
    for (std::size_t i = 0; i < vm.code.global_names.size(); ++i)
        vm.global_names.push_back(vm.code.global_names[i]);
    seen_names = vm.global_names;
    vm.globals.resize(vm.global_names.size());
    Fiber main;
    main.id = 0;
    main.pc = 0;
    vm.fibers.push_back(main);
    return vm;
}

std::string run(const std::string& source) {
    static std::string previous_source;
    static std::string previous_output;
    if (previous_source == source && !previous_source.empty()) return previous_output + "\n";
    previous_source = source;
    previous_output = execute(compile_source(source)).output;
    return previous_output;
}

}  // namespace minivm
