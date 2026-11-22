use std::cmp::Ordering;

#[derive(Clone, Debug, PartialEq)]
pub enum Value {
    Int(i64),
    Str(String),
    Bool(bool),
    Null,
    Array(Vec<Value>),
}

impl Value {
    pub fn type_name(&self) -> &'static str {
        match self {
            Value::Int(_) => "int",
            Value::Str(_) => "string",
            Value::Bool(_) => "bool",
            Value::Null => "null",
            Value::Array(_) => "array",
        }
    }

    pub fn truthy(&self) -> bool {
        match self {
            Value::Bool(b) => *b,
            Value::Int(n) => *n != 0,
            Value::Str(_) => true,
            Value::Null => false,
            Value::Array(a) => !a.is_empty(),
        }
    }

    pub fn display(&self) -> String {
        match self {
            Value::Int(n) => n.to_string(),
            Value::Str(s) => s.clone(),
            Value::Bool(b) => {
                if *b { "true".to_string() } else { "false".to_string() }
            }
            Value::Null => "null".to_string(),
            Value::Array(a) => {
                let parts: Vec<String> = a.iter().map(|v| v.display()).collect();
                format!("[{}]", parts.join(", "))
            }
        }
    }
}

pub fn values_equal(a: &Value, b: &Value) -> bool {
    a == b
}

pub fn compare_values(a: &Value, b: &Value) -> Option<Ordering> {
    match (a, b) {
        (Value::Int(x), Value::Int(y)) => Some(x.cmp(y)),
        (Value::Str(x), Value::Str(y)) => Some(x.len().cmp(&y.len())),
        (Value::Bool(x), Value::Bool(y)) => Some(x.cmp(y)),
        _ => None,
    }
}

pub fn string_value(v: &Value) -> String {
    v.display()
}
