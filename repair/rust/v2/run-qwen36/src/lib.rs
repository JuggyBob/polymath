//! Results, iterators and trait impls — repair fixture v2.
//!
//! Public signatures, variants and trait impls are fixed. Some
//! implementations below are wrong; fix the behaviour, not the API or tests.

use std::fmt;
use std::str::FromStr;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ParseError {
    Empty,
    InvalidNumber(String),
    NegativeNotAllowed,
    OutOfRange,
    UnknownUnit,
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ParseError::Empty => write!(f, "empty input"),
            ParseError::InvalidNumber(s) => write!(f, "invalid number: {}", s),
            ParseError::NegativeNotAllowed => write!(f, "negative value not allowed"),
            ParseError::OutOfRange => write!(f, "value out of range"),
            ParseError::UnknownUnit => write!(f, "unknown unit"),
        }
    }
}

impl std::error::Error for ParseError {}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Reading {
    pub label: String,
    pub value: i64,
}

impl fmt::Display for Reading {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: {}", self.label, self.value)
    }
}

impl FromStr for Reading {
    type Err = ParseError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        if s.trim().is_empty() {
            return Err(ParseError::Empty);
        }
        parse_reading(s)
    }
}

/// Parse one "label=value" line.
pub fn parse_reading(s: &str) -> Result<Reading, ParseError> {
    let t = s.trim();
    if t.is_empty() {
        return Err(ParseError::Empty);
    }
    let (label, raw) = match t.split_once('=') {
        Some(p) => p,
        None => return Err(ParseError::Empty),
    };
    let label = label.trim();
    if label.is_empty() {
        return Err(ParseError::Empty);
    }
    let raw = raw.trim();
    let value: i64 = match raw.parse() {
        Ok(v) => v,
        Err(_) => return Err(ParseError::InvalidNumber(raw.to_string())),
    };
    if value < 0 {
        return Err(ParseError::NegativeNotAllowed);
    }
    if value > 1000 {
        return Err(ParseError::OutOfRange);
    }
    Ok(Reading {
        label: label.to_string(),
        value,
    })
}

/// Parse every line, or fail on the first invalid one.
pub fn parse_all(lines: &[&str]) -> Result<Vec<Reading>, ParseError> {
    lines.iter().map(|s| parse_reading(s)).collect()
}

/// First line that parses, without panicking on the ones before it.
pub fn first_valid(lines: &[&str]) -> Option<Reading> {
    lines.iter().find_map(|s| parse_reading(s).ok())
}

/// Count values strictly greater than threshold.
pub fn count_over(values: &[i64], threshold: i64) -> usize {
    values.iter().filter(|&&v| v > threshold).count()
}

/// The n largest values, descending.
pub fn take_top_n(readings: &[Reading], n: usize) -> Vec<i64> {
    let mut vals: Vec<i64> = readings.iter().map(|r| r.value).collect();
    vals.sort_unstable_by(|a, b| b.cmp(a));
    vals.into_iter().take(n).collect()
}

/// Labels after skipping the first n readings.
pub fn skip_first_n(readings: &[Reading], n: usize) -> Vec<String> {
    readings.iter().skip(n).map(|r| r.label.clone()).collect()
}

/// Integers among the tokens, in order.
pub fn parse_scores(tokens: &[&str]) -> Vec<i64> {
    tokens.iter().filter_map(|t| t.parse::<i64>().ok()).collect()
}

/// Sum of values, rejecting any negative value.
pub fn sum_values(readings: &[Reading]) -> Result<i64, ParseError> {
    readings.iter().try_fold(0i64, |acc, r| {
        if r.value < 0 {
            Err(ParseError::NegativeNotAllowed)
        } else {
            Ok(acc + r.value)
        }
    })
}

/// Labels joined by ", ".
pub fn join_labels(readings: &[Reading]) -> String {
    readings
        .iter()
        .map(|r| r.label.as_str())
        .collect::<Vec<_>>()
        .join(", ")
}
