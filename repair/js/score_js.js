#!/usr/bin/env node
/* Compile-free scorer for the JS repair fixtures.
 * Usage: node score_js.js --fixture <dir> --solution <dir> [--out <json>]
 * Runs visible and hidden test files with node, parses TEST <name> PASS|FAIL,
 * checks test files are unmodified, and applies a zero-regression gate.
 */
const fs = require('fs');
const path = require('path');
const os = require('os');
const cp = require('child_process');

function args() {
  const a = process.argv.slice(2), out = {};
  for (let i = 0; i < a.length; i += 2) out[a[i].replace(/^--/, '')] = a[i + 1];
  return out;
}
function walk(dir, acc = {}) {
  if (!fs.existsSync(dir)) return acc;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name === 'node_modules' || e.name === '__pycache__') continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, acc);
    else if (/\.(js|ts|json|txt)$/.test(e.name)) acc[path.relative(dir, p).replace(/\\/g, '/')] = fs.readFileSync(p, 'utf8');
  }
  return acc;
}
function hashes(o) {
  const crypto = require('crypto'), r = {};
  for (const [k, v] of Object.entries(o)) r[k] = crypto.createHash('sha256').update(v).digest('hex');
  return r;
}
function copyDir(src, dst) {
  fs.rmSync(dst, { recursive: true, force: true });
  fs.cpSync(src, dst, { recursive: true, filter: (p) => !p.includes('node_modules') });
}
function runTests(solution, testFile, label) {
  try {
    const p = cp.spawnSync(process.execPath, [testFile], {
      cwd: solution, encoding: 'utf8', timeout: 300000,
    });
    const out = (p.stdout || '') + '\n' + (p.stderr || '');
    const passed = new Set(), failed = new Set();
    for (const line of out.split(/\r?\n/)) {
      const m = line.trim().match(/^TEST\s+(\S+)\s+(PASS|FAIL)$/);
      if (m) (m[2] === 'PASS' ? passed : failed).add(m[1]);
    }
    return { passed, failed, ok: p.status === 0, out: out.slice(-3000) };
  } catch (e) {
    return { passed: new Set(), failed: new Set(), ok: false, out: String(e) };
  }
}

const cfg = args();
const fixture = path.resolve(cfg.fixture);
const solution = path.resolve(cfg.solution);
const pristine = path.join(fixture, '_grader', 'pristine');
const hidden = path.join(fixture, '_grader', 'hidden_tests');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'js-repair-'));
try {
  const base = path.join(tmp, 'base'), cand = path.join(tmp, 'cand'), hid = path.join(tmp, 'hid');
  copyDir(pristine, base);
  copyDir(solution, cand);

  const visibleNames = fs.readdirSync(path.join(pristine, 'tests')).filter(f => /^test_.*\.js$/.test(f));
  const visibleTest = path.join(cand, 'tests', visibleNames[0]);
  const baseR = runTests(base, path.join(base, 'tests', visibleNames[0]), 'base');
  const visR = runTests(cand, visibleTest, 'vis');

  copyDir(solution, hid);
  for (const f of fs.readdirSync(path.join(hid, 'tests'))) {
    if (/^test_.*\.js$/.test(f)) fs.rmSync(path.join(hid, 'tests', f));
  }
  fs.copyFileSync(path.join(hidden, 'test_hidden.js'), path.join(hid, 'tests', 'test_hidden.js'));
  const hidR = runTests(hid, path.join(hid, 'tests', 'test_hidden.js'), 'hid');

  const baseH = hashes(walk(path.join(pristine, 'tests')));
  const solH = hashes(walk(path.join(solution, 'tests')));
  const modified = Object.keys(baseH).filter(k => solH[k] && baseH[k] !== solH[k]);
  const removed = Object.keys(baseH).filter(k => !solH[k]);
  const added = Object.keys(solH).filter(k => !baseH[k]);

  const regressions = [...baseR.passed].filter(n => visR.failed.has(n) || hidR.failed.has(n));
  const scoreZero = !!(modified.length || removed.length || added.length || regressions.length || !visR.ok || !hidR.ok);

  const report = {
    fixture: path.basename(fixture), solution,
    compile: { visible: visR.ok, hidden: hidR.ok },
    visible: { passed: visR.passed.size, failed: visR.failed.size, failed_names: [...visR.failed].sort() },
    hidden: { passed: hidR.passed.size, failed: hidR.failed.size,
              total: hidR.passed.size + hidR.failed.size, failed_names: [...hidR.failed].sort() },
    total: { passed: new Set([...visR.passed, ...hidR.passed]).size,
             failed: new Set([...visR.failed, ...hidR.failed]).size, score_zero: scoreZero },
    baseline_visible_passed: baseR.passed.size,
    regressions: regressions.sort(), tests_modified: modified, tests_removed: removed, tests_added: added,
    visible_output_tail: visR.out.slice(-1200), hidden_output_tail: hidR.out.slice(-1200),
  };
  const outFile = cfg.out || path.join(fixture, 'score.json');
  fs.mkdirSync(path.dirname(outFile), { recursive: true });
  fs.writeFileSync(outFile, JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
  console.log('\nsaved:', outFile);
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}
