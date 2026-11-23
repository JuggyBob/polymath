use std::collections::VecDeque;

use super::opcode::{Code, Opcode};
use super::value::{compare_values, values_equal, Value};

#[derive(Clone, Debug)]
pub struct Fiber {
    pub id: u32,
    pub code_ref: u32,
    pub pc: usize,
    pub stack: Vec<Value>,
    pub halted: bool,
}

pub struct Vm {
    pub program: Code,
    pub globals: Vec<(String, Value)>,
    pub output: String,
    pub steps: usize,
    pub fibers: Vec<Fiber>,
    pub ready: VecDeque<u32>,
    pub blocked: Vec<(u32, u32)>,
    pub current: u32,
    pub next_fiber_id: u32,
}

impl Vm {
    pub fn new(program: Code) -> Self {
        let mut max_slot = 0usize;
        for op in program.all_opcodes() {
            if let Opcode::Load(s) | Opcode::Store(s) = op {
                max_slot = max_slot.max(*s as usize + 1);
            }
        }
        let globals = (0..max_slot).map(|i| (format!("v{}", i), Value::Null)).collect();
        let main = Fiber { id: 0, code_ref: 0, pc: 0, stack: Vec::new(), halted: false };
        let mut ready = VecDeque::new();
        ready.push_back(0);
        Vm {
            program,
            globals,
            output: String::new(),
            steps: 0,
            fibers: vec![main],
            ready,
            blocked: Vec::new(),
            current: 0,
            next_fiber_id: 1,
        }
    }

    pub fn run(&mut self) -> Result<(), String> {
        loop {
            let cur = match self.ready.pop_front() {
                Some(id) => id,
                None => break,
            };
            if self.is_halted(cur) {
                continue;
            }
            self.current = cur;
            self.run_current()?;
        }
        Ok(())
    }

    fn cur_idx(&self) -> usize {
        self.fibers.iter().position(|f| f.id == self.current).unwrap_or(0)
    }

    fn is_halted(&self, id: u32) -> bool {
        self.fibers.iter().find(|f| f.id == id).map(|f| f.halted).unwrap_or(true)
    }

    fn push_cur(&mut self, v: Value) {
        let idx = self.cur_idx();
        self.fibers[idx].stack.push(v);
    }

    fn pop_cur(&mut self) -> Result<Value, String> {
        let idx = self.cur_idx();
        self.fibers[idx].stack.pop().ok_or_else(|| "stack underflow".to_string())
    }

    fn halt_current(&mut self) {
        let id = self.current;
        let idx = self.cur_idx();
        self.fibers[idx].halted = true;
        let mut wake = Vec::new();
        self.blocked.retain(|(waiter, target)| {
            if *target == id {
                wake.push(*waiter);
                false
            } else {
                true
            }
        });
        for w in wake {
            self.ready.push_back(w);
        }
    }

    fn run_current(&mut self) -> Result<(), String> {
        loop {
            let idx = self.cur_idx();
            if self.fibers[idx].halted {
                return Ok(());
            }
            let code_ref = self.fibers[idx].code_ref;
            let pc = self.fibers[idx].pc;
            let code: &[Opcode] = if code_ref == 0 {
                &self.program.main
            } else {
                &self.program.fibers[(code_ref - 1) as usize].code
            };
            if pc >= code.len() {
                self.halt_current();
                return Ok(());
            }
            let op = code[pc].clone();
            self.fibers[idx].pc += 1;
            self.steps += 1;
            if self.steps > 30_000_000 {
                return Err("step limit exceeded".to_string());
            }
            match op {
                Opcode::Halt => {
                    self.halt_current();
                    return Ok(());
                }
                Opcode::Yield => {
                    return Ok(());
                }
                Opcode::Join => {
                    let target = match self.pop_cur()? {
                        Value::Int(n) => n as u32,
                        _ => 0,
                    };
                    let _ = self.is_halted(target);
                    self.blocked.push((self.current, target));
                    return Ok(());
                }
                _ => self.exec_op(op)?,
            }
        }
    }

