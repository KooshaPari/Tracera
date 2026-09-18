#!/usr/bin/env node
/** Static, side-effect-free audit of the canonical frontend client and Rust routes. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..', '..');
const client = fs.readFileSync(path.join(root, 'frontend/apps/web/src/api/endpoints.ts'), 'utf8');
const clientRoutes = new Set();
const routePattern = /apiClient\.(GET|POST|PUT|DELETE)\(\s*['"]([^'"]+)['"]/g;
for (const match of client.matchAll(routePattern)) {
  clientRoutes.add(`${match[1].toUpperCase()} ${match[2]}`);
}
// The axum router lives in its own module (crates/tracera-server/src/router.rs),
// not main.rs. Walk the crate's whole source tree instead of naming one file, so
// moving the router again cannot silently reduce this audit to zero routes.
const serverRoutes = new Set();
const crateSrc = path.join(root, 'crates/tracera-server/src');
const serverFiles = fs
  .readdirSync(crateSrc, { recursive: true, withFileTypes: true })
  .filter((entry) => entry.isFile() && entry.name.endsWith('.rs'))
  .map((entry) => path.join(entry.parentPath ?? entry.path, entry.name));
for (const file of serverFiles) {
  // `.route(` and its path usually sit on separate lines, so collapse that
  // opening first; `\s` then spans the newline to the method name.
  const source = fs.readFileSync(file, 'utf8').replace(/\.route\(\s+/g, '.route(');
  const serverRoutePattern = /\.route\("([^"]+)",\s*(get|post|put|delete)\(/g;
  for (const match of source.matchAll(serverRoutePattern)) {
    serverRoutes.add(`${match[2].toUpperCase()} ${match[1]}`);
  }
}
assert.ok(clientRoutes.size > 0, 'no client routes found');
assert.ok(serverRoutes.size > 0, 'no Rust routes found');
const shared = [...clientRoutes].filter((route) => serverRoutes.has(route));
const missing = [...clientRoutes].filter((route) => !serverRoutes.has(route));
assert.ok(shared.length > 0, 'no client routes overlap the Rust router');
// The rich dashboard intentionally keeps its projects/items/links/graph/search
// surface behind the Python/Go gateway.  Only routes outside these explicit
// gateway-owned namespaces are required to be implemented by Rust here.
const gatewayOwnedPrefixes = [
  '/api/v1/projects',
  '/api/v1/items',
  '/api/v1/links',
  '/api/v1/graph',
  '/api/v1/search',
  '/api/v1/import',
];
const unexpected = missing.filter((route) => {
  const path = route.replace(/^[A-Z]+ /, '');
  return !gatewayOwnedPrefixes.some((prefix) => path.startsWith(prefix));
});
assert.deepEqual(unexpected, [], `unowned client routes missing from Rust router: ${unexpected.join(', ')}`);
console.log(
  `PASS client/server route audit (${shared.length} Rust-native, ${missing.length} gateway-owned)`,
);
