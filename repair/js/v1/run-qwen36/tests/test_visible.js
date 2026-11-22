'use strict';
const U = require('../src/utils.js');

function CHECK(name, cond) {
  console.log('TEST ' + name + ' ' + (cond ? 'PASS' : 'FAIL'));
}

CHECK('sum_basic', U.sum([1, 2, 3]) === 6);
CHECK('sum_sparse', U.sum([1, , 3]) === 4);

CHECK('average_basic', U.average([2, 4, 6]) === 4);
CHECK('average_nan', U.average([1, NaN, 3]) === 2);

CHECK('unique_order', JSON.stringify(U.unique([10, 2, 1, 2])) === '[10,2,1]');
CHECK('unique_dedup', JSON.stringify(U.unique([1, 1, 2, 3, 3])) === '[1,2,3]');

CHECK('chunk_values', JSON.stringify(U.chunk([1, 2, 3, 4, 5], 2)) === '[[1,2],[3,4],[5]]');
const chunkSrc = [1, 2, 3, 4, 5];
U.chunk(chunkSrc, 2);
CHECK('chunk_nonmutating', chunkSrc.length === 5);

CHECK('groupby_basic', (function () {
  const g = U.groupBy((x) => (x % 2 === 0 ? 'even' : 'odd'), [1, 2, 3, 4]);
  return g.even.length === 2 && g.odd.length === 2;
})());
CHECK('groupby_independent', (function () {
  U.groupBy((x) => (x > 0 ? 'pos' : 'neg'), [1, 2]);
  const g = U.groupBy((x) => (x > 0 ? 'pos' : 'neg'), [-1]);
  return g.pos === undefined && g.neg.length === 1;
})());

CHECK('flatten_deep', JSON.stringify(U.flatten([1, [2, [3, 4]], 5], 2)) === '[1,2,3,4,5]');

CHECK('frequency_types', (function () {
  const m = U.frequency([1, '1', 1]);
  return m.get(1) === 2 && m.get('1') === 1;
})());

CHECK('clamp_bounds', U.clamp(5, 0, 10) === 5 && U.clamp(-5, 0, 10) === 0 && U.clamp(15, 0, 10) === 10);
CHECK('clamp_negative_zero', Object.is(U.clamp(-0, -1, 1), 0));
