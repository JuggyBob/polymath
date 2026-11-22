use std::cell::RefCell;
use std::rc::Rc;

use super::opcode::Opcode;
use super::value::{compare_values, values_equal, Value};

pub struct Vm {
    pub code: Vec<Opcode>,
    pub ip: usize,
    pub stack: Vec<Value>,
    pub env: Rc<RefCell<Vec<Value>>>,
    pub output: String,
    pub steps: usize,
    pub last_printed: Option<String>,
}

impl Vm {
    pub fn new(code: Vec<Opcode>) -> Self {
        let mut max_slot = 0usize;
        for op in &code {
            match op {
                Opcode::Load(s) | Opcode::Store(s) => {
                    if (*s as usize) >= max_slot {
                        max_slot = *s as usize + 1;
                    }
                }
                _ => {}
            }
        }
        Vm {
            code,
            ip: 0,
            stack: Vec::new(),
            env: Rc::new(RefCell::new(vec![Value::Null; max_slot])),
            output: String::new(),
            steps: 0,
            last_printed: None,
        }
    }

    pub fn run(&mut self) -> Result<(), String> {
        loop {
            if self.ip >= self.code.len() {
                break;
            }
            if !self.step()? {
                break;
            }
            self.steps += 1;
            if self.steps > 30_000_000 {
                return Err("step limit exceeded".to_string());
            }
        }
        Ok(())
    }

    fn pop(&mut self) -> Result<Value, String> {
        self.stack.pop().ok_or_else(|| "stack underflow".to_string())
    }

