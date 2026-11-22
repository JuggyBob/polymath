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
    safe("v_parse_ok", || {
        parse_reading("cpu=42") == Ok(reading("cpu", 42))
    });
    safe("v_parse_bad_number", || parse_reading("cpu=xyz").is_err());

    safe("v_fromstr_empty", || {
        "".parse::<Reading>() == Err(ParseError::Empty)
    });

    safe("v_parse_all_ok", || {
        parse_all(&["a=1", "b=2"]) == Ok(vec![reading("a", 1), reading("b", 2)])
    });
    safe("v_parse_all_bad", || parse_all(&["a=1", "oops", "b=2"]).is_err());

    safe("v_first_valid_ok", || {
        first_valid(&["bad", "a=1"]) == Some(reading("a", 1))
    });

    safe("v_count_over", || count_over(&[1, 5, 3], 2) == 2);

    let rs = [reading("cpu", 3), reading("mem", 9), reading("io", 5)];
    safe("v_take_top_n", || take_top_n(&rs, 2) == vec![9, 5]);
    safe("v_skip_first_n", || {
        skip_first_n(&rs, 1) == vec!["mem".to_string(), "io".to_string()]
    });

    safe("v_parse_scores", || {
        parse_scores(&["1", "x", "3"]) == vec![1, 3]
    });

    safe("v_sum_values_ok", || {
        sum_values(&[reading("a", 1), reading("b", 2)]) == Ok(3)
    });
    safe("v_sum_values_negative", || {
        sum_values(&[reading("a", 1), reading("b", -2)]).is_err()
    });

    safe("v_join_labels", || {
        join_labels(&[reading("a", 1), reading("b", 2), reading("c", 3)]) == "a, b, c"
    });
    safe("v_display_reading", || {
        format!("{}", reading("cpu", 7)) == "cpu: 7"
    });
}
