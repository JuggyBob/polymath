'use strict';
const U = require('../src/utils.js');

function CHECK(name, cond) {
  console.log('TEST ' + name + ' ' + (cond ? 'PASS' : 'FAIL'));
}

CHECK('h_sum_empty', U.sum([]) === 0);
CHECK('h_sum_negative', U.sum([-1, 2, -3]) === -2);
CHECK('h_sum_sparse', U.sum([1, , 3]) === 4);

CHECK('h_average_empty', Number.isNaN(U.average([])));
CHECK('h_average_nan', U.average([1, NaN, 3]) === 2);

CHECK('h_unique_dedup', JSON.stringify(U.unique([1, 1, 2, 3, 3])) === '[1,2,3]');
CHECK('h_unique_order', JSON.stringify(U.unique([5, 3, 5, 1])) === '[5,3,1]');
CHECK('h_unique_nan', (function () {
  const a = U.unique([NaN, NaN, 1]);
  return a.length === 2 && Number.isNaN(a[0]);
})());

CHECK('h_chunk_exact', JSON.stringify(U.chunk([1, 2, 3, 4], 2)) === '[[1,2],[3,4]]');
CHECK('h_chunk_nonmutating', (function () {
  const a = [1, 2, 3];
  U.chunk(a, 2);
  return a.length === 3;
})());

CHECK('h_groupby_grouping', (function () {
  const g = U.groupBy((x) => (x % 2 ? 'odd' : 'even'), [1, 2, 3]);
  return g.odd.length === 2 && g.even.length === 1;
})());
CHECK('h_groupby_independent', (function () {
  U.groupBy(() => 'a', [1]);
  const g = U.groupBy(() => 'b', [2]);
  return g.a === undefined && g.b.length === 1;
})());

CHECK('h_flatten_deep', JSON.stringify(U.flatten([1, [2, [3, [4]]]], 3)) === '[1,2,3,4]');

CHECK('h_frequency_strict', (function () {
  const m = U.frequency([1, '1', 1]);
  return m.get(1) === 2 && m.get('1') === 1;
})());
CHECK('h_frequency_nan', U.frequency([NaN, NaN]).get(NaN) === 2);
CHECK('h_frequency_empty', U.frequency([]).size === 0);

CHECK('h_clamp_bounds', U.clamp(0, 0, 10) === 0 && U.clamp(10, 0, 10) === 10);
CHECK('h_clamp_negzero', Object.is(U.clamp(-0, -5, 5), 0));
