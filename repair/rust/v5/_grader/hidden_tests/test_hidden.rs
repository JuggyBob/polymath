#[path = "../src/lib.rs"]
mod lib;
use lib::*;
use std::time::Instant;

const HOT_THRESHOLD_S: f64 = 0.020;
const PRIME_BATCH_THRESHOLD_S: f64 = 0.040;

macro_rules! check {
    ($name:ident, $cond:expr) => {
        println!("TEST {} {}", stringify!($name), if $cond { "PASS" } else { "FAIL" });
    };
}

fn p(x: f64, y: f64, z: f64, m: f64, a: bool) -> Particle {
    make_particle(x, y, z, m, a)
}

fn main() {
    // ---- const generics ----
    check!(test_h_vec_len_zero, Vector::<0>::new([]).len() == 0);
    check!(test_h_vec_len_one, Vector::<1>::new([5.0]).len() == 1);
    check!(test_h_vec_len_three, Vector::<3>::new([1.0, 2.0, 3.0]).len() == 3);
    check!(test_h_vec_sum_basic, (Vector::<3>::new([1.0, 2.0, 3.0]).sum() - 6.0).abs() < 1e-9);

    let a = Vector::<3>::new([1.0, 2.0, 3.0]);
    let b = Vector::<3>::new([4.0, 5.0, 6.0]);
    check!(test_h_vec_dot_distinct, (a.dot(&b) - 32.0).abs() < 1e-9);
    check!(test_h_vec_add_basic, a.add(&b).data == [5.0, 7.0, 9.0]);
    check!(test_h_vec_add_last,
        Vector::<2>::new([1.0, 2.0]).add(&Vector::<2>::new([10.0, 20.0])).data == [11.0, 22.0]);
    check!(test_h_vec_scale_all, a.scale(3.0).data == [3.0, 6.0, 9.0]);
    check!(test_h_vec_scale_negative, a.scale(-2.0).data == [-2.0, -4.0, -6.0]);

    // ---- generic iterator helpers ----
    check!(test_h_sum_even_mixed, sum_even(&[1, 2, 3, 4, 5, 6]) == 12);
    check!(test_h_sum_even_all_odd, sum_even(&[1, 3, 5]) == 0);
    check!(test_h_fold_count_first_matches, fold_count(&[2, 4, 6], |x| x % 2 == 0) == 3);
    check!(test_h_apply_times_once, apply_times(10, 1, |x| x + 3) == 13);
    check!(test_h_apply_times_many, apply_times(1, 3, |x| x * 2) == 8);
    check!(test_h_first_match_single, first_match(&[1, 3, 5], |x| *x > 3) == Some(2));
    check!(test_h_first_match_multiple, first_match(&[1, 3, 5, 6], |x| *x % 2 == 1) == Some(0));

    // ---- particle layouts and hot loop ----
    check!(test_h_total_mass_inactive,
        (total_active_mass(&[p(0.0, 0.0, 0.0, 10.0, true), p(0.0, 0.0, 0.0, 99.0, false)]) - 10.0).abs() < 1e-9);
    check!(test_h_mean_speed_values,
        (mean_speed(&[p(3.0, 4.0, 0.0, 1.0, true), p(0.0, 0.0, 12.0, 1.0, true)]) - 8.5).abs() < 1e-9);
    {
        let particles: Vec<Particle> = (0..(1usize << 22))
            .map(|i| p((i % 97) as f64, (i % 89) as f64, (i % 83) as f64, 1.0, true))
            .collect();
        let t = Instant::now();
        let m = mean_speed(&particles);
        let elapsed = t.elapsed().as_secs_f64();
        check!(test_h_mean_speed_perf, m > 0.0 && elapsed < HOT_THRESHOLD_S);
    }

    let soa = ParticleSoA {
        x: vec![3.0, 0.0, 1.0],
        y: vec![4.0, 0.0, 1.0],
        z: vec![0.0, 0.0, 0.0],
        mass: vec![2.0, 3.0, 100.0],
        active: vec![true, true, false],
    };
    check!(test_h_soa_mass_last, (soa_mass(&soa) - 5.0).abs() < 1e-9);
    check!(test_h_soa_speed_z_used,
        (soa_speed_sum(&ParticleSoA { x: vec![3.0], y: vec![4.0], z: vec![12.0],
                                      mass: vec![1.0], active: vec![true] }) - 13.0).abs() < 1e-9);

    // ---- bit-level reinterpretation ----
    check!(test_h_bits_to_f32_known, (bits_to_f32(0x3F80_0000) - 1.0).abs() < 1e-9);
    check!(test_h_f32_to_bits_known, f32_to_bits(1.0) == 0x3F80_0000);
    check!(test_h_u64_from_le_bytes, u64_from_le_bytes([1, 0, 0, 0, 0, 0, 0, 0]) == 1);
    check!(test_h_u64_bytes_roundtrip,
        u64_from_le_bytes(u64_le_bytes(0x0102_0304_0506_0708)) == 0x0102_0304_0506_0708);
    check!(test_h_sign_negative_zero, sign_of_f64(-0.0));
    check!(test_h_reinterpret_min, reinterpret_u32_as_i32(0xFFFF_FFFF) == -1);

    // ---- enum layout and niche encoding ----
    check!(test_h_maybe_from_zero, maybe_from(Some(0)) == MaybeU32::Some(0));
    check!(test_h_maybe_value_none, maybe_value(MaybeU32::None) == None);
    check!(test_h_pack_option_none, pack_option(None) == 0);
    check!(test_h_unpack_option_one, unpack_option(1).map(|v| v.get()) == Some(1));
    check!(test_h_unpack_option_zero, unpack_option(0).is_none());
    check!(test_h_niche_sizes, niche_sizes() == (4, 8));
    check!(test_h_color_code_blue, color_code(Color::Blue) == 3);
    check!(test_h_color_from_code_two, color_from_code(2) == Some(Color::Green));

    // ---- frozen legacy helper ----
    check!(test_h_legacy_frozen,
        legacy_is_odd_prime(9) && legacy_is_odd_prime(3) && !legacy_is_odd_prime(2)
            && !legacy_is_odd_prime(4) && !legacy_is_odd_prime(1));

    // ---- primality ----
    check!(test_h_is_prime_zero, !is_prime(0));
    check!(test_h_is_prime_one, !is_prime(1));
    check!(test_h_is_prime_small_primes,
        [5u64, 7, 11, 13, 17, 19, 23, 29].iter().all(|&n| is_prime(n)));
    check!(test_h_is_prime_small_composites,
        [25u64, 27, 33, 35, 49, 121].iter().all(|&n| !is_prime(n)));
    check!(test_h_is_prime_semiprime_large, !is_prime(1_000_003u64 * 1_000_003));
    check!(test_h_is_prime_u64_max, !is_prime(u64::MAX));
    check!(test_h_is_prime_large_prime, is_prime(1_000_000_007));

    check!(test_h_count_primes_mixed, count_primes(&[0, 1, 2, 3, 4, 5, 9, 11]) == 4);
    {
        let candidates: Vec<u64> = (0..1_000_000u64).map(|i| 2 + (i % 2000)).collect();
        let t = Instant::now();
        let c = count_primes(&candidates);
        let elapsed = t.elapsed().as_secs_f64();
        check!(test_h_count_primes_perf, c > 0 && elapsed < PRIME_BATCH_THRESHOLD_S);
    }
}
