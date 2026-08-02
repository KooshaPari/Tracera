#!/usr/bin/env node

/**
 * Guard the current rich dashboard transport contract.
 *
 * The Jan/Feb-descended frontend replaced the short-lived
 * `src/services/traceraClient.js` adapter with the typed API surface under
 * `apps/web/src/api/`.  Keep this check source-based so it can run in a
 * clean checkout without a Vite build, browser, or backend process.
 */

import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const source = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");

const apiOrigin = source("apps/web/src/config/api-origin.ts");
const clientCore = source("apps/web/src/api/client-core.ts");
const preflight = source("apps/web/src/lib/preflight.ts");
const openapi = JSON.parse(source("apps/web/public/specs/openapi.json"));

const cases = [
  [
    "uses VITE_API_URL with the loopback gateway fallback",
    () => {
      assert.match(apiOrigin, /DEFAULT_API_ORIGIN\s*=\s*['"]http:\/\/127\.0\.0\.1:18000['"]/);
      assert.match(apiOrigin, /import\.meta\.env\.VITE_API_URL\s*\?\?/);
      assert.match(clientCore, /import \{ API_ORIGIN \} from ['"]@\/config\/api-origin['"]/);
      assert.match(clientCore, /baseUrl:\s*API_BASE_URL/);
    },
  ],
  [
    "gates startup on the gateway readiness contract",
    () => {
      assert.match(preflight, /['"]\/ready['"]/);
      assert.match(preflight, /['"]\/health['"]/);
      assert.match(preflight, /['"]\/api\/v1\/health['"]/);
      assert.match(preflight, /:18000/);
      assert.doesNotMatch(
        preflight,
        /localhost:8000|127\.0\.0\.1:8000|localhost:8080|127\.0\.0\.1:8080/,
      );
    },
  ],
  [
    "ships the generated rich-frontend API schema",
    () => {
      assert.ok(openapi.paths && typeof openapi.paths === "object");
      assert.ok(Object.keys(openapi.paths).length >= 50, "expected the full rich API schema");
      for (const pathName of ["/health", "/api/v1/auth/me", "/api/v1/graph/analysis/impact"]) {
        assert.ok(openapi.paths[pathName], `missing generated API path: ${pathName}`);
      }
    },
  ],
];

let failures = 0;
for (const [name, check] of cases) {
  try {
    check();
    console.log(`PASS ${name}`);
  } catch (error) {
    failures += 1;
    console.error(`FAIL ${name}: ${error instanceof Error ? error.message : String(error)}`);
  }
}

if (failures > 0) {
  process.exitCode = 1;
} else {
  console.log(`Tracera rich client contract: PASS (${cases.length} checks)`);
}
