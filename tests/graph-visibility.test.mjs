import assert from "node:assert/strict";
import test from "node:test";

import { graphLinkForView, graphVisibility } from "../frontend/apps/web/src/pages/projects/views/graphVisibility.ts";

test("gives canonical link triples stable renderer IDs scoped to their project", () => {
  const link = { source_id: "A", target_id: "B", type: "implements" };
  const a = graphLinkForView(link, "project-a");
  const same = graphLinkForView(link, "project-a");
  const b = graphLinkForView(link, "project-b");
  assert.equal(a.id, same.id);
  assert.notEqual(a.id, b.id);
  assert.equal(a.type, "implements");
  assert.equal(a.sourceId, "A");
  assert.equal(a.targetId, "B");
  assert.equal(link.id, undefined);
});

test("keeps every persisted relationship type available across explicit viewport expansion", () => {
  const items = Array.from({ length: 20 }, (_, i) => ({ id: `item-${i}` }));
  const types = ["satisfies", "implements", "verifies", "depends_on"];
  const links = Array.from({ length: 10_001 }, (_, i) => ({
    sourceId: `item-${i % 20}`,
    targetId: `item-${(i + 1) % 20}`,
    type: types[i % types.length],
  }));

  const initial = graphVisibility(items, links, 20, 250, false, false);
  assert.equal(initial.visibleLinks.length, 250);
  assert.equal(initial.canLoadMore, true);
  assert.equal(initial.unavailableEndpointLinks, 0);

  const expanded = graphVisibility(items, links, 20, 10_001, false, false);
  assert.equal(expanded.visibleLinks.length, 10_001);
  assert.deepEqual(new Set(expanded.visibleLinks.map((link) => link.type)), new Set(types));
  assert.equal(expanded.canLoadMore, false);
});

test("reports links to absent items instead of quietly treating them as rendered", () => {
  const items = [{ id: "story-1" }];
  const links = [{ sourceId: "story-1", targetId: "REQ-1", type: "satisfies" }];
  const pending = graphVisibility(items, links, 200, 250, true, false);
  assert.equal(pending.canLoadMore, true);
  assert.equal(pending.unavailableEndpointLinks, 0);

  const exhausted = graphVisibility(items, links, 200, 250, false, false);
  assert.equal(exhausted.visibleLinks.length, 0);
  assert.equal(exhausted.unavailableEndpointLinks, 1);
  assert.equal(exhausted.canLoadMore, false);
});
