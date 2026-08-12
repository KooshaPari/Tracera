#!/usr/bin/env bun
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const workflowPath = join(import.meta.dirname, "..", "..", ".github", "workflows", "release-desktop.yml");
const workflow = readFileSync(workflowPath, "utf8");

assert.ok(
  workflow.includes("${{ matrix.archive_format }}"),
  "release-desktop artifact upload must interpolate matrix.archive_format",
);
assert.ok(
  !workflow.includes(".{{ matrix.archive_format }}"),
  "release-desktop artifact upload must not use a literal GitHub expression",
);

console.log("release-desktop artifact upload interpolation verified");
