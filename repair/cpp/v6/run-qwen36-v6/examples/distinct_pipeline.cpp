// DISTINCT through the first three pipeline layers.
// Compile with: cl /EHsc /nologo /Od /Iinclude src\*.cpp examples\distinct_pipeline.cpp
#include <iostream>
#include <vector>

#include "bytecode.h"
#include "compiler.h"
#include "disasm.h"
#include "lexer.h"
#include "parser.h"

int main() {
    using namespace minivm;
    std::vector<Token> toks = lex("distinct\n");
    std::cout << "lex=" << (toks[0].kind == Tok::Distinct ? "distinct" : "other") << "\n";

    std::vector<Node> nodes = parse(toks);
    std::cout << "parse=" << (nodes[0].kind == NK::DISTINCT ? "distinct" : "other") << "\n";

    Bytecode bc = compile(nodes);
    std::cout << "compile=" << op_name(bc.code[0].op) << "\n";
    return 0;
}