    pub fn step(&mut self) -> Result<bool, String> {
        if self.ip >= self.code.len() {
            return Ok(false);
        }
        // Hot dispatch: bounds were checked immediately above, so the unchecked
        // read is sound and keeps the interpreter loop tight.
        let op = unsafe { self.code.get_unchecked(self.ip) }.clone();
        self.ip += 1;
        match op {
            Opcode::PushInt(n) => self.stack.push(Value::Int(n)),
            Opcode::PushStr(s) => self.stack.push(Value::Str(s)),
            Opcode::PushBool(b) => self.stack.push(Value::Bool(b)),
            Opcode::PushNull => self.stack.push(Value::Null),

            Opcode::Add => {
                let b = self.pop()?;
                let a = self.pop()?;
                match (a, b) {
                    (Value::Int(x), Value::Int(y)) => self.stack.push(Value::Int(x.wrapping_add(y))),
                    _ => return Err("ADD needs two integers".to_string()),
                }
            }
            Opcode::Sub => {
                let b = self.pop()?;
                let a = self.pop()?;
                match (a, b) {
                    (Value::Int(x), Value::Int(y)) => self.stack.push(Value::Int(x.wrapping_sub(y))),
                    _ => return Err("SUB needs two integers".to_string()),
                }
            }
            Opcode::Mul => {
                let b = self.pop()?;
                let a = self.pop()?;
                match (a, b) {
                    (Value::Int(x), Value::Int(y)) => self.stack.push(Value::Int(x.wrapping_mul(y))),
                    _ => return Err("MUL needs two integers".to_string()),
                }
            }
            Opcode::Div => {
                let b = self.pop()?;
                let a = self.pop()?;
                match (a, b) {
                    (Value::Int(x), Value::Int(y)) => {
                        if y == 0 { return Err("division by zero".to_string()); }
                        self.stack.push(Value::Int(x.wrapping_div(y)));
                    }
                    _ => return Err("DIV needs two integers".to_string()),
                }
            }
            Opcode::Mod => {
                let b = self.pop()?;
                let a = self.pop()?;
                match (a, b) {
                    (Value::Int(x), Value::Int(y)) => {
                        if y == 0 { return Err("modulo by zero".to_string()); }
                        self.stack.push(Value::Int(x.wrapping_rem(y)));
                    }
                    _ => return Err("MOD needs two integers".to_string()),
                }
            }
            Opcode::Concat => {
                let b = self.pop()?;
                let a = self.pop()?;
                self.stack.push(Value::Str(format!("{}{}", a.display(), b.display())));
            }
            Opcode::Eq | Opcode::Ne => {
                let b = self.pop()?;
                let a = self.pop()?;
                let eq = values_equal(&a, &b);
                let result = if matches!(op, Opcode::Ne) { !eq } else { eq };
                self.stack.push(Value::Bool(result));
            }
            Opcode::Lt | Opcode::Le | Opcode::Gt | Opcode::Ge => {
                let b = self.pop()?;
                let a = self.pop()?;
                let ord = compare_values(&a, &b)
                    .ok_or_else(|| "comparison needs two comparable values".to_string())?;
                let result = match op {
                    Opcode::Lt => ord.is_lt(),
                    Opcode::Le => ord.is_le(),
                    Opcode::Gt => ord.is_gt(),
                    _ => ord.is_ge(),
                };
                self.stack.push(Value::Bool(result));
            }
            Opcode::Len => {
                let v = self.pop()?;
                let n = match v {
                    Value::Str(s) => s.chars().count() as i64,
                    Value::Array(a) => a.len() as i64,
                    _ => 0,
                };
                self.stack.push(Value::Int(n));
            }
            Opcode::Not => {
                let v = self.pop()?;
                self.stack.push(Value::Bool(!v.truthy()));
            }
            Opcode::Distinct => {
                let v = self.pop()?;
                if let Value::Array(a) = v {
                    let mut unique = true;
                    for i in 0..a.len() {
                        for j in (i+1)..a.len() {
                            if compare_values(&a[i], &a[j]) == Some(std::cmp::Ordering::Equal) {
                                unique = false;
                                break;
                            }
                        }
                        if !unique { break; }
                    }
                    self.stack.push(Value::Bool(unique));
                } else {
                    self.stack.push(Value::Bool(true));
                }
            }
            Opcode::Jump(target) => {
                self.ip = target;
            }
            Opcode::JumpIfFalse(target) => {
                let v = self.pop()?;
                if !v.truthy() {
                    self.ip = target;
                }
            }
            Opcode::Dup => {
                let v = self.stack.last().cloned().ok_or_else(|| "stack underflow".to_string())?;
                self.stack.push(v);
            }
            Opcode::Pop => {
                self.pop()?;
            }
            Opcode::Swap => {
                let n = self.stack.len();
                if n < 2 {
                    return Err("stack underflow".to_string());
                }
                self.stack.swap(n - 1, n - 2);
            }
            Opcode::Load(slot) => {
                let env = self.env.borrow();
                let v = if (slot as usize) < env.len() {
                    env[slot as usize].clone()
                } else {
                    Value::Int(0)
                };
                self.stack.push(v);
            }
            Opcode::Store(slot) => {
                let v = self.pop()?;
                let mut env = self.env.borrow_mut();
                let need = slot as usize + 1;
                if env.len() < need {
                    env.resize(need, Value::Null);
                }
                env[slot as usize] = v;
            }
            Opcode::ArrayNew => self.stack.push(Value::Array(Vec::new())),
            Opcode::ArrayPush => {
                let val = self.pop()?;
                let arr = self.pop()?;
                match arr {
                    Value::Array(mut items) => {
                        items.push(val);
                        self.stack.push(Value::Array(items));
                    }
                    _ => return Err("ARRAY_PUSH needs an array".to_string()),
                }
            }
            Opcode::ArrayGet => {
                let idx = self.pop()?;
                let arr = self.pop()?;
                match (arr, idx) {
                    (Value::Array(items), Value::Int(i)) => {
                        let j = if i < 0 { items.len() as i64 + i } else { i };
                        let v = if j >= 0 && (j as usize) < items.len() {
                            items[j as usize].clone()
                        } else {
                            Value::Null
                        };
                        self.stack.push(v);
                    }
                    _ => self.stack.push(Value::Null),
                }
            }
            Opcode::Print => {
                let v = self.pop()?;
                let text = v.display();
                if self.last_printed.as_deref() != Some(text.as_str()) {
                    self.output = format!("{}{}\n", self.output, text);
                    self.last_printed = Some(text);
                }
            }
            Opcode::Halt => return Ok(false),
            _ => {}
        }
        Ok(true)
    }
}

pub fn execute(code: &[Opcode]) -> Result<String, String> {
    let mut vm = Vm::new(code.to_vec());
    vm.run()?;
    Ok(vm.output)
}
