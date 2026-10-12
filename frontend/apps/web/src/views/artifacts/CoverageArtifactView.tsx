// Coverage matrix: requirements (rows) x verifying artifacts (columns), cells from trace links.
import { useMemo, useState } from "react";

import { useProjectGraphData } from "./useProjectGraphData";

const COVER_TYPES = new Set(["tests", "verifies", "implements"]);
const CELL = 9;
const LABEL_W = 280;
const HEAD_H = 14;

export function CoverageArtifactView({ projectId }: { projectId?: string | undefined }) {
  const { data, isLoading, error } = useProjectGraphData(projectId);
  const [gapsOnly, setGapsOnly] = useState(false);
  const [colType, setColType] = useState<string>("test");
  const [rowSel, setRowSel] = useState<string>("");
  const [q, setQ] = useState("");
  const [hover, setHover] = useState<string>("");

  const model = useMemo(() => {
    if (!data) return null;
    const byId = new Map(data.items.map((i) => [i.id, i]));
    const counts = new Map<string, number>();
    const linkedRows = new Map<string, Set<string>>();
    for (const l of data.links) {
      if (!COVER_TYPES.has(l.type)) continue;
      for (const id of [l.source_id, l.target_id]) {
        const t = byId.get(id)?.type;
        if (t && t !== "test") {
          counts.set(t, (counts.get(t) ?? 0) + 1);
          const s2 = linkedRows.get(t) ?? new Set<string>();
          s2.add(id);
          linkedRows.set(t, s2);
        }
      }
    }
    const rowTypes = Array.from(new Set(data.items.filter((i) => i.type !== "test").map((i) => i.type)));
    const bestRow = (counts.get("requirement") ?? 0) > 0 ? "requirement" : ([...counts.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] ?? "requirement");
    const rowType = rowSel || bestRow;
    const reqs = data.items.filter((i) => i.type === rowType);
    const reqIds = new Set(reqs.map((r) => r.id));
    const cover = new Map<string, Set<string>>();
    for (const l of data.links) {
      if (!COVER_TYPES.has(l.type)) continue;
      let r = l.source_id;
      let o = l.target_id;
      if (!reqIds.has(r)) [r, o] = [o, r];
      if (!reqIds.has(r)) continue;
      const set = cover.get(r) ?? new Set<string>();
      set.add(o);
      cover.set(r, set);
    }
    const types = Array.from(new Set(data.items.map((i) => i.type)));
    return { byId, reqs, cover, types, rowTypes, rowType };
  }, [data, rowSel]);

  if (isLoading) return <div className="p-6 text-sm">Loading coverage matrix...</div>;
  if (error || !model) return <div className="p-6 text-sm text-red-500">Failed to load: {String(error)}</div>;

  const covered = model.reqs.filter((r) => (model.cover.get(r.id)?.size ?? 0) > 0).length;
  const total = model.reqs.length;
  const pct = total ? Math.round((covered / total) * 1000) / 10 : 0;

  let rows = model.reqs.filter((r) => r.title.toLowerCase().includes(q.toLowerCase()));
  if (gapsOnly) rows = rows.filter((r) => (model.cover.get(r.id)?.size ?? 0) === 0);
  rows = [...rows].sort((a, b) => (model.cover.get(b.id)?.size ?? 0) - (model.cover.get(a.id)?.size ?? 0));

  const colOrder: string[] = [];
  const seen = new Set<string>();
  for (const r of rows) {
    for (const t of model.cover.get(r.id) ?? []) {
      const it = model.byId.get(t);
      if (it && it.type === colType && !seen.has(t)) {
        seen.add(t);
        colOrder.push(t);
      }
    }
  }
  const colIdx = new Map(colOrder.map((id, i) => [id, i]));
  const width = LABEL_W + colOrder.length * CELL + 20;
  const height = HEAD_H + rows.length * CELL + 10;

  return (
    <div className="flex h-full flex-col gap-3 p-4">
      <div className="flex flex-wrap items-center gap-4 text-sm">
        <span className="font-semibold">Coverage matrix</span>
        <select className="rounded border bg-transparent px-2 py-1" value={model.rowType} onChange={(e) => setRowSel(e.target.value)}>
          {model.rowTypes.map((t) => (
            <option key={t} value={t}>{`rows: ${t}`}</option>
          ))}
        </select>
        <span>{total} rows</span>
        <span className="text-green-500">{covered} covered</span>
        <span className="text-red-500">{total - covered} uncovered</span>
        <span className="font-semibold">{pct}%</span>
        <select className="rounded border bg-transparent px-2 py-1" value={colType} onChange={(e) => setColType(e.target.value)}>
          {model.types.map((t) => (
            <option key={t} value={t}>{`columns: ${t}`}</option>
          ))}
        </select>
        <label className="flex items-center gap-1">
          <input type="checkbox" checked={gapsOnly} onChange={(e) => setGapsOnly(e.target.checked)} /> gaps only
        </label>
        <input className="rounded border bg-transparent px-2 py-1" placeholder="filter rows" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      <div className="h-3 w-full rounded bg-red-900/40">
        <div className="h-3 rounded bg-green-500" style={{ width: `${pct}%` }} />
      </div>
      <div className="min-h-[24px] text-xs opacity-80">{hover || "Hover a cell for requirement and verifying artifact. Rows sorted by coverage count."}</div>
      <div className="overflow-auto rounded border" style={{ maxHeight: "70vh" }}>
        <svg width={width} height={height} role="img" aria-label="coverage matrix">
          {rows.map((r, ri) => {
            const set = model.cover.get(r.id);
            const y = HEAD_H + ri * CELL;
            return (
              <g key={r.id}>
                <text x={4} y={y + CELL - 1} fontSize={7} fill={set && set.size ? "#cbd5e1" : "#f87171"}>
                  {`${set?.size ?? 0} | ${r.title.slice(0, 52)}`}
                </text>
                <line x1={LABEL_W} x2={width} y1={y + CELL} y2={y + CELL} stroke="#ffffff10" />
                {Array.from(set ?? []).map((t) => {
                  const ci = colIdx.get(t);
                  if (ci === undefined) return null;
                  return (
                    <rect
                      key={t}
                      x={LABEL_W + ci * CELL}
                      y={y + 1}
                      width={CELL - 2}
                      height={CELL - 2}
                      fill="#22c55e"
                      onMouseEnter={() => setHover(`${r.title}  <-  ${model.byId.get(t)?.title ?? t}`)}
                    />
                  );
                })}
              </g>
            );
          })}
          <text x={LABEL_W} y={10} fontSize={8} fill="#94a3b8">{`${colOrder.length} ${colType} columns`}</text>
        </svg>
      </div>
    </div>
  );
}

export default CoverageArtifactView;
