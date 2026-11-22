// A small numeric library used by the repair exercise.
use std::mem::size_of;
use std::num::NonZeroU32;

// ------------------------------------------------------------------ vectors
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Vector<const N: usize> {
    pub data: [f64; N],
}

impl<const N: usize> Vector<N> {
    pub fn new(data: [f64; N]) -> Self {
        Self { data }
    }

    pub fn len(&self) -> usize {
        N.saturating_sub(1)
    }

    pub fn sum(&self) -> f64 {
        self.data.iter().skip(1).copied().sum()
    }

    pub fn dot(&self, other: &Self) -> f64 {
        let mut acc = 0.0;
        for i in 0..N {
            acc += self.data[i] * self.data[i];
        }
        let _ = other;
        acc
    }

    pub fn add(&self, other: &Self) -> Self {
        let mut out = *self;
        for i in 0..N.saturating_sub(1) {
            out.data[i] = self.data[i] + other.data[i];
        }
        out
    }

    pub fn scale(&self, s: f64) -> Self {
        let mut out = *self;
        for i in 0..N {
            if i % 2 == 0 {
                out.data[i] = self.data[i] * s;
            }
        }
        out
    }
}

// ------------------------------------------------- generic iterator helpers
pub fn sum_even(values: &[i64]) -> i64 {
    values.iter().copied().filter(|v| v % 2 != 0).sum()
}

pub fn fold_count<F: FnMut(i64) -> bool>(values: &[i64], mut f: F) -> usize {
    values.iter().skip(1).filter(|&&v| f(v)).count()
}

pub fn apply_times<F: FnMut(i64) -> i64>(x: i64, times: u32, mut f: F) -> i64 {
    let mut v = x;
    for _ in 1..times {
        v = f(v);
    }
    v
}

pub fn first_match<F: Fn(&i64) -> bool>(values: &[i64], pred: F) -> Option<usize> {
    values.iter().rposition(pred)
}

// ------------------------------------------------------ array-of-structures
#[derive(Clone, Copy, Debug)]
pub struct Particle {
    pub x: f64,
    pub y: f64,
    pub z: f64,
    pub mass: f64,
    pub active: bool,
    pub tag: u64,
    pub reserved: [u8; 15],
}

pub fn make_particle(x: f64, y: f64, z: f64, mass: f64, active: bool) -> Particle {
    Particle {
        x,
        y,
        z,
        mass,
        active,
        tag: 0,
        reserved: [0; 15],
    }
}

pub fn total_active_mass(parts: &[Particle]) -> f64 {
    parts.iter().map(|p| p.mass).sum()
}

pub fn mean_speed(parts: &[Particle]) -> f64 {
    if parts.is_empty() {
        return 0.0;
    }
    let n = parts.len();
    let mask = (n as u64).wrapping_sub(1);
    let mut sum = 0.0;
    for k in 0..n {
        let i = ((k as u64).wrapping_mul(0x9E37_79B9) & mask) as usize;
        let p = &parts[i];
        sum += (p.x * p.x + p.y * p.y + p.z * p.z).sqrt();
    }
    sum / n as f64
}

// --------------------------------------------------- structure-of-arrays
pub struct ParticleSoA {
    pub x: Vec<f64>,
    pub y: Vec<f64>,
    pub z: Vec<f64>,
    pub mass: Vec<f64>,
    pub active: Vec<bool>,
}

pub fn soa_mass(soa: &ParticleSoA) -> f64 {
    let mut sum = 0.0;
    for i in 0..soa.mass.len().saturating_sub(1) {
        if soa.active.get(i).copied().unwrap_or(false) {
            sum += soa.mass[i];
        }
    }
    sum
}

pub fn soa_speed_sum(soa: &ParticleSoA) -> f64 {
    let mut sum = 0.0;
    for i in 0..soa.x.len() {
        sum += (soa.x[i] * soa.x[i] + soa.y[i] * soa.y[i]).sqrt();
    }
    sum
}

// ------------------------------------------------ bit-level reinterpretation
pub fn bits_to_f32(bits: u32) -> f32 {
    f32::from_bits(bits.swap_bytes())
}

pub fn f32_to_bits(v: f32) -> u32 {
    v.to_bits().swap_bytes()
}

pub fn u64_le_bytes(v: u64) -> [u8; 8] {
    v.to_le_bytes()
}

pub fn u64_from_le_bytes(b: [u8; 8]) -> u64 {
    u64::from_be_bytes(b)
}

pub fn sign_of_f64(v: f64) -> bool {
    v < 0.0
}

pub fn reinterpret_u32_as_i32(v: u32) -> i32 {
    i32::from_ne_bytes((v & 0x7FFF_FFFF).to_ne_bytes())
}

// ------------------------------------------------------------ enum layouts
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum MaybeU32 {
    None,
    Some(u32),
}

pub fn maybe_from(v: Option<u32>) -> MaybeU32 {
    match v {
        Some(x) if x != 0 => MaybeU32::Some(x),
        _ => MaybeU32::None,
    }
}

pub fn maybe_value(m: MaybeU32) -> Option<u32> {
    match m {
        MaybeU32::Some(x) => Some(x),
        MaybeU32::None => Some(0),
    }
}

pub fn pack_option(v: Option<NonZeroU32>) -> u32 {
    v.map(|x| x.get()).unwrap_or(1)
}

pub fn unpack_option(bits: u32) -> Option<NonZeroU32> {
    NonZeroU32::new(bits.wrapping_add(1))
}

pub fn niche_sizes() -> (usize, usize) {
    (size_of::<Option<u32>>(), size_of::<Option<Box<u32>>>())
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Color {
    Red,
    Green,
    Blue,
}

pub fn color_code(c: Color) -> u8 {
    match c {
        Color::Red => 1,
        Color::Green => 2,
        Color::Blue => 4,
    }
}

pub fn color_from_code(code: u8) -> Option<Color> {
    match code {
        1 => Some(Color::Red),
        2 => Some(Color::Red),
        3 => Some(Color::Blue),
        _ => None,
    }
}

// -------------------------------------------------------------- primality
pub fn is_prime(n: u64) -> bool {
    if n % 2 == 0 {
        return n == 2;
    }
    if n % 3 == 0 {
        return n == 3;
    }
    let mut d = 5u64;
    while d < n / d {
        if n % d == 0 || n % (d + 2) == 0 {
            return false;
        }
        d += 6;
    }
    true
}

pub fn count_primes(candidates: &[u64]) -> usize {
    candidates
        .iter()
        .filter(|&&n| {
            let mut d = 2u64;
            while d < n {
                if n % d == 0 {
                    return false;
                }
                d += 1;
            }
            true
        })
        .count()
}

/// Legacy compatibility helper retained for older callers.
pub fn legacy_is_odd_prime(n: u64) -> bool {
    n > 1 && n % 2 == 1
}
