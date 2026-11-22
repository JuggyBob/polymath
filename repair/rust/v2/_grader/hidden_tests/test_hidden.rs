#[path = "../src/lib.rs"]
mod lib;

use lib::*;

fn check(name: &str, cond: bool) {
    println!("TEST {} {}", name, if cond {"PASS"} else {"FAIL"});
}

fn safe(name: &str, f: impl FnOnce() -> bool) {
    let cond = std::panic::catch_unwind(std::panic::AssertUnwindSafe(f)).unwrap_or(false);
    check(name, cond);
}

fn reading(label: &str, value: i64) -> Reading {
    Reading { label: label.to_string(), value }
}

fn main() {
    safe("h_parse_trim", || {
        parse_reading("  cpu = 42  ") == Ok(reading("cpu", 42))
    });
    safe("h_parse_empty", || parse_reading("") == Err(ParseError::Empty));
    safe("h_parse_negative", || {
        parse_reading("cpu=-3") == Err(ParseError::NegativeNotAllowed)
    });
    safe("h_parse_out_of_range", || {
        parse_reading("cpu=2000") == Err(ParseError::OutOfRange)
    });

    safe("h_fromstr_invalid_number", || {
        "cpu=abc".parse::<Reading>() == Err(ParseError::InvalidNumber("abc".to_string()))
    });

    safe("h_parse_all_empty", || parse_all(&[]) == Ok(vec![]));
    safe("h_parse_all_order", || {
        parse_all(&["b=2", "a=1"]) == Ok(vec![reading("b", 2), reading("a", 1)])
    });

    safe("h_first_valid_all_bad", || first_valid(&["x", "y"]).is_none());
    safe("h_first_valid_first_good", || {
        first_valid(&["a=1", "b=2"]) == Some(reading("a", 1))
    });

    safe("h_count_over_all", || count_over(&[5, 6, 7], 4) == 3);
    safe("h_count_over_negative", || count_over(&[-3, -1, 0], -2) == 2);

    let rs = [reading("cpu", 3), reading("mem", 9), reading("io", 5)];
    safe("h_take_zero", || take_top_n(&rs, 0).is_empty());
    safe("h_skip_zero", || {
        skip_first_n(&rs, 0)
            == vec!["cpu".to_string(), "mem".to_string(), "io".to_string()]
    });
    safe("h_skip_all", || skip_first_n(&rs, 50).is_empty());

    safe("h_parse_scores_malformed", || {
        parse_scores(&["x", "2", "y"]) == vec![2]
    });

    safe("h_sum_values_empty", || sum_values(&[]) == Ok(0));
    safe("h_sum_values_positive", || {
        sum_values(&[reading("a", 3), reading("b", 4)]) == Ok(7)
    });
    safe("h_sum_values_negative", || {
        sum_values(&[reading("a", 5), reading("b", -5)]) == Err(ParseError::NegativeNotAllowed)
    });

    safe("h_display_error_invalid", || {
        format!("{}", ParseError::InvalidNumber("x".to_string())) == "invalid number: x"
    });
    safe("h_display_reading_negative", || {
        format!("{}", reading("d", -2)) == "d: -2"
    });
}
