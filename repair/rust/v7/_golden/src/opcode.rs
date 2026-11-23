#[derive(Clone, Debug, PartialEq)]
pub enum Opcode {
    PushInt(i64),
    PushStr(String),
    PushBool(bool),
    PushNull,
    Add,
    Sub,
    Mul,
    Div,
    Mod,
    Concat,
    Eq,
    Ne,
    Lt,
    Le,
    Gt,
    Ge,
    Len,
    Distinct,
    Not,
    Jump(usize),
    JumpIfFalse(usize),
    Dup,
    Pop,
    Swap,
    Load(u32),
    Store(u32),
    ArrayNew,
    ArrayPush,
    ArrayGet,
    Print,
    Halt,
    Spawn(u32),
    Join,
    Yield,
}

#[derive(Clone, Debug, PartialEq)]
pub struct FiberCode {
    pub name: String,
    pub code: Vec<Opcode>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Code {
    pub main: Vec<Opcode>,
    pub fibers: Vec<FiberCode>,
}

impl Code {
    pub fn new() -> Self {
        Code { main: Vec::new(), fibers: Vec::new() }
    }

    pub fn all_opcodes(&self) -> impl Iterator<Item = &Opcode> {
        self.main.iter().chain(self.fibers.iter().flat_map(|f| f.code.iter()))
    }
}

pub fn tag(op: &Opcode) -> u8 {
    match op {
        Opcode::PushInt(_) => 1,
        Opcode::PushStr(_) => 2,
        Opcode::PushBool(_) => 3,
        Opcode::PushNull => 4,
        Opcode::Add => 5,
        Opcode::Sub => 6,
        Opcode::Mul => 7,
        Opcode::Div => 8,
        Opcode::Mod => 9,
        Opcode::Concat => 10,
        Opcode::Eq => 11,
        Opcode::Ne => 12,
        Opcode::Lt => 13,
        Opcode::Le => 14,
        Opcode::Gt => 15,
        Opcode::Ge => 16,
        Opcode::Len => 17,
        Opcode::Distinct => 18,
        Opcode::Not => 19,
        Opcode::Jump(_) => 20,
        Opcode::JumpIfFalse(_) => 21,
        Opcode::Dup => 22,
        Opcode::Pop => 23,
        Opcode::Swap => 24,
        Opcode::Load(_) => 25,
        Opcode::Store(_) => 26,
        Opcode::ArrayNew => 27,
        Opcode::ArrayPush => 28,
        Opcode::ArrayGet => 29,
        Opcode::Print => 30,
        Opcode::Halt => 31,
        Opcode::Spawn(_) => 32,
        Opcode::Join => 33,
        Opcode::Yield => 34,
    }
}

fn mnemonic(op: &Opcode) -> &'static str {
    match op {
        Opcode::PushInt(_) => "PUSH_INT",
        Opcode::PushStr(_) => "PUSH_STR",
        Opcode::PushBool(_) => "PUSH_BOOL",
        Opcode::PushNull => "PUSH_NULL",
        Opcode::Add => "ADD",
        Opcode::Sub => "SUB",
        Opcode::Mul => "MUL",
        Opcode::Div => "DIV",
        Opcode::Mod => "MOD",
        Opcode::Concat => "CONCAT",
        Opcode::Eq => "EQ",
        Opcode::Ne => "NE",
        Opcode::Lt => "LT",
        Opcode::Le => "LE",
        Opcode::Gt => "GT",
        Opcode::Ge => "GE",
        Opcode::Len => "LEN",
        Opcode::Distinct => "DISTINCT",
        Opcode::Not => "NOT",
        Opcode::Jump(_) => "JUMP",
        Opcode::JumpIfFalse(_) => "JUMP_IF_FALSE",
        Opcode::Dup => "DUP",
        Opcode::Pop => "POP",
        Opcode::Swap => "SWAP",
        Opcode::Load(_) => "LOAD",
        Opcode::Store(_) => "STORE",
        Opcode::ArrayNew => "ARRAY_NEW",
        Opcode::ArrayPush => "ARRAY_PUSH",
        Opcode::ArrayGet => "ARRAY_GET",
        Opcode::Print => "PRINT",
        Opcode::Halt => "HALT",
        Opcode::Spawn(_) => "SPAWN",
        Opcode::Join => "JOIN",
        Opcode::Yield => "YIELD",
    }
}

pub fn escape(s: &str) -> String {
    let mut out = String::new();
    for c in s.chars() {
        match c {
            '\\' => out.push_str("\\\\"),
            '"' => out.push_str("\\\""),
            '\n' => out.push_str("\\n"),
            '\t' => out.push_str("\\t"),
            '\r' => out.push_str("\\r"),
            '\0' => out.push_str("\\0"),
            _ => out.push(c),
        }
    }
    out
}

pub fn unescape(s: &str) -> Result<String, String> {
    let chars: Vec<char> = s.chars().collect();
    let mut out = String::new();
    let mut i = 0usize;
    while i < chars.len() {
        if chars[i] == '\\' {
            i += 1;
            if i >= chars.len() {
                return Err("dangling escape".to_string());
            }
            match chars[i] {
                '\\' => out.push('\\'),
                '"' => out.push('"'),
                'n' => out.push('\n'),
                't' => out.push('\t'),
                'r' => out.push('\r'),
                '0' => out.push('\0'),
                other => return Err(format!("bad escape {}", other)),
            }
            i += 1;
        } else {
            out.push(chars[i]);
            i += 1;
        }
    }
    Ok(out)
}

