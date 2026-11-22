# Contributing

Thanks for helping improve the harness. Please keep changes small and
measurable.

## Reporting a bug

Open an issue using the **Bug report** template. Include:

- the suite and question id or fixture version;
- the exact command and your port/model/quant/context;
- the expected and observed score;
- the result JSON and, if relevant, the reasoning file from `reasoning/`.

If a score is wrong because of a scorer bug, include a minimal reproducing
answer, not just the final number.

## Suggesting a feature

Use the **Feature request** template. Explain which comparison the change
enables and how you would verify it. New questions must include their answer
key, accepted aliases and a primary source or derivation.

## Pull requests

1. Fork and create a branch from `main` named `type/short-description`, e.g.
   `fix/trap-negation` or `question/new-swe-item`.
2. Keep one concern per PR. Do not change a scorer and add questions in the
   same PR.
3. Run the smoke commands in the relevant suite README (for example
   `python qa/open-ended/run_suite.py --port 8080 --dry-run`) and any scorer
   self-tests before opening the PR. There is no top-level `tests/` directory,
   so `python -m pytest tests` does not work in this repository.
4. If you change a scorer, state which historical scores change and by how
   much. Never silently re-score old baselines.
5. Fill in the pull request template, including validation and anything you
   did **not** run.

## Coding standards

- Python 3.10+, standard library where possible.
- No absolute paths, no embedded keys, no hardcoded ports.
- User-facing output must show progress and a final score.
- Every new runner must write one reasoning file per question.
- Keep the "not official benchmark" disclaimers in place.

## Questions and answer keys

- Each question needs a stable `id`, `category`, `type`, `q`, `answer` and
  `accept` list.
- Rubric patterns must be specific. A pattern that matches every string is a
  bug.
- Trap questions must be self-contained; do not refer to a previous question.
- Integer answers must compare exactly; do not use percentage tolerance on an
  integer key.
