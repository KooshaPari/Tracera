import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFile, unlink, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const root = resolve(__dirname, "..");
const tscBin = resolve(root, "node_modules", ".bin", "tsc");

const packageJson = JSON.parse(
  await readFile(resolve(root, "package.json"), "utf8"),
);

// ---------------------------------------------------------------------------
// 1. Assert that the per-project typecheck scripts are factually correct
// ---------------------------------------------------------------------------
assert.equal(
  packageJson.scripts["typecheck:web"],
  "bun x tsc --noEmit --pretty false -p apps/web/tsconfig.json",
);

assert.equal(
  packageJson.scripts["typecheck:packages"],
  [
    "bun x tsc --noEmit --pretty false -p packages/api-client/tsconfig.json",
    "bun x tsc --noEmit --pretty false -p packages/config/tsconfig.json",
    "bun x tsc --noEmit --pretty false -p packages/env-manager/tsconfig.json",
    "bun x tsc --noEmit --pretty false -p packages/state/tsconfig.json",
    "bun x tsc --noEmit --pretty false -p packages/types/tsconfig.json",
    "bun x tsc --noEmit --pretty false -p packages/ui/tsconfig.json",
  ].join(" && "),
);

assert.equal(
  packageJson.scripts.pretypecheck,
  "node scripts/test-native-typecheck-contract.mjs",
);

// Anti-regression assertions for F02/F03: the multi-`-p` form silently drops
// all but the last project.  Only `&&`-chained per-project invocations are
// acceptable.
assert.match(
  packageJson.scripts["typecheck:packages"],
  /&&/,
  "typecheck:packages MUST use &&-chained per-project tsc invocations (F02)",
);
assert.doesNotMatch(
  packageJson.scripts["typecheck:packages"],
  /tsc[^&]+-p\s+\S+[^&]+-p\s+\S+/,
  "typecheck:packages MUST NOT pass multiple -p flags to a single tsc (F03)",
);

assert.doesNotMatch(packageJson.scripts.typecheck, /oxlint-tsgolint/);
assert.doesNotMatch(packageJson.scripts.typecheck, /--build/);

// ---------------------------------------------------------------------------
// 2. Prove every configured project is actually checked (F02 / F03)
//
//    For each project in typecheck:packages, inject a deliberate type error,
//    verify tsc exits non-zero, then remove the error and verify tsc passes.
// ---------------------------------------------------------------------------
const PACKAGES = [
  "api-client",
  "config",
  "env-manager",
  "state",
  "types",
  "ui",
];

function runTsc(pkg) {
  return spawnSync(
    tscBin,
    [
      "--noEmit",
      "--pretty", "false",
      "-p", resolve(root, "packages", pkg, "tsconfig.json"),
    ],
    { cwd: root, encoding: "utf8", timeout: 30_000 },
  );
}

/**
 * tsc writes diagnostics to stdout; stderr carries only fatal errors, so both
 * streams have to be inspected when asserting on reported diagnostics.
 */
function tscOutput(result) {
  return `${result.stdout ?? ""}${result.stderr ?? ""}`;
}

/**
 * Inject a deliberate type error, verify tsc catches it, clean up.
 * Proves this specific project is actually being scanned.
 */
async function proveProjectTypecheckFails(pkg) {
  const probeFile = resolve(root, "packages", pkg, "src", "test-typecheck-gate-bad.ts");
  const probeContent = `// DO NOT REMOVE — typecheck gate probe (F02)\nconst _probe_tc_gate: boolean = "not-a-boolean";\n`;

  await writeFile(probeFile, probeContent, "utf8");

  try {
    const result = runTsc(pkg);
    const diagnostics = tscOutput(result);
    assert.notEqual(
      result.status,
      0,
      `tsc -p packages/${pkg} must FAIL with deliberate type error (exit=${result.status}):\n${diagnostics.slice(0, 200)}`,
    );
    assert.ok(
      diagnostics.includes("_probe_tc_gate"),
      `tsc output for packages/${pkg} must reference the injected probe:\n${diagnostics.slice(0, 300)}`,
    );
  } finally {
    // Cleanup: error file, plus any .tsbuildinfo that may have been written.
    // Runs even when an assertion above throws, so a failed run never leaves
    // the probe behind in the workspace.
    try { await unlink(probeFile); } catch { /* ok */ }
  }
}

/**
 * Verify a package type-checks cleanly.
 */
function assertProjectTypecheckPasses(pkg) {
  const result = runTsc(pkg);
  assert.equal(
    result.status,
    0,
    `tsc -p packages/${pkg} must pass cleanly (exit=${result.status}):\n${tscOutput(result).slice(0, 300)}`,
  );
}

// Run the per-project proof
for (const pkg of PACKAGES) {
  await proveProjectTypecheckFails(pkg);
  assertProjectTypecheckPasses(pkg);
}