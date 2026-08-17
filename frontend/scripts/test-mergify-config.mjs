import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const scriptDirectory = new URL(".", import.meta.url);
const config = await readFile(
  fileURLToPath(new URL("../../.mergify.yml", scriptDirectory)),
  "utf8",
);

assert.match(config, /author ~= \^\(\?:dependabot\\\[bot\\\]\|renovate\\\[bot\\\]\)\$/);
assert.match(config, /author ~= \^\(\?:trunk-io\\\[bot\\\]\|mergify\\\[bot\\\]\|github-actions\\\[bot\\\]\)\$/);
assert.match(config, /updated-at < 30 days ago/);
assert.match(config, /\n        users:\n          - KooshaPari/);
assert.doesNotMatch(config, /post_merge:|github_accounts:|age>=30d/);
