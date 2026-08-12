#!/usr/bin/env bun
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const repoRoot = join(import.meta.dirname, "..", "..");
const deny = readFileSync(join(repoRoot, "deny.toml"), "utf8");
const ci = readFileSync(join(repoRoot, ".github", "workflows", "ci.yml"), "utf8");
const releaseWorkflowTest = readFileSync(
  join(repoRoot, "frontend", "scripts", "test-release-desktop-workflow.mjs"),
  "utf8",
);

assert.match(
  deny,
  /"LGPL-2\.1-or-later"/,
  "cargo-deny must use the SPDX GNU-or-later identifier",
);
assert.doesNotMatch(
  deny,
  /"LGPL-2\.1\+"/,
  "cargo-deny must not use a plus-sign GNU license form",
);
assert.match(
  ci,
  /name: Security Scan[\s\S]*?uses: actions\/checkout@v4\s+with:\s+fetch-depth: 0[\s\S]*?name: gitleaks/,
  "Gitleaks must receive full history so its PR base parent exists locally",
);
assert.match(
  releaseWorkflowTest,
  /^#!\/usr\/bin\/env bun$/m,
  "CI contract test scripts must use the repository Bun runtime",
);

console.log("CI policy contract verified");
