'use strict';

const { Greeter, hasProperty, Parent, Child, invoke } = require('../src/objects.js');
const { getSequence, flatten, append, groupBy } = require('../src/collection.js');
const { cloneConfig, removeKey, same, withDefaults } = require('../src/values.js');

function CHECK(name, cond) {
  let ok = false;
  try {
    ok = typeof cond === 'function' ? !!cond() : !!cond;
  } catch (e) {
    ok = false;
  }
  console.log('TEST ' + name + ' ' + (ok ? 'PASS' : 'FAIL'));
}

function collect(iterable) {
  const out = [];
  for (const v of iterable) out.push(v);
  return out;
}

const g = new Greeter('Ada');
CHECK('greet_direct', () => g.greet() === 'Hello, Ada');
const extracted = g.greet;
CHECK('greet_extracted', () => extracted() === 'Hello, Ada');

CHECK('has_own', () => hasProperty({ a: 1 }, 'a') === true);
CHECK('has_inherited', () => hasProperty(Object.create({ inherited: 1 }), 'inherited') === true);

CHECK('parent_kind', () => new Parent().kind === 'parent');
Child.prototype.kind = 'child';
CHECK('child_override', () => new Parent().kind === 'parent');

CHECK('invoke_method', () => invoke({ x: 7, method() { return this.x; } }) === 7);

CHECK('seq_first', () => collect(getSequence()).join(',') === '0,1,2');
CHECK('seq_second', () => collect(getSequence()).join(',') === '0,1,2');

CHECK('flatten_basic', () => JSON.stringify(collect(flatten([[1, 2], [3]]))) === '[1,2,3]');

const original = [1, 2];
const appended = append(original, 3);
CHECK('append_immutable', () => original.join(',') === '1,2' && appended.join(',') === '1,2,3');

const grouped = groupBy([{ k: 'a', v: 1 }, { k: 'b', v: 2 }], x => x.k);
grouped.a.push({ k: 'a', v: 99 });
CHECK('groupby_independent', () => grouped.b.length === 1);

const cfg = { settings: { level: 1 }, name: 'x' };
const clone = cloneConfig(cfg);
clone.settings.level = 2;
CHECK('clone_nested', () => cfg.settings.level === 1);

const obj = { keep: 1, drop: 2 };
removeKey(obj, 'drop');
CHECK('remove_key_gone', () => !('drop' in obj));

CHECK('same_strict', () => same(1, '1') === false);

const defTags = withDefaults({});
defTags.tags.push('leak');
CHECK('withdefaults_tags', () => withDefaults({}).tags.join(',') === 'default');
