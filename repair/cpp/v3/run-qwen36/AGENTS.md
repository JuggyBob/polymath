# Repair task C++ v3 — string map and owned buffer

Two small classes, both built from raw pointers.
**Some tests fail. Fix the code.**

## Rules

- Do not modify anything under `tests/`. Those files are frozen.
- Do not change `include/map.h` (public API, member layout and struct layout).
- Standard C++ only. No third-party libraries.
- Keep fixes small and local. Do not rewrite the whole design.
- You may not add or remove source files under `src/`.

## Build and run

```
cl /EHsc /nologo /Od /Iinclude src\*.cpp tests\test_visible.cpp
test_visible.exe
```

The grader compiles the same way and also links the hidden test against your
`src/*.cpp` and `include/map.h`.

## Background: open addressing

`StringMap` keeps an array of `Entry` slots called *buckets*.
Each bucket is `EMPTY` (never used), `OCCUPIED`, or `TOMB` (a removed entry).
To place or find a key, start at its home slot and walk forward one slot at a
time. When you walk past the last slot you wrap around to slot 0 and keep
going. Stop when you reach an `EMPTY` slot: the key is not in the table.

A `TOMB` slot is **not** `EMPTY`. It may be reused by a later insert, but a
lookup must walk past it. Otherwise a key stored after a tombstone becomes
unreachable.

## Contracts

### Hashing

```
hash_key(key):
    h = 2166136261u                       (32-bit unsigned)
    for each character c of key:
        h = (h XOR c) * 16777619u          (unsigned 32-bit wraparound)
    return h

home_slot(key, cap) = hash_key(key) % cap
```

Use the character value as an unsigned byte. Worked values (decimal):

| key      | hash_key(key) | home_slot(cap 8) | home_slot(cap 16) |
|----------|---------------|------------------|-------------------|
| `""`     | 2166136261    | 5                | 5                 |
| `"a"`    | 3826002220    | 4                | 12                |
| `"cat"`  | 108289031     | 7                | 7                 |
| `"Apple"`| 3061292127    | 7                | 15                |
| `"alpha"`| 1569418667    | 3                | 11                |

`"cat"` and `"Apple"` both start at slot 7 when `cap == 8`. Whichever is
inserted second must go to slot 0, because probing wraps around.

### Keys and duplicates (tie behaviour)

Keys are **case-sensitive**: `"Cat"` and `"cat"` are two different keys.
`insert` on a key that is already present (a tie) **overwrites the value in
place**. It does not add a second entry and it does not change `size()`.
`contains` and `get` use the same case-sensitive comparison.

### Resizing

The table starts at `capacity() == 8`.
Before inserting a brand-new key, if `used + 1 > cap * 3 / 4` (where `used` is
the number of occupied slots plus tombstones), grow the table to exactly
`cap * 2` capacity and reinsert every occupied entry into the new table.
Updating an existing value never grows the table.

Worked example: with an empty table, the first 6 inserts keep capacity 8.
The 7th distinct key grows capacity to 16. All 7 keys are still present after
the growth.

### Removal and size

`remove(key)` returns true when the key was present and false otherwise.
A removed slot becomes a `TOMB`, never `EMPTY`. `size()` counts only occupied
slots, so it drops by exactly one per successful removal and is unchanged by a
failed removal. `tombstones()` counts the `TOMB` slots and is zero for a fresh
table.

Removing an entry from the middle of a probe chain must not make the entries
after it unreachable. Inserting a new key may reuse a tombstone; doing so must
not disturb any other key.

### Buffer (rule of three)

`Buffer` owns exactly one dynamic `int` array with `count` elements.
`Buffer()` creates an empty buffer. `Buffer(values, n)` copies `n` ints.
`get(i)` / `set(i, v)` access element `i`, with `0 <= i < count`.

- The copy constructor makes a **separate** array with the same values.
- Assignment makes a separate array too, and releases the old one.
- Self-assignment (`b = b`) must leave the buffer unchanged and must not free
  its storage.
- The destructor releases the array it owns.

Each allocation must be paired with exactly one matching deallocation. The
tests count live `new[]` allocations, so both a missing delete and a double
delete are visible.

## What to look for

Read every contract above before editing. The visible tests are only a subset
of the checks. Expect bugs in pointer/index arithmetic, in the hash update,
in tombstone handling, in probing and growth, in removal bookkeeping, and in
the rule of three.
