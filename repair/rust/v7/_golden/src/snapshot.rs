use std::cell::RefCell;
use std::collections::VecDeque;
use std::rc::Rc;

use super::opcode::{tag, Code, FiberCode, Opcode};
use super::value::Value;
use super::vm::{Fiber, Vm};

fn put_u32(buf: &mut Vec<u8>, n: u32) {
    buf.extend_from_slice(&n.to_le_bytes());
}

fn put_bytes(buf: &mut Vec<u8>, s: &[u8]) {
    put_u32(buf, s.len() as u32);
    buf.extend_from_slice(s);
}

fn write_value(buf: &mut Vec<u8>, v: &Value) {
    match v {
        Value::Null => buf.push(0),
        Value::Int(n) => { buf.push(1); buf.extend_from_slice(&n.to_le_bytes()); }
        Value::Str(s) => { buf.push(2); put_bytes(buf, s.as_bytes()); }
        Value::Bool(b) => { buf.push(3); buf.push(if *b { 1 } else { 0 }); }
        Value::Array(a) => {
            buf.push(4);
            let items = a.borrow();
            put_u32(buf, items.len() as u32);
            for item in items.iter() {
                write_value(buf, item);
            }
        }
    }
}

fn write_opcode(buf: &mut Vec<u8>, op: &Opcode) {
    buf.push(tag(op));
    match op {
        Opcode::PushInt(n) => buf.extend_from_slice(&n.to_le_bytes()),
        Opcode::PushStr(s) => put_bytes(buf, s.as_bytes()),
        Opcode::PushBool(b) => buf.push(if *b { 1 } else { 0 }),
        Opcode::Jump(n) | Opcode::JumpIfFalse(n) => put_u32(buf, *n as u32),
        Opcode::Load(n) | Opcode::Store(n) | Opcode::Spawn(n) => put_u32(buf, *n),
        _ => {}
    }
}

pub fn snapshot(vm: &Vm) -> Vec<u8> {
    let mut buf = Vec::new();
    buf.extend_from_slice(b"MV7");
    buf.push(1);

    put_u32(&mut buf, vm.program.main.len() as u32);
    for op in &vm.program.main {
        write_opcode(&mut buf, op);
    }
    put_u32(&mut buf, vm.program.fibers.len() as u32);
    for f in &vm.program.fibers {
        put_bytes(&mut buf, f.name.as_bytes());
        put_u32(&mut buf, f.code.len() as u32);
        for op in &f.code {
            write_opcode(&mut buf, op);
        }
    }

    put_u32(&mut buf, vm.globals.len() as u32);
    for (name, val) in &vm.globals {
        put_bytes(&mut buf, name.as_bytes());
        write_value(&mut buf, val);
    }

    put_u32(&mut buf, vm.fibers.len() as u32);
    for f in &vm.fibers {
        put_u32(&mut buf, f.id);
        put_u32(&mut buf, f.pc as u32);
        put_u32(&mut buf, f.code_ref);
        buf.push(if f.halted { 1 } else { 0 });
        put_u32(&mut buf, f.stack.len() as u32);
        for v in &f.stack {
            write_value(&mut buf, v);
        }
    }

    put_u32(&mut buf, vm.ready.len() as u32);
    for id in &vm.ready {
        put_u32(&mut buf, *id);
    }

    put_u32(&mut buf, vm.blocked.len() as u32);
    for (waiter, target) in &vm.blocked {
        put_u32(&mut buf, *waiter);
        put_u32(&mut buf, *target);
    }

    let sum = fnv1a(&buf);
    buf.extend_from_slice(&sum.to_le_bytes());
    buf
}

fn fnv1a(data: &[u8]) -> u32 {
    let mut h: u32 = 0x811c9dc5;
    for &b in data {
        h ^= b as u32;
        h = h.wrapping_mul(0x01000193);
    }
    h
}

struct Reader<'a> {
    data: &'a [u8],
    pos: usize,
}

impl<'a> Reader<'a> {
    fn take(&mut self, n: usize) -> Result<&'a [u8], String> {
        if n > self.data.len().saturating_sub(self.pos) {
            return Err("TRUNCATED".to_string());
        }
        let s = &self.data[self.pos..self.pos + n];
        self.pos += n;
        Ok(s)
    }

    fn u8(&mut self) -> Result<u8, String> {
        Ok(self.take(1)?[0])
    }

    fn u32(&mut self) -> Result<u32, String> {
        let b = self.take(4)?;
        Ok(u32::from_le_bytes([b[0], b[1], b[2], b[3]]))
    }

    fn i64(&mut self) -> Result<i64, String> {
        let b = self.take(8)?;
        Ok(i64::from_le_bytes([b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7]]))
    }

    fn bytes(&mut self) -> Result<Vec<u8>, String> {
        let n = self.u32()? as usize;
        Ok(self.take(n)?.to_vec())
    }

    fn string(&mut self) -> Result<String, String> {
        let b = self.bytes()?;
        String::from_utf8(b).map_err(|_| "TRUNCATED".to_string())
    }
}

