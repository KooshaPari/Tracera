#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..', '..');
const contract = fs.readFileSync(path.join(root, 'docs/operations/openapi_contract_guard.md'), 'utf8');
const client = fs.readFileSync(path.join(root, 'frontend/apps/web/src/services/traceraClient.js'), 'utf8');
const rows = contract.split('\n').filter((line) => /^\|\s*(GET|POST)\s*\|/.test(line));

assert.ok(rows.length > 0, 'contract document must contain endpoint rows');
for (const row of rows) {
  const [, method, endpoint] = row.match(/^\|\s*(GET|POST)\s*\|\s*`([^`]+)`/) ?? [];
  assert.ok(method && endpoint, `malformed contract row: ${row}`);
  const normalized = endpoint.replace(/:artifact_id/g, '');
  assert.ok(client.includes(normalized) || client.includes(endpoint), `${method} ${endpoint} missing from traceraClient.js`);
}
console.log(`PASS contract doc parity (${rows.length} endpoints)`);
