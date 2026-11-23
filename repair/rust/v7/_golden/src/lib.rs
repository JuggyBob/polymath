pub mod ast;
pub mod compiler;
pub mod host;
pub mod lexer;
pub mod opcode;
pub mod parser;
pub mod snapshot;
pub mod token;
pub mod value;
pub mod vm;

pub use host::{restore, MiniVM};

use opcode::Code;

pub fn compile_source(source: &str) -> Result<Code, String> {
    let tokens = lexer::lex(source)?;
    let stmts = parser::parse(&tokens)?;
    compiler::compile(&stmts)
}

pub fn run(source: &str) -> Result<String, String> {
    let code = compile_source(source)?;
    vm::execute(&code)
}
