export type GeometryTruth = "physical" | "measured" | "semantic" | "illustrative";
export type SpatialViewKind = "assembly" | "flow" | "environment" | "hybrid";
export interface SpatialGlyph {
  entity_ref: string;
  kind: string;
  label: string;
  geometry_truth: GeometryTruth;
  geometry_source_ref: string | null;
  position: [number, number, number];
}
export interface SpatialConduit {
  relation_ref: string;
  source_ref: string;
  target_ref: string;
  kind: string;
  source_evidence_ref: string | null;
}
export interface SpatialProjection {
  scope: { product_id: string; baseline_revision: number; view: SpatialViewKind; max_nodes: number; max_relations: number };
  glyphs: SpatialGlyph[];
  conduits: SpatialConduit[];
  omitted_nodes: number;
  omitted_relations: number;
  truncated: boolean;
  input_complete: boolean;
  read_only: true;
}
type RecordValue = Record<string, unknown>;
const record = (x: unknown): x is RecordValue => x !== null && typeof x === "object" && !Array.isArray(x);
const truthKinds = new Set<GeometryTruth>(["physical", "measured", "semantic", "illustrative"]);
const viewKinds = new Set<SpatialViewKind>(["assembly", "flow", "environment", "hybrid"]);
const str = (x: unknown, field: string): string => {
  if (typeof x !== "string" || !x.trim()) throw new Error("Invalid spatial field: " + field);
  return x;
};
const optStr = (x: unknown): string | null => x === null || x === undefined ? null : str(x, "provenance");
const int = (x: unknown, field: string): number => {
  if (typeof x !== "number" || !Number.isSafeInteger(x) || x < 0) throw new Error("Invalid spatial number: " + field);
  return x;
};
export function parseSpatialProjection(value: unknown): SpatialProjection {
  if (!record(value) || !record(value.scope)) throw new Error("Invalid spatial envelope");
  const rawScope = value.scope;
  const productId = str(rawScope.product_id, "product_id");
  const baseline = int(rawScope.baseline_revision, "baseline_revision");
  if (!viewKinds.has(rawScope.view as SpatialViewKind)) throw new Error("Invalid spatial view");
  if (!Array.isArray(value.glyphs) || !Array.isArray(value.conduits) || value.read_only !== true) {
    throw new Error("Spatial projection authority or elements invalid");
  }
  if (typeof value.input_complete !== "boolean" || typeof value.truncated !== "boolean") {
    throw new Error("Spatial completeness not supplied");
  }
  const ids = new Set<string>();
  const glyphs: SpatialGlyph[] = value.glyphs.map((x: unknown) => {
    if (!record(x) || !Array.isArray(x.position) || x.position.length !== 3) throw new Error("Invalid spatial glyph");
    const id = str(x.entity_ref, "entity_ref");
    if (ids.has(id)) throw new Error("Duplicate entity");
    ids.add(id);
    const truth = x.geometry_truth as GeometryTruth;
    if (!truthKinds.has(truth)) throw new Error("Unknown geometry truth");
    const source = optStr(x.geometry_source_ref);
    if ((truth === "physical" || truth === "measured") && !source) throw new Error("Missing physical provenance");
    const position = x.position.map((n: unknown) => int(n, "position")) as [number, number, number];
    return { entity_ref: id, label: str(x.label, "label"), kind: str(x.kind, "kind"),
      geometry_truth: truth, geometry_source_ref: source, position };
  });
  const edges = new Set<string>();
  const conduits: SpatialConduit[] = value.conduits.map((x: unknown) => {
    if (!record(x)) throw new Error("Invalid conduit");
    const id = str(x.relation_ref, "relation_ref");
    const from = str(x.source_ref, "source_ref");
    const to = str(x.target_ref, "target_ref");
    if (edges.has(id) || !ids.has(from) || !ids.has(to)) throw new Error("Duplicate or dangling conduit");
    edges.add(id);
    return { relation_ref: id, source_ref: from, target_ref: to,
      kind: str(x.kind, "kind"), source_evidence_ref: optStr(x.source_evidence_ref) };
  });
  return { scope: { product_id: productId, baseline_revision: baseline,
      view: rawScope.view as SpatialViewKind,
      max_nodes: int(rawScope.max_nodes, "max_nodes"),
      max_relations: int(rawScope.max_relations, "max_relations") },
    glyphs, conduits, omitted_nodes: int(value.omitted_nodes, "omitted_nodes"),
    omitted_relations: int(value.omitted_relations, "omitted_relations"),
    truncated: value.truncated, input_complete: value.input_complete, read_only: true };
}
