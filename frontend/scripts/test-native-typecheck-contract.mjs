import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const scriptDirectory = new URL(".", import.meta.url);
const packageJson = JSON.parse(
  await readFile(
    fileURLToPath(new URL("../package.json", scriptDirectory)),
    "utf8",
  ),
);

assert.equal(
  packageJson.scripts["typecheck:web"],
  "bun x tsc --noEmit --pretty false -p apps/web/tsconfig.json",
);
assert.equal(
  packageJson.scripts["typecheck:packages"],
  "bun x tsc --noEmit --pretty false -p packages/api-client/tsconfig.json -p packages/config/tsconfig.json -p packages/env-manager/tsconfig.json -p packages/state/tsconfig.json -p packages/types/tsconfig.json -p packages/ui/tsconfig.json",
);
assert.equal(
  packageJson.scripts.pretypecheck,
  "node scripts/test-native-typecheck-contract.mjs",
);
assert.doesNotMatch(packageJson.scripts.typecheck, /oxlint-tsgolint/);
assert.doesNotMatch(packageJson.scripts.typecheck, /--build/);