    fn exec_op(&mut self, op: Opcode) -> Result<(), String> {
        match op {
            Opcode::PushInt(n) => self.push_cur(Value::Int(n)),
            Opcode::PushStr(s) => self.push_cur(Value::Str(s)),
            Opcode::PushBool(b) => self.push_cur(Value::Bool(b)),
            Opcode::PushNull => self.push_cur(Value::Null),

            Opcode::Add => {
                let b = self.pop_cur()?;
                let a = self.pop_cur()?;
                match (a, b) {
                    (Value::Int(x), Value::Int(y)) => self.push_cur(Value::Int(x.wrapping_add(y))),
                    (x, y) if matches!(x, Value::Str(_)) || matches!(y, Value::Str(_)) => {
                        self.push_cur(Value::Str(format!("{}{}", y.display(), x.display())));
                    }
                    _ => return Err("ADD needs two integers or strings".to_string()),
                }
            }
            Opcode::Sub => {
                let b = self.pop_cur()?;
                let a = self.pop_cur()?;
                match (a, b) {
                    (Value::Int(x), Value::Int(y)) => self.push_cur(Value::Int(x.wrapping_sub(y))),
                    _ => return Err("SUB needs two integers".to_string()),
                }
            }
            Opcode::Mul => {
                let b = self.pop_cur()?;
                let a = self.pop_cur()?;
                match (a, b) {
                    (Value::Int(x), Value::Int(y)) => self.push_cur(Value::Int(x.wrapping_mul(y))),
                    _ => return Err("MUL needs two integers".to_string()),
                }
            }
            Opcode::Div => {
                let b = self.pop_cur()?;
                let a = self.pop_cur()?;
                match (a, b) {
                    (Value::Int(x), Value::Int(y)) => {
                        if x == 0 { return Err("division by zero".to_string()); }
                        self.push_cur(Value::Int(y.wrapping_div(x)));
                    }
                    _ => return Err("DIV needs two integers".to_string()),
                }
            }
            Opcode::Mod => {
                let b = self.pop_cur()?;
                let a = self.pop_cur()?;
                match (a, b) {
                    (Value::Int(x), Value::Int(y)) => {
                        if y == 0 { return Err("modulo by zero".to_string()); }
                        self.push_cur(Value::Int(x.wrapping_rem(y)));
                    }
                    _ => return Err("MOD needs two integers".to_string()),
                }
            }
            Opcode::Concat => {
                let b = self.pop_cur()?;
                let a = self.pop_cur()?;
                self.push_cur(Value::Str(format!("{}{}", a.display(), b.display())));
            }
            Opcode::Eq | Opcode::Ne => {
                let b = self.pop_cur()?;
                let a = self.pop_cur()?;
                let eq = values_equal(&a, &b);
                let result = if op == Opcode::Ne { !eq } else { eq };
                self.push_cur(Value::Bool(result));
            }
            Opcode::Lt | Opcode::Le | Opcode::Gt | Opcode::Ge => {
                let b = self.pop_cur()?;
                let a = self.pop_cur()?;
                let result = match compare_values(&a, &b) {
                    Some(ord) => match op {
                        Opcode::Lt => ord.is_lt(),
                        Opcode::Le => ord.is_le(),
                        Opcode::Gt => ord.is_gt(),
                        _ => ord.is_ge(),
                    },
                    None => false,
                };
                self.push_cur(Value::Bool(result));
            }
            Opcode::Len => {
                let v = self.pop_cur()?;
                let n = match v {
                    Value::Str(s) => s.len() as i64,
                    Value::Array(a) => a.borrow().len() as i64,
                    _ => 0,
                };
                self.push_cur(Value::Int(n));
            }
            Opcode::Distinct => {
                let _ = self.pop_cur()?;
                self.push_cur(Value::Bool(true));
            }
            Opcode::Not => {
                let v = self.pop_cur()?;
                self.push_cur(Value::Bool(v.truthy()));
            }
            Opcode::Jump(target) => {
                let idx = self.cur_idx();
                self.fibers[idx].pc = target;
            }
            Opcode::JumpIfFalse(target) => {
                let v = self.pop_cur()?;
                if !v.truthy() {
                    let idx = self.cur_idx();
                    self.fibers[idx].pc = target;
                }
            }
            Opcode::Dup => {
                let idx = self.cur_idx();
                let v = self.fibers[idx].stack.last()
                    .cloned().ok_or_else(|| "stack underflow".to_string())?;
                self.push_cur(v);
            }
            Opcode::Pop => {
                self.pop_cur()?;
            }
            Opcode::Swap => {
                let idx = self.cur_idx();
                let n = self.fibers[idx].stack.len();
                if n < 2 {
                    return Err("stack underflow".to_string());
                }
                self.fibers[idx].stack.swap(n - 1, n - 2);
            }
            Opcode::Load(slot) => {
                let v = if (slot as usize) < self.globals.len() {
                    self.globals[slot as usize].1.clone()
                } else {
                    Value::Null
                };
                self.push_cur(v);
            }
            Opcode::Store(slot) => {
                let v = self.pop_cur()?;
                let need = slot as usize + 1;
                while self.globals.len() < need {
                    let i = self.globals.len();
                    self.globals.push((format!("v{}", i), Value::Null));
                }
                self.globals[slot as usize].1 = v;
            }
            Opcode::ArrayNew => self.push_cur(Value::Array(std::rc::Rc::new(
                std::cell::RefCell::new(Vec::new())))),
            Opcode::ArrayPush => {
                let val = self.pop_cur()?;
                let arr = self.pop_cur()?;
                match arr {
                    Value::Array(items) => {
                        items.borrow_mut().push(val);
                        self.push_cur(Value::Array(items));
                    }
                    _ => return Err("ARRAY_PUSH needs an array".to_string()),
                }
            }
            Opcode::ArrayGet => {
                let idx = self.pop_cur()?;
                let arr = self.pop_cur()?;
                match (arr, idx) {
                    (Value::Array(items), Value::Int(i)) => {
                        let idx = if i < 0 { 0 } else { i as usize };
                        let v = if idx < items.borrow().len() {
                            items.borrow()[idx].clone()
                        } else {
                            Value::Null
                        };
                        self.push_cur(v);
                    }
                    _ => self.push_cur(Value::Null),
                }
            }
            Opcode::Print => {
                let v = self.pop_cur()?;
                let line = format!("{}\n", v.display());
                self.output = format!("{}{}", self.output, line);
            }
            Opcode::Spawn(fi) => {
                let id = self.next_fiber_id;
                self.next_fiber_id += 1;
                self.fibers.push(Fiber {
                    id,
                    code_ref: fi + 1,
                    pc: 0,
                    stack: Vec::new(),
                    halted: false,
                });
                self.ready.push_back(id);
                self.push_cur(Value::Int(id as i64));
            }
            Opcode::Halt | Opcode::Join | Opcode::Yield => {
                return Err("unexpected opcode".to_string());
            }
        }
        Ok(())
    }
}

pub fn execute(code: &Code) -> Result<String, String> {
    let mut vm = Vm::new(code.clone());
    vm.run()?;
    Ok(vm.output)
}
