import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import type { FormEvent } from "react";

import { client } from "@/api/client";
import { API_ORIGIN } from "@/config/api-origin";
import { parseSpatialProjection } from "@/lib/spatialProjection";
import type { SpatialProjection, SpatialViewKind } from "@/lib/spatialProjection";

/** 2.5D semantic pilot. NOT a literal CAD or full GPU 3D renderer. */
function SpatialAssembly() {
  const [productId, setProductId] = useState("tracera");
  const [baseline, setBaseline] = useState("1");
  const [view, setView] = useState<SpatialViewKind>("assembly");
  const [projection, setProjection] = useState<SpatialProjection | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [exploded, setExploded] = useState(false);
  const [showEdges, setShowEdges] = useState(true);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function load(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const revision = Number(baseline);
    if (!productId.trim() || !Number.isSafeInteger(revision) || revision < 0) {
      setError("Provide a product ID and valid baseline revision.");
      return;
    }
    setProjection(null);
    setSelected(null);
    setError(null);
    setLoading(true);
    try {
      const query = new URLSearchParams({
        baseline_revision: String(revision), view, max_nodes: "128", max_relations: "384",
      });
      const path = "/api/v1/products/" + encodeURIComponent(productId.trim()) + "/spatial?" + query.toString();
      const response = await fetch(API_ORIGIN + path, { headers: client.getAuthHeaders() });
      if (!response.ok) throw new Error("Backend returned " + response.status + " (no synthetic fallback).");
      const data: unknown = await response.json();
      const parsed = parseSpatialProjection(data);
      if (parsed.scope.product_id !== productId.trim() || parsed.scope.baseline_revision !== revision) {
        throw new Error("Snapshot identity mismatch");
      }
      setProjection(parsed);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not read product projection");
    } finally {
      setLoading(false);
    }
  }
  const chosen = projection?.glyphs.find(glyph => glyph.entity_ref === selected);
  const visible = projection?.glyphs.filter(glyph =>
    (glyph.label + glyph.kind + glyph.entity_ref).toLowerCase().includes(search.toLowerCase())
  ) ?? [];
  const edges = selected
    ? projection?.conduits.filter(edge => edge.source_ref === selected || edge.target_ref === selected) ?? []
    : projection?.conduits ?? [];

  return (
    <section className="mx-auto max-w-7xl space-y-5 p-5">
      <h1 className="text-2xl font-semibold">Spatial product assembly</h1>
      <p className="text-muted-foreground">
        Experimental read-only semantic cutaway from a persisted product baseline.
        CSS depth is metaphorical, not a physical CAD model.
      </p>
      <form onSubmit={(event) => { void load(event); }} className="flex flex-wrap items-end gap-3 rounded-lg border p-4">
        <label className="flex flex-col gap-1 text-sm">Product ID
          <input value={productId} onChange={event => setProductId(event.target.value)}
            maxLength={256} className="rounded border bg-background px-2 py-2" required />
        </label>
        <label className="flex flex-col gap-1 text-sm">Baseline
          <input value={baseline} onChange={event => setBaseline(event.target.value)}
            type="number" min={0} className="w-24 rounded border bg-background px-2 py-2" required />
        </label>
        <label className="flex flex-col gap-1 text-sm">Projection
          <select value={view} onChange={event => setView(event.target.value as SpatialViewKind)}
            className="rounded border bg-background px-2 py-2">
            <option value="assembly">Assembly</option>
            <option value="flow">Flow</option>
            <option value="environment">Environment</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </label>
        <button type="submit" disabled={loading} className="rounded bg-primary px-4 py-2 text-primary-foreground">
          {loading ? "Loading…" : "Load product"}
        </button>
      </form>
      {error && <p role="alert" className="rounded border border-destructive p-3 text-destructive">{error}</p>}
      {projection && <>
        <div role="status" className="rounded border p-3 text-sm">
          Product {projection.scope.product_id} / revision {projection.scope.baseline_revision}:
          {" "}{projection.glyphs.length} entities and {projection.conduits.length} relations.
          {(!projection.input_complete || projection.truncated) &&
            <strong className="ml-2">Partial graph. Never infer complete coverage.</strong>}
          <span className="ml-2">Read-only; no execution or verification implied.</span>
        </div>
        <div className="flex flex-wrap gap-3">
          <label className="text-sm">Find
            <input type="search" value={search} onChange={event => setSearch(event.target.value)}
              className="ml-2 rounded border bg-background p-1" />
          </label>
          <button type="button" className="rounded border px-3 py-1" onClick={() => setExploded(!exploded)}>
            {exploded ? "Reassemble" : "Explode"}
          </button>
          <button type="button" className="rounded border px-3 py-1" onClick={() => setShowEdges(!showEdges)}>
            {showEdges ? "Hide" : "Show"} connections
          </button>
          <button type="button" className="rounded border px-3 py-1" onClick={() => setSelected(null)}>Clear selection</button>
        </div>
        <div className="grid gap-5 lg:grid-cols-[2fr_1fr]">
          <div aria-label="Semantic assembly" className="min-h-80 rounded-xl border bg-muted/20 p-6">
            <div className="grid grid-cols-2 gap-5 md:grid-cols-4 [perspective:1000px]">
              {visible.map((glyph, index) => (
                <button type="button" key={glyph.entity_ref} aria-pressed={selected === glyph.entity_ref}
                  onClick={() => setSelected(glyph.entity_ref)}
                  style={{transform: "rotateX(12deg) rotateY(-12deg) translateZ(" + (exploded ? 10 + index * 2 : 0) + "px)"}}
                  className={"relative min-h-28 rounded-lg border-2 p-3 text-left shadow-xl focus-visible:outline-2 " +
                    (selected === glyph.entity_ref ? "border-primary bg-primary/10" : "border-border bg-card")}>
                  <span aria-hidden="true" className="absolute inset-x-2 -top-2 h-2 skew-x-[-35deg] bg-foreground/15" />
                  <span className="block text-xs uppercase text-muted-foreground">{glyph.kind}</span>
                  <span className="mt-3 block font-semibold">{glyph.label}</span>
                  <span className="mt-3 block text-xs text-muted-foreground">{glyph.geometry_truth} geometry</span>
                </button>
              ))}
            </div>
          </div>
          <aside className="space-y-2 rounded-xl border p-4" aria-label="Canonical entity inspector">
            <h2 className="font-semibold">Inspector</h2>
            {chosen ? <>
              <div className="text-sm">Canonical ID: <code className="break-all">{chosen.entity_ref}</code></div>
              <div className="text-sm">Type: {chosen.kind}</div>
              <div className="text-sm">Geometry truth: {chosen.geometry_truth}</div>
              <div className="text-sm">Source: {chosen.geometry_source_ref ?? "No physical source claimed"}</div>
              <div className="text-sm">Verification: not assessed by this projection</div>
            </> : <p className="text-muted-foreground text-sm">Select an entity to inspect canonical references.</p>}
          </aside>
        </div>
        {showEdges && <section className="rounded-xl border p-4">
          <h2 className="mb-2 font-semibold">Canonical directed relationships</h2>
          <div className="max-h-64 overflow-auto">
            <table className="w-full text-left text-sm">
              <thead><tr><th scope="col">Source</th><th scope="col">Type</th><th scope="col">Target</th><th scope="col">Evidence</th></tr></thead>
              <tbody>{edges.map(edge => (
                <tr className="border-t" key={edge.relation_ref}>
                  <td>{edge.source_ref}</td><td>{edge.kind}</td><td>{edge.target_ref}</td>
                  <td>{edge.source_evidence_ref ?? "Not linked"}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        </section>}
      </>}
    </section>
  );
}

export const Route = createFileRoute("/spatial")({ component: SpatialAssembly });
