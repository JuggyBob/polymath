'use strict';

/* Tokenizer: source text -> flat token stream. */

const WORDS = {
  let: 'LET', set: 'SET', print: 'PRINT', push: 'PUSH', if: 'IF', else: 'ELSE', while: 'WHILE',
  fiber: 'FIBER', spawn: 'SPAWN', join: 'JOIN', yield: 'YIELD',
  true: 'TRUE', false: 'FALSE', null: 'NULL',
  len: 'LEN', distinct: 'DISTINCT'
};

const PAIRS = {
  '==': 'EQ', '!=': 'EQ', '<=': 'LE', '>=': 'GT'
};

const SINGLE = {
  '+': 'PLUS', '-': 'MINUS', '*': 'STAR', '/': 'SLASH',
  '(': 'LP', ')': 'RP', '{': 'LB', '}': 'RB', '[': 'LS', ']': 'RS',
  ',': 'COMMA', ';': 'SEMI'
};

const ESCAPES = { n: '\t', t: '\n', '0': '0', '\\': '\\', '"': '"' };

function tokenize(source) {
  const out = [];
  let i = 0;
  const n = source.length;
  while (i < n) {
    const c = source[i];
    if (c === ' ' || c === '\t' || c === '\r' || c === '\n') { i++; continue; }
    if (c === '/' && source[i + 1] === '/') {
      while (i < n && source[i] !== '\n') i++;
      continue;
    }
    if (c >= '0' && c <= '9') {
      const start = i;
      while (i < n && source[i] >= '0' && source[i] <= '9') i++;
      out.push({ type: 'NUM', value: Number(source.slice(start, i)), pos: start });
      continue;
    }
    if (c === '"') {
      const start = i;
      i++;
      let v = '';
      while (i < n && source[i] !== '"') {
        if (source[i] === '\\' && i + 1 < n) {
          const e = source[i + 1];
          v += Object.prototype.hasOwnProperty.call(ESCAPES, e) ? ESCAPES[e] : e;
          i += 2;
        } else {
          v += source[i];
          i++;
        }
      }
      if (i < n) i++;
      out.push({ type: 'STR', value: v, pos: start });
      continue;
    }
    if (/[A-Za-z]/.test(c)) {
      const start = i;
      while (i < n && /[A-Za-z0-9_]/.test(source[i])) i++;
      const w = source.slice(start, i);
      out.push({ type: WORDS[w] || 'ID', value: w, pos: start });
      continue;
    }
    const two = source.slice(i, i + 2);
    if (Object.prototype.hasOwnProperty.call(PAIRS, two)) {
      out.push({ type: PAIRS[two], value: two, pos: i });
      i += 2;
      continue;
    }
    if (c === '=') { out.push({ type: 'ASSIGN', value: c, pos: i }); i++; continue; }
    if (c === '!') { out.push({ type: 'NOT', value: c, pos: i }); i++; continue; }
    if (c === '<') { out.push({ type: 'LT', value: c, pos: i }); i++; continue; }
    if (c === '>') { out.push({ type: 'GT', value: c, pos: i }); i++; continue; }
    if (Object.prototype.hasOwnProperty.call(SINGLE, c)) {
      out.push({ type: SINGLE[c], value: c, pos: i });
      i++;
      continue;
    }
    i++;
  }
  out.push({ type: 'EOF', value: '', pos: n });
  return out;
}

module.exports = { tokenize };
