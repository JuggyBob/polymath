'use strict';

/* Recursive-descent parser: token stream -> AST. */

const { tokenize } = require('./lexer.js');

class ParseError extends Error {
  constructor(msg, pos) { super(msg + ' at ' + pos); this.pos = pos; }
}

class Parser {
  constructor(tokens) { this.tokens = tokens; this.i = 0; }

  peek() { return this.tokens[this.i]; }
  at(type) { return this.peek().type === type; }
  take(type) {
    const t = this.peek();
    if (t.type !== type) throw new ParseError('expected ' + type + ', got ' + t.type, t.pos);
    this.i++;
    return t;
  }
  match(type) {
    if (this.at(type)) { this.i++; return true; }
    return false;
  }

  parseProgram() {
    const body = [];
    while (!this.at('EOF')) body.push(this.statement());
    return body;
  }

  statement() {
    if (this.at('LET')) {
      this.i++;
      const name = this.take('ID').value;
      this.take('ASSIGN');
      const expr = this.expression();
      this.take('SEMI');
      return { k: 'let', name, expr };
    }
    if (this.at('PRINT')) {
      this.i++;
      const expr = this.expression();
      this.take('SEMI');
      return { k: 'print', expr };
    }
    if (this.at('IF')) return this.ifStatement();
    if (this.at('WHILE')) {
      this.i++;
      const cond = this.expression();
      const body = this.block();
      return { k: 'while', cond, body };
    }
    if (this.at('ID') && this.isAssignmentAhead()) {
      const target = this.postfix();
      this.take('ASSIGN');
      const expr = this.expression();
      this.take('SEMI');
      return { k: 'assign', target, expr };
    }
    const expr = this.expression();
    this.take('SEMI');
    return { k: 'expr', expr };
  }

  ifStatement() {
    this.take('IF');
    const cond = this.expression();
    const then = this.block();
    let otherwise = [];
    if (this.match('ELSE')) otherwise = this.block();
    return { k: 'if', cond, then, otherwise };
  }

  isAssignmentAhead() {
    let j = this.i;
    let depth = 0;
    while (j < this.tokens.length) {
      const t = this.tokens[j].type;
      if (t === 'LS' || t === 'LP') depth++;
      else if (t === 'RS' || t === 'RP') depth--;
      else if (depth === 0 && t === 'ASSIGN') return true;
      else if (depth === 0 && (t === 'SEMI' || t === 'EOF')) return false;
      j++;
    }
    return false;
  }

  block() {
    this.take('LB');
    const body = [];
    while (!this.at('RB')) {
      if (this.at('EOF')) throw new ParseError('unterminated block', this.peek().pos);
      body.push(this.statement());
    }
    this.take('RB');
    return body;
  }

  expression() { return this.orExpr(); }

  orExpr() {
    let left = this.andExpr();
    while (this.match('OR')) left = { k: 'bin', op: '||', l: left, r: this.andExpr() };
    return left;
  }

  andExpr() {
    let left = this.eqExpr();
    while (this.match('AND')) left = { k: 'bin', op: '&&', l: left, r: this.eqExpr() };
    return left;
  }

  eqExpr() {
    let left = this.relExpr();
    while (this.at('EQ') || this.at('NEQ')) {
      const op = this.peek().type === 'EQ' ? '==' : '!=';
      this.i++;
      left = { k: 'bin', op, l: left, r: this.relExpr() };
    }
    return left;
  }

  relExpr() {
    let left = this.addExpr();
    while (this.at('LT') || this.at('LE') || this.at('GT') || this.at('GE')) {
      const t = this.peek();
      const op = t.type === 'LT' ? '<' : t.type === 'LE' ? '<=' : t.type === 'GT' ? '>' : '>=';
      this.i++;
      left = { k: 'bin', op, l: left, r: this.addExpr() };
    }
    return left;
  }

  addExpr() {
    let left = this.mulExpr();
    while (this.at('PLUS') || this.at('MINUS')) {
      const op = this.peek().type === 'PLUS' ? '+' : '-';
      this.i++;
      left = { k: 'bin', op, l: left, r: this.mulExpr() };
    }
    return left;
  }

  mulExpr() {
    let left = this.unary();
    while (this.at('STAR') || this.at('SLASH') || this.at('PERCENT')) {
      const t = this.peek();
      const op = t.type === 'STAR' ? '*' : t.type === 'SLASH' ? '/' : '%';
      this.i++;
      left = { k: 'bin', op, l: left, r: this.unary() };
    }
    return left;
  }

  unary() {
    if (this.match('MINUS')) return { k: 'un', op: '-', e: this.unary() };
    if (this.match('NOT')) return { k: 'un', op: '!', e: this.unary() };
    return this.postfix();
  }

  postfix() {
    let e = this.primary();
    while (this.match('LS')) {
      const idx = this.expression();
      this.take('RS');
      e = { k: 'idx', a: e, i: idx };
    }
    return e;
  }

  primary() {
    const t = this.peek();
    if (t.type === 'NUM') { this.i++; return { k: 'num', v: t.value }; }
    if (t.type === 'STR') { this.i++; return { k: 'str', v: t.value }; }
    if (t.type === 'TRUE') { this.i++; return { k: 'bool', v: true }; }
    if (t.type === 'FALSE') { this.i++; return { k: 'bool', v: false }; }
    if (t.type === 'NULL') { this.i++; return { k: 'null' }; }
    if (t.type === 'ID') { this.i++; return { k: 'id', name: t.value }; }
    if (t.type === 'DISTINCT') {
      this.i++;
      const e = this.unary();
      return { k: 'distinct', e };
    }
    if (t.type === 'LEN') {
      this.i++;
      const e = this.unary();
      return { k: 'len', e };
    }
    if (this.match('LP')) {
      const e = this.expression();
      this.take('RP');
      return e;
    }
    if (this.match('LS')) {
      const items = [];
      if (!this.at('RS')) {
        items.push(this.expression());
        while (this.match('COMMA')) items.push(this.expression());
      }
      this.take('RS');
      return { k: 'arr', items };
    }
    throw new ParseError('unexpected token ' + t.type, t.pos);
  }
}

function parse(input) {
  const tokens = Array.isArray(input) ? input : tokenize(input);
  return new Parser(tokens).parseProgram();
}

module.exports = { parse, ParseError };
