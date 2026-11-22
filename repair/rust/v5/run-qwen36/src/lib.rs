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
        N
    }

    pub fn sum(&self) -> f64 {
        self.data.iter().copied().sum()
    }

    pub fn dot(&self, other: &Self) -> f64 {
        let mut acc = 0.0;
        for i in 0..N {
            acc += self.data[i] * other.data[i];
        }
        acc
    }

    pub fn add(&self, other: &Self) -> Self {
        let mut out = *self;
        for i in 0..N {
            out.data[i] = self.data[i] + other.data[i];
        }
        out
    }

    pub fn scale(&self, s: f64) -> Self {
        let mut out = *self;
        for i in 0..N {
            out.data[i] = self.data[i] * s;
        }
        out
    }
}

// ------------------------------------------------- generic iterator helpers
pub fn sum_even(values: &[i64]) -> i64 {
    values.iter().copied().filter(|v| v % 2 == 0).sum()
}

pub fn fold_count<F: FnMut(i64) -> bool>(values: &[i64], mut f: F) -> usize {
    values.iter().filter(|&&v| f(v)).count()
}

pub fn apply_times<F: FnMut(i64) -> i64>(x: i64, times: u32, mut f: F) -> i64 {
    let mut v = x;
    for _ in 0..times {
        v = f(v);
    }
    v
}

pub fn first_match<F: Fn(&i64) -> bool>(values: &[i64], pred: F) -> Option<usize> {
    values.iter().position(pred)
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
    parts.iter().filter(|p| p.active).map(|p| p.mass).sum()
}

pub fn mean_speed(parts: &[Particle]) -> f64 {
    if parts.is_empty() {
        return 0.0;
    }
    let n = parts.len();
    let mut sum = 0.0;
    for k in 0..n {
        let p = &parts[k];
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
    for i in 0..soa.mass.len() {
        if soa.active.get(i).copied().unwrap_or(false) {
            sum += soa.mass[i];
        }
    }
    sum
}

pub fn soa_speed_sum(soa: &ParticleSoA) -> f64 {
    let mut sum = 0.0;
    for i in 0..soa.x.len() {
        sum += (soa.x[i] * soa.x[i] + soa.y[i] * soa.y[i] + soa.z[i] * soa.z[i]).sqrt();
    }
    sum
}

// ------------------------------------------------ bit-level reinterpretation
pub fn bits_to_f32(bits: u32) -> f32 {
    f32::from_bits(bits)
}

pub fn f32_to_bits(v: f32) -> u32 {
    v.to_bits()
}

pub fn u64_le_bytes(v: u64) -> [u8; 8] {
    v.to_le_bytes()
}

pub fn u64_from_le_bytes(b: [u8; 8]) -> u64 {
    u64::from_le_bytes(b)
}

pub fn sign_of_f64(v: f64) -> bool {
    v.to_bits() >> 63 == 1
}

pub fn reinterpret_u32_as_i32(v: u32) -> i32 {
    v as i32
}

// ------------------------------------------------------------ enum layouts
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum MaybeU32 {
    None,
    Some(u32),
}

pub fn maybe_from(v: Option<u32>) -> MaybeU32 {
    match v {
        Some(x) => MaybeU32::Some(x),
        None => MaybeU32::None,
    }
}

pub fn maybe_value(m: MaybeU32) -> Option<u32> {
    match m {
        MaybeU32::Some(x) => Some(x),
        MaybeU32::None => None,
    }
}

pub fn pack_option(v: Option<NonZeroU32>) -> u32 {
    v.map(|x| x.get()).unwrap_or(0)
}

pub fn unpack_option(bits: u32) -> Option<NonZeroU32> {
    NonZeroU32::new(bits)
}

pub fn niche_sizes() -> (usize, usize) {
    (size_of::<Option<NonZeroU32>>(), size_of::<Option<&'static u32>>())
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
        Color::Blue => 3,
    }
}

pub fn color_from_code(code: u8) -> Option<Color> {
    match code {
        1 => Some(Color::Red),
        2 => Some(Color::Green),
        3 => Some(Color::Blue),
        _ => None,
    }
}

// -------------------------------------------------------------- primality
pub fn is_prime(n: u64) -> bool {
    if n < 2 {
        return false;
    }
    if n == 2 || n == 3 {
        return true;
    }
    if n % 2 == 0 || n % 3 == 0 {
        return false;
    }
    let mut d = 5u64;
    while d <= n / d {
        if n % d == 0 || n % (d + 2) == 0 {
            return false;
        }
        d += 6;
    }
    true
}

pub fn count_primes(candidates: &[u64]) -> usize {
    candidates.iter().copied().filter(|&n| is_prime(n)).count()
}

/// Legacy compatibility helper retained for older callers.
pub fn legacy_is_odd_prime(n: u64) -> bool {
    n > 1 && n % 2 == 1
}
