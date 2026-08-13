#!/usr/bin/env node

/**
 * Verify the documented Rust gateway contract without depending on the
 * retired `src/services/traceraClient.js` file.
 *
 * The rich dashboard has a separate generated OpenAPI client surface.  The
 * documented 13-route contract remains the compatibility boundary for the
 * Rust gateway and future sidecars, so this check compares it with the
 * authoritative server registrations and the current frontend bootstrap.
 */

import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const repoRoot = path.resolve(import.meta.dirname, "..", "..");
const frontendRoot = path.resolve(import.meta.dirname, "..");
const read = (relativePath) => fs.readFileSync(path.join(repoRoot, relativePath), "utf8");

const contract = read("docs/operations/openapi_contract_guard.md");
const server = read("crates/tracera-server/src/main.rs");
const clientCore = read("frontend/apps/web/src/api/client-core.ts");
const apiOrigin = read("frontend/apps/web/src/config/api-origin.ts");
const preflight = read("frontend/apps/web/src/lib/preflight.ts");
const currentClientPath = "frontend/apps/web/src/api/client-core.ts";

const rows = contract.split("\n").filter((line) => /^\|\s*(GET|POST)\s*\|/.test(line));
assert.ok(rows.length > 0, "contract document must contain endpoint rows");

const routes = new Set();
for (const line of server.split("\n")) {
  const marker = '.route("';
  const start = line.indexOf(marker);
  if (start < 0) continue;
  const endpointStart = start + marker.length;
  const endpointEnd = line.indexOf('"', endpointStart);
  const comma = line.indexOf(",", endpointEnd);
  if (endpointEnd < 0 || comma < 0) continue;
  const endpoint = line.slice(endpointStart, endpointEnd);
  const handlers = line.slice(comma + 1);
  for (const method of ["get", "post"]) {
    if (new RegExp(`\\b${method}\\s*\\(`).test(handlers)) {
      routes.add(`${method.toUpperCase()} ${endpoint}`);
    }
  }
}

for (const row of rows) {
  const [, method, endpoint] = row.match(/^\|\s*(GET|POST)\s*\|\s*`([^`]+)`/) ?? [];
  assert.ok(method && endpoint, `malformed contract row: ${row}`);
  assert.ok(
    routes.has(`${method} ${endpoint}`),
    `${method} ${endpoint} missing from tracera-server route registration`,
  );
}

assert.ok(fs.existsSync(path.join(frontendRoot, "apps/web/src/api/client-core.ts")));
assert.match(clientCore, /API_ORIGIN/);
assert.match(apiOrigin, /VITE_API_URL/);
assert.match(preflight, /\/ready/);
assert.match(preflight, /:18000/);
assert.doesNotMatch(contract, /src\/services\/traceraClient\.js|VITE_API_BASE/);

console.log(
  `PASS contract doc parity (${rows.length} gateway endpoints; client=${currentClientPath})`,
);
