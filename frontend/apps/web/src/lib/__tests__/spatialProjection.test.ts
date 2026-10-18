import { describe, expect, it } from "vitest";
import { parseSpatialProjection } from "../spatialProjection";

const fixture = () => ({
  scope: { product_id: "tracera", baseline_revision: 1, view: "assembly", max_nodes: 10, max_relations: 10 },
  glyphs: [
    { entity_ref: "a", label: "API", kind: "capability", geometry_truth: "semantic", geometry_source_ref: null, position: [0,0,0] },
    { entity_ref: "b", label: "DB", kind: "component", geometry_truth: "semantic", geometry_source_ref: null, position: [4,0,0] },
  ],
  conduits: [{ relation_ref: "e1", source_ref: "a", target_ref: "b", kind: "depends_on", source_evidence_ref: null }],
  omitted_nodes: 0, omitted_relations: 0, truncated: false, input_complete: true, read_only: true,
});
describe("spatial projection parse contract", () => {
  it("retains canonical identities and edge direction", () => {
    const x = parseSpatialProjection(fixture());
    expect(x.glyphs.map(g => g.entity_ref)).toEqual(["a","b"]);
    expect(x.conduits[0]).toMatchObject({source_ref:"a", target_ref:"b", kind:"depends_on"});
  });
  it("rejects false physical provenance", () => {
    const x = fixture();
    x.glyphs[0]!.geometry_truth = "physical";
    expect(() => parseSpatialProjection(x)).toThrow("provenance");
  });
  it("rejects dangling typed relations", () => {
    const x = fixture();
    x.conduits[0]!.target_ref = "missing";
    expect(() => parseSpatialProjection(x)).toThrow("dangling");
  });
  it("enforces read-only and completeness disclosure", () => {
    expect(() => parseSpatialProjection({...fixture(), read_only: false})).toThrow("authority");
    expect(() => parseSpatialProjection({...fixture(), input_complete: null})).toThrow("completeness");
  });
  it("preserves incomplete state", () => {
    const x = parseSpatialProjection({...fixture(), truncated: true, input_complete: false, omitted_nodes: 5});
    expect(x.input_complete).toBe(false);
    expect(x.omitted_nodes).toBe(5);
  });
});
