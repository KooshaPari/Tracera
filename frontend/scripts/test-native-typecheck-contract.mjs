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
  "bun x tsc --build --pretty false apps/web/tsconfig.json",
);
assert.equal(
  packageJson.scripts["typecheck:packages"],
  "bun x tsc --build --pretty false packages/*/tsconfig.json",
);
assert.doesNotMatch(packageJson.scripts.typecheck, /oxlint-tsgolint/);
