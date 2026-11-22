use super::token::{keyword, Token, TokenKind};

pub fn lex(src: &str) -> Result<Vec<Token>, String> {
    let chars: Vec<char> = src.chars().collect();
    let mut i = 0usize;
    let mut line = 1usize;
    let mut out = Vec::new();

    while i < chars.len() {
        let c = chars[i];
        if c == '\n' {
            line += 1;
            i += 1;
            continue;
        }
        if c.is_whitespace() {
            i += 1;
            continue;
        }
        if c == '/' && i + 1 < chars.len() && chars[i + 1] == '/' {
            while i < chars.len() && chars[i] != '\n' {
                i += 1;
            }
            continue;
        }
        if c.is_ascii_digit() {
            let start = i;
            while i < chars.len() && chars[i].is_ascii_digit() {
                i += 1;
            }
            let s: String = chars[start..i].iter().collect();
            let n: i64 = s.parse().map_err(|_| format!("line {}: bad integer", line))?;
            out.push(Token { kind: TokenKind::Int(n), line });
            continue;
        }
        if c == '"' {
            i += 1;
            let mut s = String::new();
            loop {
                if i >= chars.len() {
                    return Err(format!("line {}: unterminated string", line));
                }
                let d = chars[i];
                if d == '"' {
                    i += 1;
                    break;
                }
                if d == '\\' {
                    i += 1;
                    if i >= chars.len() {
                        return Err(format!("line {}: bad escape", line));
                    }
                    let e = chars[i];
                    match e {
                        'n' => s.push('\n'),
                        't' => s.push_str("    "),
                        'r' => s.push('\r'),
                        '\\' => s.push('\\'),
                        '"' => s.push('"'),
                        '0' => s.push('\0'),
                        _ => return Err(format!("line {}: unknown escape", line)),
                    }
                    i += 1;
                } else {
                    if d == '\n' {
                        line += 1;
                    }
                    s.push(d);
                    i += 1;
                }
            }
            out.push(Token { kind: TokenKind::Str(s), line });
            continue;
        }
        if c.is_ascii_alphabetic() || c == '_' {
            let start = i;
            while i < chars.len() && (chars[i].is_ascii_alphanumeric() || chars[i] == '_') {
                i += 1;
            }
            let s: String = chars[start..i].iter().collect();
            let kind = keyword(&s).unwrap_or(TokenKind::Ident(s));
            out.push(Token { kind, line });
            continue;
        }
        let two = if i + 1 < chars.len() {
            [chars[i], chars[i + 1]]
        } else {
            ['\0', '\0']
        };
        let kind = match two {
            ['=', '='] => { i += 2; TokenKind::EqEq }
            ['!', '='] => { i += 2; TokenKind::NotEq }
            ['<', '='] => { i += 2; TokenKind::Le }
            ['>', '='] => { i += 2; TokenKind::Ge }
            _ => match c {
                '+' => { i += 1; TokenKind::Plus }
                '-' => { i += 1; TokenKind::Minus }
                '*' => { i += 1; TokenKind::Star }
                '/' => { i += 1; TokenKind::Slash }
                '%' => { i += 1; TokenKind::Percent }
                '<' => { i += 1; TokenKind::Lt }
                '>' => { i += 1; TokenKind::Gt }
                '=' => { i += 1; TokenKind::Assign }
                '!' => { i += 1; TokenKind::Bang }
                '(' => { i += 1; TokenKind::LParen }
                ')' => { i += 1; TokenKind::RParen }
                '[' => { i += 1; TokenKind::LBracket }
                ']' => { i += 1; TokenKind::RBracket }
                '{' => { i += 1; TokenKind::LBrace }
                '}' => { i += 1; TokenKind::RBrace }
                ',' => { i += 1; TokenKind::Comma }
                ';' => { i += 1; TokenKind::Semi }
                _ => return Err(format!("line {}: unexpected char '{}'", line, c)),
            },
        };
        out.push(Token { kind, line });
    }
    out.push(Token { kind: TokenKind::Eof, line });
    Ok(out)
}
