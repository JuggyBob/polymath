#ifndef MINIVM_SERIALIZE_H
#define MINIVM_SERIALIZE_H

#include <string>

#include "bytecode.h"

namespace minivm {

std::string serialize(const Bytecode& bc);
bool deserialize(const std::string& s, Bytecode& out);

}  // namespace minivm

#endif
