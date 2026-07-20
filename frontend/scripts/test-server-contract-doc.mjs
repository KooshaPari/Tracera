#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..', '..');
const contract = fs.readFileSync(
  path.join(root, 'docs/operations/openapi_contract_guard.md'),
  'utf8',
);
const server = fs.readFileSync(
  path.join(root, 'crates/tracera-server/src/main.rs'),
  'utf8',
);

const rows = contract.split('\n').filter((line) => /^\|\s*(GET|POST)\s*\|/.test(line));
assert.ok(rows.length > 0, 'contract document must contain endpoint rows');

const routes = new Set();
for (const match of server.matchAll(/\.route\(\s*(['"])([^'"]+)\1\s*,\s*([^)]{0,200})\)/g)) {
  const [, , endpoint, handlers] = match;
  for (const method of ['get', 'post']) {
    if (new RegExp(`\\b${method}\\s*\\(`).test(handlers)) {
      routes.add(`${method.toUpperCase()} ${endpoint}`);
    }
  }
}

for (const row of rows) {
  const [, method, endpoint] = row.match(/^\|\s*(GET|POST)\s*\|\s*`([^`]+)`/) ?? [];
  assert.ok(method && endpoint, `malformed contract row: ${row}`);
  const normalized = endpoint.replace(/:artifact_id/g, ':artifact_id');
  assert.ok(
    routes.has(`${method} ${normalized}`),
    `${method} ${endpoint} missing from tracera-server route registration`,
  );
}

console.log(`PASS server contract parity (${rows.length} endpoints)`);
