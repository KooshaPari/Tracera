#!/usr/bin/env node
/** Static, side-effect-free comparison of traceraClient paths and Rust routes. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..', '..');
const client = fs.readFileSync(path.join(root, 'frontend/apps/web/src/services/traceraClient.js'), 'utf8');
const server = fs.readFileSync(path.join(root, 'crates/tracera-server/src/main.rs'), 'utf8');
const clientRoutes = new Set();
const routePattern = /\$\{DEFAULT_API_BASE\}([^`'"\s]+)/g;
for (const match of client.matchAll(routePattern)) {
  const endpoint = match[1]
    .replace(/\$\{encodeURIComponent\(String\(artifactId\)\)\}/g, ':artifact_id')
    .replace(/\?.*$/, '');
  // All client POST calls are under the versioned analysis namespace; the
  // remaining client calls are read-only GETs. This keeps parsing deterministic
  // even when a request options object spans multiple lines.
  const method = endpoint.startsWith('/api/v1/') ? 'POST' : 'GET';
  clientRoutes.add(`${method.toUpperCase()} ${endpoint}`);
}
const serverRoutes = new Set();
for (const line of server.split('\n')) {
  const match = line.match(/\.route\("([^"]+)",\s*(get|post)\(([^)]*)\)/);
  if (match) serverRoutes.add(`${match[2].toUpperCase()} ${match[1]}`);
}
assert.ok(clientRoutes.size > 0, 'no client routes found');
assert.ok(serverRoutes.size > 0, 'no Rust routes found');
const missing = [...clientRoutes].filter((route) => !serverRoutes.has(route));
assert.deepEqual(missing, [], `client routes missing from Rust router: ${missing.join(', ')}`);
console.log(`PASS client/server route parity (${clientRoutes.size} client routes)`);
