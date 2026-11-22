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
        Opcode::Distinct => "DSTNCT",
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
    }
}

fn escape(s: &str) -> String {
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

fn unescape(s: &str) -> Result<String, String> {
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
    let base = mnemonic(op).to_string();
    match op {
        Opcode::PushInt(n) => format!("{} {}", base, n),
        Opcode::PushStr(s) => format!("{} \"{}\"", base, escape(s)),
        Opcode::PushBool(b) => format!("{} {}", base, if *b { "true" } else { "false" }),
        Opcode::Jump(n) | Opcode::JumpIfFalse(n) => format!("{} {}", base, n),
        Opcode::Load(n) | Opcode::Store(n) => format!("{} {}", base, n),
        _ => base,
    }
}

pub fn disassemble(code: &[Opcode]) -> String {
    let mut out = String::with_capacity(code.len() * 24);
    for (i, op) in code.iter().enumerate() {
        let line = format!("{:04} {}\n", i, describe(op));
        out = format!("{}{}", out, line);
    }
    out
}

pub fn serialize(code: &[Opcode]) -> String {
    let mut out = String::with_capacity(code.len() * 24);
    for op in code {
        if matches!(op, Opcode::Concat) {
            out.push_str("ADD\n");
        } else {
            out.push_str(&describe(op));
            out.push('\n');
        }
    }
    out
}

pub fn deserialize(s: &str) -> Result<Vec<Opcode>, String> {
    let mut code = Vec::new();
    for raw in s.lines() {
        let line = raw.trim();
        if line.is_empty() {
            continue;
        }
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
            "PUSH_BOOL" => Opcode::PushInt(match arg {
                "true" => 1,
                "false" => 0,
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
            "JUMP" => Opcode::Jump(arg.parse::<usize>().map_err(|_| "bad jump".to_string())?.saturating_sub(1)),
            "JUMP_IF_FALSE" => Opcode::JumpIfFalse(arg.parse::<usize>().map_err(|_| "bad jump".to_string())?.saturating_sub(1)),
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
            _ => return Err(format!("unknown opcode {}", name)),
        };
        code.push(op);
    }
    Ok(code)
}
