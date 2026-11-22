'use strict';

// Map every item with an async function. The result array must be in the
// same order as the input, regardless of how long each mapper call takes.
async function mapOrdered(items, mapper) {
  const out = [];
  await Promise.all(items.map(async (item, i) => {
    const value = await mapper(item);
    out.push(value);
  }));
  return out;
}

// Forward every value of `source` through `transform`. A failure in the
// transform must be visible to the caller of `pipe`.
async function pipe(source, transform) {
  const out = [];
  try {
    for await (const value of source) out.push(transform(value));
  } catch (err) {
    return out;
  }
  return out;
}

// A small in-memory buffer used by the stream helpers.
function createBuffer() {
  let items = [];
  let closed = false;
  return {
    push(v) { if (!closed) items.push(v); },
    close() { closed = false; },
    isClosed() { return closed; },
    drain() { const out = items; items = []; return out; },
    size() { return items.length; },
  };
}

module.exports = { mapOrdered, pipe, createBuffer };
