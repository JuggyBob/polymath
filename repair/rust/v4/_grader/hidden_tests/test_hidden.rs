#[path = "../src/lib.rs"]
mod lib;
use lib::*;

fn report(name: &str, ok: bool) {
    println!("TEST {} {}", name, if ok { "PASS" } else { "FAIL" });
}

fn main() {
    // ---- 16 behavioural contracts that fail on the planted code ----

    let mut v = RawVec::new();
    for x in [1, 2, 3, 4] { v.push(x); }
    report("test_h_sum_all", v.sum() == 10);

    let mut v = RawVec::new();
    for x in [4, 5, 6] { v.push(x); }
    report("test_h_pop_last", v.pop() == Some(6));

    let mut v = RawVec::new();
    for x in [1, 2, 3, 4, 5] { v.push(x); }
    report("test_h_contains_tail", v.contains(&5));

    let mut v = RawVec::new();
    for x in [1, 2, 3] { v.push(x); }
    v.reverse();
    report("test_h_reverse_full", v.as_slice() == &[3, 2, 1]);

    let c = SharedCounter::new();
    c.set(10);
    report("test_h_fetch_add_old", c.fetch_add(3) == 10);

    let c = SharedCounter::new();
    c.set(1);
    report("test_h_compare_set_mismatch", !c.compare_set(9, 7) && c.get() == 1);

    let c = SharedCounter::new();
    c.set(8);
    report("test_h_add_capped", c.add_capped(10, 10) == 2 && c.get() == 10);

    let cell = Cell::new(5);
    report("test_h_cell_replace_old", cell.replace_with(|x| x + 1) == 5);

    let mut slot = Slot::<i32>::new();
    slot.put(1);
    slot.put(2);
    slot.put(3);
    report("test_h_slot_init_count", slot.init_count() == 3);

    let mut slot = Slot::<i32>::new();
    slot.put(1);
    report("test_h_slot_put_if_empty_second", !slot.put_if_empty(2) && slot.get() == Some(&1));

    let mut slot = Slot::<i32>::new();
    slot.put(7);
    report("test_h_slot_get_or_stored", slot.get_or(&99) == &7);

    report("test_h_split_empty_fields", split_fields("a,,b") == vec!["a", "", "b"]);

    report("test_h_parse_pairs_empty_value", {
        let pairs = parse_pairs("a=&b=2");
        pairs.len() == 2 && pairs[0] == ("a", "") && pairs[1] == ("b", "2")
    });

    report("test_h_first_field", first_field("abc,def") == "abc");

    report("test_h_parse_int_index", parse_int_field("1,2,3", 1) == Some(2));

    let data = vec![1i32; 1000];
    reset_work();
    let total = prefix_sum(&data, 1000);
    report("test_h_perf_linear", total == 1000 && work() <= 2000);

    // ---- 24 supporting contracts (pass on pristine and on the fix) ----

    let mut v = RawVec::new();
    for x in [1, 2, 3, 4] { v.push(x); }
    report("test_h_rawvec_len", v.len() == 4);

    report("test_h_rawvec_get", {
        let mut v = RawVec::new();
        v.push(10); v.push(20); v.push(30);
        v.get(2) == Some(30) && v.get(9) == None
    });

    report("test_h_rawvec_first_empty", RawVec::new().first() == None);

    report("test_h_rawvec_pop_single", {
        let mut v = RawVec::new();
        v.push(7);
        v.pop() == Some(7) && v.len() == 0
    });

    report("test_h_rawvec_clear", {
        let mut v = RawVec::new();
        v.push(1); v.push(2);
        v.clear();
        v.len() == 0
    });

    let c = SharedCounter::new();
    c.inc(); c.inc(); c.inc();
    report("test_h_shared_inc", c.get() == 3);
    c.set(-3);
    report("test_h_shared_set", c.get() == -3);
    let c2 = c.clone();
    report("test_h_shared_strong_count", c.strong_count() == 2 && c2.strong_count() == 2);

    report("test_h_cell_thread", on_thread(Cell::new(11), |cell| *cell.get()) == 11);
    report("test_h_cell_get", Cell::new(4).get() == &4);

    report("test_h_slot_empty", Slot::<i32>::new().get() == None);
    report("test_h_slot_take_twice", {
        let mut s = Slot::<i32>::new();
        s.put(1);
        s.take() == Some(1) && s.take() == None
    });
    report("test_h_slot_is_init", {
        let mut s = Slot::<i32>::new();
        s.put(1);
        s.is_init()
    });

    report("test_h_split_no_empty", split_fields("x,y,z") == vec!["x", "y", "z"]);
    report("test_h_parse_pairs_all", parse_pairs("k=v&a=b") == vec![("k", "v"), ("a", "b")]);
    report("test_h_first_field_single", first_field("only") == "only");
    report("test_h_parse_int_dup", parse_int_field("5,5", 0) == Some(5));
    report("test_h_parse_int_oob", parse_int_field("1,2", 9) == None);

    report("test_h_prefix_sum_result", prefix_sum(&[2, 4], 2) == 6);

    report("test_h_zerocopy_fields", {
        let buf = String::from("aa,bb,cc");
        let fields = split_fields(&buf);
        let base = buf.as_ptr() as usize;
        let end = base + buf.len();
        fields.len() == 3 && fields.iter().all(|f| {
            let p = f.as_ptr() as usize;
            p >= base && p <= end
        })
    });

    report("test_h_zerocopy_pairs", {
        let buf = String::from("key=value&a=b");
        let pairs = parse_pairs(&buf);
        let base = buf.as_ptr() as usize;
        let end = base + buf.len();
        pairs.len() == 2 && pairs.iter().all(|(k, v)| {
            let kp = k.as_ptr() as usize;
            let vp = v.as_ptr() as usize;
            kp >= base && kp <= end && vp >= base && vp <= end
        })
    });

    // Intentional legacy policy: lenient decoding must not be changed.
    report("test_h_legacy_lenient", legacy_decode("not-a-number") == 0);
    report("test_h_legacy_valid", legacy_decode("123") == 123);

    // The unsafe Send/Sync impl on RawVec must keep working across threads.
    report("test_h_rawvec_thread", {
        let mut v = RawVec::new();
        v.push(5); v.push(6); v.push(0);
        on_thread(v, |b| b.sum()) == 11
    });
}
