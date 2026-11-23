#[derive(Clone, Debug)]
pub enum UnOp {
    Neg,
    Not,
}

#[derive(Clone, Debug)]
pub enum BinOp {
    Add,
    Sub,
    Mul,
    Div,
    Mod,
    Eq,
    Ne,
    Lt,
    Le,
    Gt,
    Ge,
}

#[derive(Clone, Debug)]
pub enum Expr {
    Int(i64),
    Str(String),
    Bool(bool),
    Null,
    Var(String),
    Unary { op: UnOp, expr: Box<Expr> },
    Binary { op: BinOp, left: Box<Expr>, right: Box<Expr> },
    Array(Vec<Expr>),
    Index { array: Box<Expr>, index: Box<Expr> },
    Len(Box<Expr>),
    Distinct(Box<Expr>),
    Spawn(String),
}

#[derive(Clone, Debug)]
pub enum Stmt {
    Let(String, Expr),
    Set(String, Expr),
    Push(String, Expr),
    Print(Expr),
    If(Expr, Vec<Stmt>, Vec<Stmt>),
    While(Expr, Vec<Stmt>),
    Fiber(String, Vec<Stmt>),
    Join(Expr),
    Yield,
    ExprStmt(Expr),
}
