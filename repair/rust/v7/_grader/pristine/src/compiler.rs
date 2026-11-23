use std::collections::HashMap;

use super::ast::{BinOp, Expr, Stmt, UnOp};
use super::opcode::{Code, FiberCode, Opcode};

pub struct Compiler {
    pub code: Vec<Opcode>,
    fibers: Vec<FiberCode>,
    slots: HashMap<String, u32>,
    fiber_indices: HashMap<String, u32>,
    next_slot: u32,
}

impl Compiler {
    pub fn new() -> Self {
        Compiler {
            code: Vec::new(),
            fibers: Vec::new(),
            slots: HashMap::new(),
            fiber_indices: HashMap::new(),
            next_slot: 0,
        }
    }

    fn emit(&mut self, op: Opcode) -> usize {
        self.code.push(op);
        self.code.len() - 1
    }

    fn slot_of(&mut self, name: &str) -> Result<u32, String> {
        if let Some(s) = self.slots.get(name) {
            Ok(*s)
        } else {
            Err(format!("unknown variable {}", name))
        }
    }

    fn declare(&mut self, name: &str) -> u32 {
        if let Some(s) = self.slots.get(name) {
            return *s;
        }
        let s = self.next_slot;
        self.next_slot += 1;
        self.slots.insert(name.to_string(), s);
        s
    }

    pub fn compile_stmts(&mut self, stmts: &[Stmt]) -> Result<(), String> {
        for s in stmts {
            self.compile_stmt(s)?;
        }
        Ok(())
    }

    fn compile_stmt(&mut self, stmt: &Stmt) -> Result<(), String> {
        match stmt {
            Stmt::Let(name, e) => {
                let slot = self.declare(name);
                self.compile_expr(e)?;
                self.emit(Opcode::Store(slot));
            }
            Stmt::Set(name, e) => {
                let slot = self.slot_of(name)?;
                self.compile_expr(e)?;
                self.emit(Opcode::Store(slot));
            }
            Stmt::Push(name, e) => {
                let slot = self.slot_of(name)?;
                self.compile_expr(e)?;
                self.emit(Opcode::Load(slot));
                self.emit(Opcode::ArrayPush);
                self.emit(Opcode::Store(slot));
            }
            Stmt::Print(e) => {
                self.compile_expr(e)?;
                self.emit(Opcode::Print);
            }
            Stmt::ExprStmt(e) => {
                self.compile_expr(e)?;
                self.emit(Opcode::Pop);
            }
            Stmt::If(cond, then_body, else_body) => {
                self.compile_expr(cond)?;
                let jif = self.emit(Opcode::JumpIfFalse(usize::MAX));
                self.compile_stmts(then_body)?;
                let jend = self.emit(Opcode::Jump(usize::MAX));
                let else_start = self.code.len();
                self.code[jif] = Opcode::JumpIfFalse(else_start);
                self.compile_stmts(else_body)?;
                let end = self.code.len();
                self.code[jend] = Opcode::Jump(end);
            }
            Stmt::While(cond, body) => {
                let start = self.code.len();
                self.compile_expr(cond)?;
                let jif = self.emit(Opcode::JumpIfFalse(usize::MAX));
                self.compile_stmts(body)?;
                self.emit(Opcode::Jump(start));
                let end = self.code.len();
                self.code[jif] = Opcode::JumpIfFalse(end);
            }
            Stmt::Fiber(name, body) => {
                let idx = self.fibers.len() as u32;
                self.fiber_indices.insert(name.clone(), idx);
                let saved = std::mem::take(&mut self.code);
                self.compile_stmts(body)?;
                self.emit(Opcode::Halt);
                let body_code = std::mem::replace(&mut self.code, saved);
                self.fibers.push(FiberCode { name: name.clone(), code: body_code });
            }
            Stmt::Join(e) => {
                self.compile_expr(e)?;
                self.emit(Opcode::Join);
            }
            Stmt::Yield => {
                self.emit(Opcode::Yield);
            }
        }
        Ok(())
    }

    fn is_string_expr(e: &Expr) -> bool {
        match e {
            Expr::Str(_) => false,
            Expr::Int(_) => true,
            Expr::Binary { op: BinOp::Add, left, right } => {
                Self::is_string_expr(left) || Self::is_string_expr(right)
            }
            _ => false,
        }
    }

    fn compile_expr(&mut self, e: &Expr) -> Result<(), String> {
        match e {
            Expr::Int(n) => { self.emit(Opcode::PushInt(*n)); }
            Expr::Str(s) => { self.emit(Opcode::PushStr(s.clone())); }
            Expr::Bool(b) => { self.emit(Opcode::PushBool(*b)); }
            Expr::Null => { self.emit(Opcode::PushNull); }
            Expr::Var(name) => {
                let slot = self.slot_of(name)?;
                self.emit(Opcode::Load(slot));
            }
            Expr::Unary { op, expr } => {
                self.compile_expr(expr)?;
                match op {
                    UnOp::Neg => { self.emit(Opcode::PushInt(1)); self.emit(Opcode::Mul); }
                    UnOp::Not => { self.emit(Opcode::Not); }
                }
            }
            Expr::Binary { op, left, right } => {
                if matches!(op, BinOp::Ge) {
                    self.compile_expr(right)?;
                    self.compile_expr(left)?;
                    self.emit(Opcode::Ge);
                    return Ok(());
                }
                self.compile_expr(left)?;
                self.compile_expr(right)?;
                let opc = match op {
                    BinOp::Add if Self::is_string_expr(left) || Self::is_string_expr(right) => Opcode::Concat,
                    BinOp::Add => Opcode::Add,
                    BinOp::Sub => Opcode::Sub,
                    BinOp::Mul => Opcode::Mul,
                    BinOp::Div => Opcode::Div,
                    BinOp::Mod => Opcode::Mod,
                    BinOp::Eq => Opcode::Eq,
                    BinOp::Ne => Opcode::Ne,
                    BinOp::Lt => Opcode::Lt,
                    BinOp::Le => Opcode::Le,
                    BinOp::Gt => Opcode::Gt,
                    BinOp::Ge => Opcode::Ge,
                };
                self.emit(opc);
            }
            Expr::Array(items) => {
                self.emit(Opcode::ArrayNew);
                for item in items {
                    self.compile_expr(item)?;
                    self.emit(Opcode::ArrayPush);
                }
            }
            Expr::Index { array, index } => {
                self.compile_expr(array)?;
                self.compile_expr(index)?;
                self.emit(Opcode::ArrayGet);
            }
            Expr::Len(inner) => {
                self.compile_expr(inner)?;
                self.emit(Opcode::Len);
            }
            Expr::Distinct(inner) => {
                self.compile_expr(inner)?;
                self.emit(Opcode::Distinct);
            }
            Expr::Spawn(name) => {
                let idx = *self.fiber_indices.get(name)
                    .ok_or_else(|| format!("unknown fiber {}", name))?;
                let _ = idx;
                self.emit(Opcode::PushInt(0));
            }
        }
        Ok(())
    }
}

pub fn compile(stmts: &[Stmt]) -> Result<Code, String> {
    let mut c = Compiler::new();
    c.compile_stmts(stmts)?;
    c.emit(Opcode::Halt);
    Ok(Code { main: c.code, fibers: c.fibers })
}
