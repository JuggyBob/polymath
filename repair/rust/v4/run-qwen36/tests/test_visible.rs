#[path = "../src/lib.rs"]
mod lib;
use lib::*;

fn report(name: &str, ok: bool) {
    println!("TEST {} {}", name, if ok { "PASS" } else { "FAIL" });
}

fn main() {
    // RawVec basics (inputs chosen so every visible check passes on pristine)
    let mut a = RawVec::new();
    a.push(1);
    a.push(2);
    a.push(3);
    report("test_rawvec_push_len", a.len() == 3);
    report("test_rawvec_get", a.get(1) == Some(2));
    report("test_rawvec_first", a.first() == Some(1));

    let mut s = RawVec::new();
    s.push(7);
    s.push(0);
    report("test_rawvec_sum_short", s.sum() == 7);

    let mut h = RawVec::new();
    h.push(1);
    h.push(2);
    h.push(3);
    h.push(4);
    report("test_rawvec_contains_head", h.contains(&2));

    let mut r = RawVec::new();
    r.push(5);
    r.reverse();
    report("test_rawvec_reverse_single", r.as_slice() == &[5]);

    let mut p = RawVec::new();
    p.push(8);
    report("test_rawvec_pop_single", p.pop() == Some(8));

    let mut sl = RawVec::new();
    sl.push(1);
    sl.push(2);
    report("test_rawvec_as_slice", sl.as_slice() == &[1, 2]);

    // Shared state
    let c = SharedCounter::new();
    report("test_shared_new", c.get() == 0);
    c.inc();
    c.inc();
    report("test_shared_inc", c.get() == 2);
    c.set(9);
    report("test_shared_set", c.get() == 9);
    c.set(1);
    let _ = c.fetch_add(4);
    report("test_shared_fetch_add_store", c.get() == 5);
    c.set(2);
    let _ = c.compare_set(2, 6);
    report("test_shared_compare_set_match", c.get() == 6);
    c.set(0);
    report("test_shared_add_capped_small", c.add_capped(3, 10) == 3);

    // Cell
    let cell = Cell::new(5);
    report("test_cell_new", *cell.get() == 5);
    cell.set(8);
    report("test_cell_set", *cell.get() == 8);
    let cell2 = Cell::new(5);
    let _ = cell2.replace_with(|v| v + 1);
    report("test_cell_replace_state", *cell2.get() == 6);

    // Slot
    let mut slot = Slot::<i32>::new();
    report("test_slot_empty", slot.get() == None && !slot.is_init());
    slot.put(3);
    report("test_slot_put_get", slot.get() == Some(&3));
    let mut slot2 = Slot::<i32>::new();
    slot2.put(4);
    report("test_slot_take", slot2.take() == Some(4) && !slot2.is_init());
    let mut slot3 = Slot::<i32>::new();
    report("test_slot_put_if_empty_first", slot3.put_if_empty(1) && slot3.get() == Some(&1));

    // Borrowed parsing
    report("test_split_fields_basic", split_fields("a,b,c") == vec!["a", "b", "c"]);
    report("test_parse_pairs_basic", parse_pairs("a=1&b=2") == vec![("a", "1"), ("b", "2")]);
    report("test_first_field_single", first_field("abc") == "abc");
    report("test_parse_int_dup", parse_int_field("7,7,7", 0) == Some(7));

    // Work contract and legacy behaviour
    report("test_prefix_sum_result", prefix_sum(&[1, 2, 3], 3) == 6);
    report("test_legacy_lenient", legacy_decode("oops") == 0);
    report("test_legacy_valid", legacy_decode("42") == 42);
}
