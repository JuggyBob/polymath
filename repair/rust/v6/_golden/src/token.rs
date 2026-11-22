#[derive(Clone, Debug, PartialEq)]
pub enum TokenKind {
    Int(i64),
    Str(String),
    Ident(String),
    Let,
    Set,
    Print,
    If,
    Else,
    While,
    Push,
    Len,
    Distinct,
    True,
    False,
    NullVal,
    Plus,
    Minus,
    Star,
    Slash,
    Percent,
    EqEq,
    NotEq,
    Lt,
    Le,
    Gt,
    Ge,
    LParen,
    RParen,
    LBracket,
    RBracket,
    LBrace,
    RBrace,
    Comma,
    Semi,
    Assign,
    Bang,
    Eof,
}

#[derive(Clone, Debug)]
pub struct Token {
    pub kind: TokenKind,
    pub line: usize,
}

pub fn keyword(s: &str) -> Option<TokenKind> {
    match s {
        "let" => Some(TokenKind::Let),
        "set" => Some(TokenKind::Set),
        "print" => Some(TokenKind::Print),
        "if" => Some(TokenKind::If),
        "else" => Some(TokenKind::Else),
        "while" => Some(TokenKind::While),
        "push" => Some(TokenKind::Push),
        "len" => Some(TokenKind::Len),
        "distinct" => Some(TokenKind::Distinct),
        "true" => Some(TokenKind::True),
        "false" => Some(TokenKind::False),
        "null" => Some(TokenKind::NullVal),
        _ => None,
    }
}
