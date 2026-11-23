# Changelog

All notable changes to this project are documented here. This file follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project does
not yet use semantic versioning.

## [Unreleased]

### Added
- `repair/v7/`: a deliberately hard MiniVM repair fixture in Python, C++,
  JavaScript and Rust, generated from one canonical manifest
  (`repair/v7-tests.json`). It adds masked cascading faults, deterministic
  fibers and a checksummed snapshot format, with 45 visible examples, 49 hidden
  tests and three performance gates per language. See `docs/V7-DESIGN.md`.
- Initial public staging of the harness: QA suites, repair fixtures in Python,
  C++, JavaScript and Rust, BrowseComp-style research sets and historical
  results.
- Apache-2.0 license, contribution guide, security policy, issue and PR
  templates, CI workflow and repository hygiene files.
- Standalone QA runners with user-supplied port, live progress, final score and
  one Markdown reasoning file per question.

### Fixed
- Open-ended suite: removed a tautological rubric pattern in `OPEN-EE-03` that
  awarded a free point to every model.
- Open-ended suite: made `TRAP-02` self-contained; it previously referred to
  a previous question that is not sent on an independent API call.
- Open-ended suite: a model that names a trap value while explicitly rejecting
  it is no longer failed.
- Open-ended suite: narrowed over-broad rubric patterns in `OPEN-BIO-04`,
  `OPEN-CS-01`, `OPEN-EE-01` and the two history items; removed a too-loose
  `0.22` alias from `TRAP-04`; tightened non-integer numeric tolerance to 0.1%.
- Repository hygiene: removed ~78 generated transcripts and usage files that
  contained a personal path and third-party snippets; tightened `.gitignore`
  and the CI secret scan to cover `.txt` files.
- Fixed-answer suites: integer answer keys now compare exactly instead of using
  a 1% tolerance that accepted neighbouring integers. Applied to the open-ended
  and both closed-book runners.
- Open-ended suite: `--compare` now expands glob patterns instead of treating
  them as a literal filename.
- Closed-book suite: the original hard evaluator concatenated response and
  reasoning before extracting `ANSWER:`; the shipped runner uses content only.
- Craft scorer: removed an invalid subtraction of `w:bCs`/`w:iCs` counts that
  falsely failed correctly bold/italic documents; raised the font threshold to
  the required 16 pt.
- BrowseComp: stale README corrected to reflect the recorded 9/10 run, with its
  low-tool-call caveats; legacy runners no longer contain absolute tool paths.

### Changed
- The direct-HTTP QA runners now ask the user to supply a port (interactive
  prompt or `--port`) instead of defaulting to a fixed one; pressing Enter at
  the prompt still selects 8080. Agent-harness and cloud-API runners use their
  own configuration.
- Historical reports are labelled as single-machine observations with known
  caveats rather than a leaderboard.

## [historical]

The original local tree was reorganised on 2026-11-19. Question sets were
expanded over time while folder names were kept for traceability:
`easy-mixed-12` now has 20 questions, `hard-mixed-20` has 30, and the unified
suite has 96 default questions (106 with BrowseComp).
