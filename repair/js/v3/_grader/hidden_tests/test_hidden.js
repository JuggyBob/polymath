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

// --- this binding -------------------------------------------------------
const a = new Greeter('Alpha');
const b = new Greeter('Beta');
const fa = a.greet;
const fb = b.greet;
CHECK('test_h_greet_extracted', () => fa() === 'Hello, Alpha');
CHECK('test_h_greet_two_instances', () => fa() === 'Hello, Alpha' && fb() === 'Hello, Beta');

// --- prototype chain lookups -------------------------------------------
CHECK('test_h_has_inherited', () => hasProperty(Object.create({ x: 1 }), 'x') === true);
const grand = Object.create({ middle: 2 });
const child = Object.create(grand);
CHECK('test_h_has_deep_chain', () => hasProperty(child, 'middle') === true);
CHECK('test_h_has_own_still', () => hasProperty({ own: true }, 'own') === true && hasProperty({}, 'nope') === false);

// --- prototype separation ----------------------------------------------
Child.prototype.kind = 'child';
CHECK('test_h_proto_not_shared', () => new Parent().kind === 'parent');
CHECK('test_h_proto_instanceof', () => (new Parent() instanceof Child) === false);
CHECK('test_h_proto_child_kind', () => new Child().kind === 'child');

// --- invoke / receiver --------------------------------------------------
CHECK('test_h_invoke_receiver', () => invoke({ x: 7, method() { return this.x; } }) === 7);
CHECK('test_h_invoke_method_uses_other_field', () => invoke({ p: 2, q: 5, method() { return this.p + this.q; } }) === 7);

// --- generator exhaustion ----------------------------------------------
CHECK('test_h_seq_first_use', () => collect(getSequence()).join(',') === '0,1,2');
CHECK('test_h_seq_fresh_each_call', () => collect(getSequence()).join(',') === '0,1,2');

// --- generator delegation ----------------------------------------------
CHECK('test_h_flatten_delegation', () => JSON.stringify(collect(flatten([[1, 2], [3, 4]]))) === '[1,2,3,4]');
CHECK('test_h_flatten_empty_arrays', () => JSON.stringify(collect(flatten([[], [5]]))) === '[5]');

// --- spread vs mutation -------------------------------------------------
const arr0 = [10, 20];
const arr1 = append(arr0, 30);
CHECK('test_h_append_no_mutate', () => arr0.join(',') === '10,20' && arr1.join(',') === '10,20,30');
const arr2 = append(append([1], 2), 3);
CHECK('test_h_append_chain', () => arr2.join(',') === '1,2,3');

// --- aliasing in groupBy ------------------------------------------------
const groups = groupBy([{ k: 'a', v: 1 }, { k: 'b', v: 2 }, { k: 'a', v: 3 }], x => x.k);
groups.a.push({ k: 'a', v: 99 });
CHECK('test_h_groupby_independent', () => groups.b.length === 1);
CHECK('test_h_groupby_keys', () => Object.keys(groups).sort().join(',') === 'a,b' && groups.a.length === 3);

// --- shallow copy -------------------------------------------------------
const base = { settings: { level: 1 }, label: 'base' };
const c1 = cloneConfig(base);
c1.settings.level = 9;
CHECK('test_h_clone_nested', () => base.settings.level === 1 && c1.settings.level === 9);
const c2 = cloneConfig(base);
c2.settings.level = 5;
CHECK('test_h_clone_sibling', () => c1.settings.level === 9 && base.settings.level === 1);

// --- delete vs undefined ------------------------------------------------
const del = { keep: 1, drop: 2 };
removeKey(del, 'drop');
CHECK('test_h_remove_key_gone', () => !('drop' in del));
CHECK('test_h_remove_key_object_keys', () => Object.keys(del).join(',') === 'keep');

// --- strict equality ----------------------------------------------------
CHECK('test_h_same_loose', () => same(1, '1') === false);
CHECK('test_h_same_null_undefined', () => same(null, undefined) === false);
CHECK('test_h_same_values', () => same(2, 2) === true);

// --- shared defaults ----------------------------------------------------
const d1 = withDefaults({});
d1.tags.push('leak');
const d2 = withDefaults({});
CHECK('test_h_withdefaults_tags', () => d2.tags.join(',') === 'default');
const d3 = withDefaults({ tags: ['mine'] });
d3.tags.push('more');
CHECK('test_h_withdefaults_override', () => d3.tags.join(',') === 'mine,more' && withDefaults({}).tags.join(',') === 'default');
