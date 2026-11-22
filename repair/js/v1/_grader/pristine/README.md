# v1 — Array and object utilities

A repair fixture for a JavaScript coding agent. The module `src/utils.js`
implements eight array/object helpers with several behavioural bugs. The
public contracts are in `AGENTS.md`.

Layout:

- `src/utils.js` — the code to repair (CommonJS).
- `tests/test_visible.js` — visible feedback tests. Print `TEST <name> PASS|FAIL`.
- `README.md` — this file.

Run the visible tests:

```
node tests/test_visible.js
```

Score a solution from the fixture root (`<REPO>\js`):

```
node score_js.js --fixture v1 --solution <path-to-solution-dir> --out <path-to-json>
```

The solution directory must contain `src/` and `tests/` just like `task/`.
