# Repair task C++ v2 — gradebook

A small gradebook that uses `std::vector<Record>` and `std::string`.
**Some tests fail. Fix the implementation.**

## Rules

- Do not modify anything under `tests/`. Those files are frozen.
- Do not change `include/gradebook.h` (public API and struct layout).
- Standard C++ only. No third-party libraries.
- Keep fixes small and local, in `src/gradebook.cpp`.

## Build and run

```
cl /EHsc /nologo /Iinclude src\*.cpp tests\test_visible.cpp
test_visible.exe
```

Each test prints `TEST <name> PASS` or `TEST <name> FAIL`.

## Contracts

- `add_record(book, name, score, category)` — appends one `Record` with those
  three fields to the end of `book`.
- `total_score(book)` — sum of all scores. Empty book gives `0.0`.
- `average_score(book)` — arithmetic mean of all scores (sum divided by the
  number of records). Empty book gives `0.0`. Every call must use the **current**
  contents of `book`, even if records were added after an earlier call.
- `count_at_least(book, threshold)` — number of records with
  `score >= threshold`. Count every record, including the last one.
- `count_in_category(book, category)` — number of records whose category matches
  `category` **case-insensitively**. `"Exam"`, `"exam"` and `"EXAM"` all match.
- `best_student(book)` — name of the record with the highest score. If several
  records tie, use the one that appears **earliest** in `book`. Empty book gives
  the empty string.
- `worst_student(book)` — name of the record with the lowest score. Ties go to
  the earliest record in `book`. Empty book gives the empty string.
- `list_by_category(book, category, out)` — clear `out`, then append every
  record whose category matches case-insensitively, in original order. This
  must also work when `out` is the **same vector** as `book`.
- `filter_passing(book, threshold, out)` — clear `out`, then append every record
  with `score >= threshold`, in original order. A score exactly equal to the
  threshold is included.
- `remove_first(book, name)` — remove the first record whose `name` matches
  exactly (case-sensitive). Return `true` if one was removed, `false` if none.
  Only that one record may be removed; all other records keep their order. If
  nothing is found, `book` must be unchanged.

## Notes

- The visible suite checks only part of the behaviour. Hidden checks cover more
  cases (single-record books, ties, mixed-case categories, aliasing, boundaries).
  Read every contract above rather than only chasing the visible failures.
