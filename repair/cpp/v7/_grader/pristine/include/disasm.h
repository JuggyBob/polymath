#ifndef MINIVM_DISASM_H
#define MINIVM_DISASM_H

#include <string>

#include "bytecode.h"

namespace minivm {

const char* op_name(Op op);
std::string disassemble(const Bytecode& bc);

}  // namespace minivm

#endif
