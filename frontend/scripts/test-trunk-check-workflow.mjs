import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const scriptDirectory = new URL(".", import.meta.url);
const workflow = await readFile(
  fileURLToPath(new URL("../../.github/workflows/trunk-check.yml", scriptDirectory)),
  "utf8",
);

assert.match(
  workflow,
  /npm install --global --ignore-scripts prettier@3\.6\.2/,
  "Trunk Check must install pinned Prettier without lifecycle scripts",
);