pub fn describe(op: &Opcode) -> String {
    let base = mnemonic(op);
    match op {
        Opcode::PushInt(n) => format!("{} {}", base, n),
        Opcode::PushStr(s) => format!("{} \"{}\"", base, escape(s)),
        Opcode::PushBool(b) => format!("{} {}", base, if *b { "true" } else { "false" }),
        Opcode::Jump(n) | Opcode::JumpIfFalse(n) => format!("{} {}", base, n),
        Opcode::Load(n) | Opcode::Store(n) => format!("{} {}", base, n),
        Opcode::Spawn(n) => format!("{} {}", base, n),
        _ => base.to_string(),
    }
}

fn disassemble_block(code: &[Opcode]) -> String {
    let mut out = String::with_capacity(code.len() * 24);
    for (i, op) in code.iter().enumerate() {
        out.push_str(&format!("{:04} {}\n", i, describe(op)));
    }
    out
}

pub fn disassemble(code: &Code) -> String {
    let mut out = disassemble_block(&code.main);
    for f in &code.fibers {
        out.push_str(&format!("FIBER {}\n", f.name));
        out.push_str(&disassemble_block(&f.code));
    }
    out
}

pub fn serialize(code: &Code) -> String {
    let mut out = String::with_capacity(code.main.len() * 24);
    for op in &code.main {
        out.push_str(&describe(op));
        out.push('\n');
    }
    for f in &code.fibers {
        out.push_str(&format!("FIBER {}\n", f.name));
        for op in &f.code {
            out.push_str(&describe(op));
            out.push('\n');
        }
    }
    out
}

fn parse_line(line: &str) -> Result<Opcode, String> {
    let mut parts = line.splitn(2, ' ');
    let name = parts.next().unwrap_or("");
    let arg = parts.next().unwrap_or("").trim();
    let op = match name {
        "PUSH_INT" => Opcode::PushInt(arg.parse::<i64>().map_err(|_| "bad int".to_string())?),
        "PUSH_STR" => {
            let inner = arg.strip_prefix('"').and_then(|x| x.strip_suffix('"'))
                .ok_or_else(|| "bad string".to_string())?;
            Opcode::PushStr(unescape(inner)?)
        }
        "PUSH_BOOL" => Opcode::PushBool(match arg {
            "true" => true,
            "false" => false,
            _ => return Err("bad bool".to_string()),
        }),
        "PUSH_NULL" => Opcode::PushNull,
        "ADD" => Opcode::Add,
        "SUB" => Opcode::Sub,
        "MUL" => Opcode::Mul,
        "DIV" => Opcode::Div,
        "MOD" => Opcode::Mod,
        "CONCAT" => Opcode::Concat,
        "EQ" => Opcode::Eq,
        "NE" => Opcode::Ne,
        "LT" => Opcode::Lt,
        "LE" => Opcode::Le,
        "GT" => Opcode::Gt,
        "GE" => Opcode::Ge,
        "LEN" => Opcode::Len,
        "DISTINCT" => Opcode::Distinct,
        "NOT" => Opcode::Not,
        "JUMP" => Opcode::Jump(arg.parse::<usize>().map_err(|_| "bad jump".to_string())?),
        "JUMP_IF_FALSE" => Opcode::JumpIfFalse(arg.parse::<usize>().map_err(|_| "bad jump".to_string())?),
        "DUP" => Opcode::Dup,
        "POP" => Opcode::Pop,
        "SWAP" => Opcode::Swap,
        "LOAD" => Opcode::Load(arg.parse::<u32>().map_err(|_| "bad slot".to_string())?),
        "STORE" => Opcode::Store(arg.parse::<u32>().map_err(|_| "bad slot".to_string())?),
        "ARRAY_NEW" => Opcode::ArrayNew,
        "ARRAY_PUSH" => Opcode::ArrayPush,
        "ARRAY_GET" => Opcode::ArrayGet,
        "PRINT" => Opcode::Print,
        "HALT" => Opcode::Halt,
        "SPAWN" => Opcode::Spawn(arg.parse::<u32>().map_err(|_| "bad fiber".to_string())?),
        "JOIN" => Opcode::Join,
        "YIELD" => Opcode::Yield,
        _ => return Err(format!("unknown opcode {}", name)),
    };
    Ok(op)
}

pub fn deserialize(s: &str) -> Result<Code, String> {
    let mut code = Code::new();
    let mut in_fiber = false;
    for raw in s.lines() {
        let line = raw.trim();
        if line.is_empty() {
            continue;
        }
        if let Some(name) = line.strip_prefix("FIBER ") {
            code.fibers.push(FiberCode { name: name.trim().to_string(), code: Vec::new() });
            in_fiber = true;
            continue;
        }
        let op = parse_line(line)?;
        if in_fiber {
            code.fibers.last_mut().unwrap().code.push(op);
        } else {
            code.main.push(op);
        }
    }
    Ok(code)
}
