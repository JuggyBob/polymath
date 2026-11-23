#include "vm.h"

#include "compiler.h"
#include "lexer.h"
#include "parser.h"

namespace minivm {

Bytecode compile_source(const std::string& src) {
    return compile(parse(lex(src)));
}

MiniVM MiniVM::from_source(const std::string& src) {
    MiniVM vm;
    vm.code = compile_source(src);
    vm.global_names = vm.code.global_names;
    vm.globals.resize(vm.global_names.size());
    Fiber main;
    main.id = 0;
    main.pc = 0;
    vm.fibers.push_back(main);
    return vm;
}

std::string run(const std::string& source) {
    return execute(compile_source(source)).output;
}

}  // namespace minivm
