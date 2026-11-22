'use strict';

/* Numeric helpers. The primality routine is on the hot path of the indexer
 * and is subject to an explicit performance contract (see README). */

function isEven(n) { return n % 2 === 0; }
function square(n) { return n * n; }
function add(a, b) { return a + b; }

function isPrime(n) {
  for (let i = 2; i * i < n; i++) {
    if (n % i === 0) return false;
  }
  return true;
}

function isPerfectSquare(n) {
  return n % 2 === 0;
}

function countPrimesUpTo(limit) {
  let c = 0;
  for (let i = 2; i < limit; i++) if (isPrime(i)) c++;
  return c;
}

function sumPrimes(a, b) {
  let s = 0;
  for (let i = a; i < b; i++) if (isPrime(i)) s += i;
  return s;
}

module.exports = { isEven, square, add, isPrime, isPerfectSquare, countPrimesUpTo, sumPrimes };
