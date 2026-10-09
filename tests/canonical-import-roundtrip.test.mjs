import assert from "node:assert/strict";
import test from "node:test";

import { parseCanonicalExport } from "../frontend/apps/web/src/views/projects-list/canonicalImport.ts";

const exported = {
  project: { id: "original-project", name: "Canonical source graph" },
  items: [{ id: "github:KooshaPari:Tracera:1099", title: "Source issue",
    view: "traceability", type: "story", status: "active", description: "Source context", version: 2,
    source_url: "https://github.com/KooshaPari/Tracera/issues/1099",
    source_repo: "KooshaPari/Tracera", source_kind: "github_issue" },
    { id: "REQ-1", title: "Requirement", view: "traceability", type: "requirement", status: "active" }],
  links: [{ source_id: "github:KooshaPari:Tracera:1099", target_id: "REQ-1", type: "satisfies" }],
};

test("canonical full export retains source provenance when prepared for reimport", () => {
  const candidate = { ...exported, project: { ...exported.project, id: "new-project" } };
  const parsed = parseCanonicalExport(JSON.stringify(candidate));
  assert.deepEqual(parsed, candidate);
  assert.deepEqual(parseCanonicalExport(JSON.stringify(parsed)), parsed);
});

test("older exports without optional provenance remain valid", () => {
  const without = structuredClone(exported);
  for (const key of ["source_url", "source_repo", "source_kind"]) delete without.items[0][key];
  assert.deepEqual(parseCanonicalExport(JSON.stringify(without)), without);
});

test("malformed required graph rows fail parsing instead of yielding a partial graph", () => {
  const malformed = structuredClone(exported);
  delete malformed.items[0].title;
  assert.equal(parseCanonicalExport(JSON.stringify(malformed)), undefined);
  assert.equal(parseCanonicalExport("{invalid JSON"), undefined);
});
