const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const test = require('node:test');

const denyToml = readFileSync(join(__dirname, '..', 'deny.toml'), 'utf8');

test('cargo-deny uses its GNU LGPL-2.1 license identifier', () => {
  assert.doesNotMatch(denyToml, /"LGPL-2\.1-or-later"/);
  assert.match(denyToml, /"LGPL-2\.1"/);
});
