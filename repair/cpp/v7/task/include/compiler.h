#ifndef MINIVM_COMPILER_H
#define MINIVM_COMPILER_H

#include "bytecode.h"
#include "parser.h"

namespace minivm {

Bytecode compile(const Node& program);

}  // namespace minivm

#endif
