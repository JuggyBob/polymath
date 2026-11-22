# Repair task

You are given a small JavaScript package in `src/`. Several functions behave
incorrectly. Your job is to fix the source files so that all behaviour matches
the documentation in this folder.

## Rules

- Edit only files under `src/`. Do not change `tests/` or add new files.
- Run the visible tests with `node tests/test_visible.js`. Each test prints
  `TEST <name> PASS` or `TEST <name> FAIL`.
- Hidden tests check the same public API more thoroughly. A correct fix must
  satisfy them as well.
- Use the `module.exports` names that are already present. Do not rename them.
- Keep the runtime at Node 24 and stay in CommonJS.

## What to look for

The code in `src/` has comments that point at suspicious lines. The problems
are in these areas:

- methods that lose their `this` receiver when extracted or passed as a callback
- prototype chains that are shared instead of inherited
- generators that are consumed once or that yield the wrong thing
- arrays and objects copied shallowly when a real copy is required
- `delete` replaced by assigning `undefined`
- loose (`==`) equality where strict (`===`) equality is required

Make the smallest change that fixes the documented behaviour. Do not change
unrelated code.
