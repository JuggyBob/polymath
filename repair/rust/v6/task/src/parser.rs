use super::ast::{BinOp, Expr, Stmt, UnOp};
use super::token::{Token, TokenKind};

pub struct Parser<'a> {
    tokens: &'a [Token],
    pos: usize,
}

impl<'a> Parser<'a> {
    pub fn new(tokens: &'a [Token]) -> Self {
        Parser { tokens, pos: 0 }
    }

    fn kind(&self) -> &TokenKind {
        &self.tokens[self.pos].kind
    }

    fn at(&self, k: &TokenKind) -> bool {
        self.kind() == k
    }

    fn bump(&mut self) -> TokenKind {
        let t = self.tokens[self.pos].kind.clone();
        if self.pos + 1 < self.tokens.len() {
            self.pos += 1;
        }
        t
    }

    fn expect(&mut self, k: &TokenKind) -> Result<(), String> {
        if self.at(k) {
            self.bump();
            Ok(())
        } else {
            Err(format!("expected {:?}, found {:?}", k, self.kind()))
        }
    }

    pub fn parse_program(&mut self) -> Result<Vec<Stmt>, String> {
        let mut stmts = Vec::new();
        while !self.at(&TokenKind::Eof) {
            stmts.push(self.parse_stmt()?);
        }
        Ok(stmts)
    }

    fn parse_stmt(&mut self) -> Result<Stmt, String> {
        match self.kind().clone() {
            TokenKind::Let => {
                self.bump();
                let name = self.parse_ident()?;
                self.expect(&TokenKind::Assign)?;
                let e = self.parse_expr()?;
                self.expect(&TokenKind::Semi)?;
                Ok(Stmt::Let(name, e))
            }
            TokenKind::Set => {
                self.bump();
                let name = self.parse_ident()?;
                self.expect(&TokenKind::Assign)?;
                let e = self.parse_expr()?;
                self.expect(&TokenKind::Semi)?;
                Ok(Stmt::Set(name, e))
            }
            TokenKind::Print => {
                self.bump();
                let e = self.parse_expr()?;
                self.expect(&TokenKind::Semi)?;
                Ok(Stmt::Print(e))
            }
            TokenKind::Push => {
                self.bump();
                let name = self.parse_ident()?;
                self.expect(&TokenKind::Comma)?;
                let e = self.parse_expr()?;
                self.expect(&TokenKind::Semi)?;
                Ok(Stmt::Push(name, e))
            }
            TokenKind::If => {
                self.bump();
                let cond = self.parse_expr()?;
                self.expect(&TokenKind::LBrace)?;
                let then_body = self.parse_block()?;
                let else_body = if self.at(&TokenKind::Else) {
                    self.bump();
                    self.expect(&TokenKind::LBrace)?;
                    self.parse_block()?
                } else {
                    Vec::new()
                };
                Ok(Stmt::If(cond, then_body, else_body))
            }
            TokenKind::While => {
                self.bump();
                let cond = self.parse_expr()?;
                self.expect(&TokenKind::LBrace)?;
                let body = self.parse_block()?;
                Ok(Stmt::While(cond, body))
            }
            _ => {
                let e = self.parse_expr()?;
                self.expect(&TokenKind::Semi)?;
                Ok(Stmt::ExprStmt(e))
            }
        }
    }

    fn parse_block(&mut self) -> Result<Vec<Stmt>, String> {
        let mut body = Vec::new();
        while !self.at(&TokenKind::RBrace) {
            if self.at(&TokenKind::Eof) {
                return Err("unterminated block".to_string());
            }
            body.push(self.parse_stmt()?);
        }
        self.expect(&TokenKind::RBrace)?;
        Ok(body)
    }

    fn parse_ident(&mut self) -> Result<String, String> {
        match self.bump() {
            TokenKind::Ident(s) => Ok(s),
            other => Err(format!("expected identifier, found {:?}", other)),
        }
    }

    pub fn parse_expr(&mut self) -> Result<Expr, String> {
        self.parse_comparison()
    }

