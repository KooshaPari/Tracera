import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const workflow = readFileSync(".github/workflows/coverage.yml", "utf8");

assert.match(
  workflow,
  /group:\s*coverage-\$\{\{\s*github\.ref\s*\}\}/,
  "coverage concurrency must be scoped to the current ref",
);
assert.doesNotMatch(
  workflow,
  /group:\s*coverage-\$\{\s+github\.ref\s+\}/,
  "coverage concurrency must not use a literal shared group",
);
assert.match(
  workflow,
  /cargo llvm-cov --workspace --text/,
  "coverage summary must use the supported text output mode",
);
assert.doesNotMatch(
  workflow,
  /cargo llvm-cov --workspace --summary/,
  "coverage workflow must not use the unsupported summary flag",
);
