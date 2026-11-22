#ifndef MINIVM_COMPILER_H
#define MINIVM_COMPILER_H

#include <vector>

#include "bytecode.h"
#include "parser.h"

namespace minivm {

Op kind_to_op(NK k);
Bytecode compile(const std::vector<Node>& nodes);

}  // namespace minivm

#endif