    fn parse_comparison(&mut self) -> Result<Expr, String> {
        let mut left = self.parse_additive()?;
        loop {
            let op = match self.kind() {
                TokenKind::EqEq => BinOp::Eq,
                TokenKind::NotEq => BinOp::Ne,
                TokenKind::Lt => BinOp::Lt,
                TokenKind::Le => BinOp::Le,
                TokenKind::Gt => BinOp::Gt,
                TokenKind::Ge => BinOp::Ge,
                _ => break,
            };
            self.bump();
            let right = self.parse_additive()?;
            left = Expr::Binary { op, left: Box::new(left), right: Box::new(right) };
            break;
        }
        Ok(left)
    }

    fn parse_additive(&mut self) -> Result<Expr, String> {
        let mut left = self.parse_mul()?;
        loop {
            let op = match self.kind() {
                TokenKind::Plus => BinOp::Add,
                TokenKind::Minus => BinOp::Sub,
                _ => break,
            };
            self.bump();
            let right = self.parse_mul()?;
            left = Expr::Binary { op, left: Box::new(left), right: Box::new(right) };
        }
        Ok(left)
    }

    fn parse_mul(&mut self) -> Result<Expr, String> {
        let mut left = self.parse_unary()?;
        loop {
            let op = match self.kind() {
                TokenKind::Star => BinOp::Mul,
                TokenKind::Slash => BinOp::Div,
                TokenKind::Percent => BinOp::Mod,
                _ => break,
            };
            self.bump();
            let right = self.parse_unary()?;
            left = Expr::Binary { op, left: Box::new(left), right: Box::new(right) };
        }
        Ok(left)
    }

    fn parse_unary(&mut self) -> Result<Expr, String> {
        match self.kind().clone() {
            TokenKind::Minus => {
                self.bump();
                Ok(Expr::Unary { op: UnOp::Neg, expr: Box::new(self.parse_primary()?) })
            }
            TokenKind::Bang => {
                self.bump();
                Ok(Expr::Unary { op: UnOp::Not, expr: Box::new(self.parse_primary()?) })
            }
            _ => self.parse_postfix(),
        }
    }

    fn parse_postfix(&mut self) -> Result<Expr, String> {
        let mut e = self.parse_primary()?;
        if self.at(&TokenKind::LBracket) {
            self.bump();
            let idx = self.parse_expr()?;
            self.expect(&TokenKind::RBracket)?;
            e = Expr::Index { array: Box::new(e), index: Box::new(idx) };
        }
        Ok(e)
    }

    fn parse_primary(&mut self) -> Result<Expr, String> {
        match self.bump() {
            TokenKind::Int(n) => Ok(Expr::Int(n)),
            TokenKind::Str(s) => Ok(Expr::Str(s)),
            TokenKind::True => Ok(Expr::Bool(true)),
            TokenKind::False => Ok(Expr::Bool(false)),
            TokenKind::NullVal => Ok(Expr::Null),
            TokenKind::Ident(s) => Ok(Expr::Var(s)),
            TokenKind::LParen => {
                let e = self.parse_expr()?;
                self.expect(&TokenKind::RParen)?;
                Ok(e)
            }
            TokenKind::LBracket => {
                let mut items = Vec::new();
                if !self.at(&TokenKind::RBracket) {
                    loop {
                        items.push(self.parse_expr()?);
                        if self.at(&TokenKind::Comma) {
                            self.bump();
                            if self.at(&TokenKind::RBracket) { break; }
                        } else {
                            break;
                        }
                    }
                }
                self.expect(&TokenKind::RBracket)?;
                Ok(Expr::Array(items))
            }
            TokenKind::Len => {
                self.expect(&TokenKind::LParen)?;
                let e = self.parse_expr()?;
                self.expect(&TokenKind::RParen)?;
                Ok(Expr::Len(Box::new(e)))
            }
            other => Err(format!("unexpected token {:?}", other)),
        }
    }
}

pub fn parse(tokens: &[Token]) -> Result<Vec<Stmt>, String> {
    let mut p = Parser::new(tokens);
    p.parse_program()
}
