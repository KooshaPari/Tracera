import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const scriptDirectory = new URL(".", import.meta.url);
const workflow = await readFile(
  fileURLToPath(new URL("../../.github/workflows/ci.yml", scriptDirectory)),
  "utf8",
);

assert.match(workflow, /^  lint:\n(?:    #.*\n)?    name: ci \/ lint$/m);
assert.match(workflow, /^  test:\n(?:    #.*\n)?    name: ci \/ test$/m);
assert.match(workflow, /needs:\s*\[detect-changes, rust-lint, rust-test\]/);
assert.match(workflow, /needs\.detect-changes\.outputs\.rust == 'true'/);