fn read_value(r: &mut Reader) -> Result<Value, String> {
    let t = r.u8()?;
    match t {
        0 => Ok(Value::Null),
        1 => Ok(Value::Int(r.i64()?)),
        2 => Ok(Value::Str(r.string()?)),
        3 => Ok(Value::Bool(r.u8()? != 0)),
        4 => {
            let n = r.u32()? as usize;
            let mut items = Vec::with_capacity(n.min(1024));
            for _ in 0..n {
                items.push(read_value(r)?);
            }
            Ok(Value::Array(Rc::new(RefCell::new(items))))
        }
        _ => Err("TRUNCATED".to_string()),
    }
}

fn read_opcode(r: &mut Reader) -> Result<Opcode, String> {
    let t = r.u8()?;
    let op = match t {
        1 => Opcode::PushInt(r.i64()?),
        2 => Opcode::PushStr(r.string()?),
        3 => Opcode::PushBool(r.u8()? != 0),
        4 => Opcode::PushNull,
        5 => Opcode::Add,
        6 => Opcode::Sub,
        7 => Opcode::Mul,
        8 => Opcode::Div,
        9 => Opcode::Mod,
        10 => Opcode::Concat,
        11 => Opcode::Eq,
        12 => Opcode::Ne,
        13 => Opcode::Lt,
        14 => Opcode::Le,
        15 => Opcode::Gt,
        16 => Opcode::Ge,
        17 => Opcode::Len,
        18 => Opcode::Distinct,
        19 => Opcode::Not,
        20 => Opcode::Jump(r.u32()? as usize),
        21 => Opcode::JumpIfFalse(r.u32()? as usize),
        22 => Opcode::Dup,
        23 => Opcode::Pop,
        24 => Opcode::Swap,
        25 => Opcode::Load(r.u32()?),
        26 => Opcode::Store(r.u32()?),
        27 => Opcode::ArrayNew,
        28 => Opcode::ArrayPush,
        29 => Opcode::ArrayGet,
        30 => Opcode::Print,
        31 => Opcode::Halt,
        32 => Opcode::Spawn(r.u32()?),
        33 => Opcode::Join,
        34 => Opcode::Yield,
        _ => return Err("TRUNCATED".to_string()),
    };
    Ok(op)
}

fn read_code(r: &mut Reader) -> Result<Vec<Opcode>, String> {
    let n = r.u32()? as usize;
    let mut code = Vec::with_capacity(n.min(1_000_000));
    for _ in 0..n {
        code.push(read_opcode(r)?);
    }
    Ok(code)
}

pub fn restore(bytes: &[u8]) -> Result<Vm, String> {
    if bytes.len() < 4 {
        return Err("TRUNCATED".to_string());
    }
    if &bytes[0..3] != b"MV7" {
        return Err("BAD_MAGIC".to_string());
    }
    if bytes[3] != 1 {
        return Err("BAD_VERSION".to_string());
    }

    let mut r = Reader { data: bytes, pos: 4 };
    let main = read_code(&mut r)?;
    let fiber_code_count = r.u32()? as usize;
    let mut fibers_code = Vec::with_capacity(fiber_code_count.min(1_000_000));
    for _ in 0..fiber_code_count {
        let name = r.string()?;
        let code = read_code(&mut r)?;
        fibers_code.push(FiberCode { name, code });
    }

    let global_count = r.u32()? as usize;
    let mut globals = Vec::with_capacity(global_count.min(1_000_000));
    for _ in 0..global_count {
        let name = r.string()?;
        let val = read_value(&mut r)?;
        globals.push((name, val));
    }

    let fiber_count = r.u32()? as usize;
    let mut fibers = Vec::with_capacity(fiber_count.min(1_000_000));
    for _ in 0..fiber_count {
        let id = r.u32()?;
        let pc = r.u32()? as usize;
        let code_ref = r.u32()?;
        let halted = r.u8()? != 0;
        let depth = r.u32()? as usize;
        let mut stack = Vec::with_capacity(depth.min(1_000_000));
        for _ in 0..depth {
            stack.push(read_value(&mut r)?);
        }
        fibers.push(Fiber { id, code_ref, pc, stack, halted });
    }

    let ready_count = r.u32()? as usize;
    let mut ready = VecDeque::with_capacity(ready_count.min(1_000_000));
    for _ in 0..ready_count {
        ready.push_back(r.u32()?);
    }

    let blocked_count = r.u32()? as usize;
    let mut blocked = Vec::with_capacity(blocked_count.min(1_000_000));
    for _ in 0..blocked_count {
        let waiter = r.u32()?;
        let target = r.u32()?;
        blocked.push((waiter, target));
    }

    let stored = r.u32()?;
    let actual = fnv1a(&bytes[..r.pos - 4]);
    if stored != actual {
        return Err("BAD_CHECKSUM".to_string());
    }

    let mut seen = std::collections::HashSet::new();
    let mut max_id = 0u32;
    for f in &fibers {
        if !seen.insert(f.id) {
            return Err("DUPLICATE_FIBER".to_string());
        }
        max_id = max_id.max(f.id);
    }

    let mut vm = Vm::new(Code { main, fibers: fibers_code });
    vm.globals = globals;
    vm.fibers = fibers;
    vm.ready = ready;
    vm.blocked = blocked;
    vm.current = vm.ready.front().copied().unwrap_or(0);
    vm.next_fiber_id = max_id + 1;
    vm.output = String::new();
    vm.steps = 0;
    Ok(vm)
}
