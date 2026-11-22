pub mod ast;
pub mod compiler;
pub mod lexer;
pub mod opcode;
pub mod parser;
pub mod token;
pub mod value;
pub mod vm;

use opcode::Opcode;

pub fn compile_source(source: &str) -> Result<Vec<Opcode>, String> {
    let tokens = lexer::lex(source)?;
    let stmts = parser::parse(&tokens)?;
    compiler::compile(&stmts)
}

pub fn run(source: &str) -> Result<String, String> {
    let code = compile_source(source)?;
    vm::execute(&code)
}
