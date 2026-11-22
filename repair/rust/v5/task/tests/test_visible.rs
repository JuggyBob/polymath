#[path = "../src/lib.rs"]
mod lib;
use lib::*;
use std::num::NonZeroU32;

macro_rules! check {
    ($name:ident, $cond:expr) => {
        println!("TEST {} {}", stringify!($name), if $cond { "PASS" } else { "FAIL" });
    };
}

fn main() {
    let v = Vector::<4>::new([0.0, 2.0, 3.0, 4.0]);
    check!(test_v_vector_sum, (v.sum() - 9.0).abs() < 1e-9);
    check!(test_v_vector_dot_self, (v.dot(&v) - 29.0).abs() < 1e-9);
    check!(test_v_vector_add_zero, v.add(&Vector::<4>::new([0.0; 4])).data == v.data);
    check!(test_v_vector_scale_one, v.scale(1.0).data == v.data);

    check!(test_v_sum_even_balanced, sum_even(&[1, 1, 2]) == 2);
    check!(test_v_fold_count_first_nonmatch, fold_count(&[1, 2, 4], |x| x % 2 == 0) == 2);
    check!(test_v_apply_times_zero, apply_times(10, 0, |x| x + 1) == 10);
    check!(test_v_first_match_single, first_match(&[1, 3, 5], |x| *x > 3) == Some(2));

    let parts = [
        make_particle(3.0, 4.0, 0.0, 2.0, true),
        make_particle(0.0, 0.0, 0.0, 3.0, true),
    ];
    check!(test_v_total_mass_all_active, (total_active_mass(&parts) - 5.0).abs() < 1e-9);
    check!(test_v_mean_speed_two, (mean_speed(&parts) - 2.5).abs() < 1e-9);

    let soa = ParticleSoA {
        x: vec![3.0, 0.0, 1.0],
        y: vec![4.0, 0.0, 1.0],
        z: vec![0.0, 0.0, 0.0],
        mass: vec![2.0, 3.0, 0.0],
        active: vec![true, true, false],
    };
    check!(test_v_soa_mass_last_zero, (soa_mass(&soa) - 5.0).abs() < 1e-9);
    check!(test_v_soa_speed_z_zero, (soa_speed_sum(&soa) - 6.414213562373095).abs() < 1e-9);

    check!(test_v_bits_roundtrip, (bits_to_f32(f32_to_bits(1.5)) - 1.5).abs() < 1e-9);
    check!(test_v_sign_negative, sign_of_f64(-3.0));
    check!(test_v_reinterpret_small, reinterpret_u32_as_i32(7) == 7);
    check!(test_v_u64_bytes_zero, u64_from_le_bytes(u64_le_bytes(0)) == 0);

    check!(test_v_maybe_from_some, maybe_from(Some(5)) == MaybeU32::Some(5));
    check!(test_v_maybe_value_some, maybe_value(MaybeU32::Some(5)) == Some(5));
    check!(test_v_pack_option_some, pack_option(NonZeroU32::new(7)) == 7);
    check!(test_v_color_code_red, color_code(Color::Red) == 1);
    check!(test_v_color_from_code_one, color_from_code(1) == Some(Color::Red));

    check!(test_v_is_prime_small, is_prime(7) && is_prime(13));
    check!(test_v_count_primes_all, count_primes(&[2, 3, 5, 7]) == 4);
    check!(test_v_legacy_odd, legacy_is_odd_prime(9) && !legacy_is_odd_prime(2));
}
