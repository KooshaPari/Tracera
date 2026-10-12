// Node-link graph of project artifacts: items are nodes, trace links are edges.
import { useParams } from "@tanstack/react-router";
import { useEffect, useMemo, useRef, useState } from "react";

import { type ArtifactItem, useProjectGraphData } from "./useProjectGraphData";

const TYPE_ORDER = ["epic", "adr", "user_story", "feature", "requirement", "task", "component", "test"];
const TYPE_COLOR: Record<string, string> = {
  adr: "#a855f7",
  component: "#f59e0b",
  epic: "#ef4444",
  feature: "#14b8a6",
  requirement: "#3b82f6",
  task: "#64748b",
  test: "#22c55e",
  user_story: "#ec4899",
};
const COL_W = 190;
const ROW_H = 26;
const MAX_NODES = 200;

function rank(type: string): number {
  const idx = TYPE_ORDER.indexOf(type);
  return idx === -1 ? TYPE_ORDER.length : idx;
}

interface Placed {
  item: ArtifactItem;
  x: number;
  y: number;
  degree: number;
}

export function GraphArtifactView({ projectId: projectIdProp }: { projectId?: string | undefined }) {
  const params = useParams({ strict: false }) as { projectId?: string };
  const projectId = projectIdProp ?? params.projectId;
  const { data, error, isLoading } = useProjectGraphData(projectId);
  const [hidden, setHidden] = useState<Set<string>>(new Set());
  const [selected, setSelected] = useState<string | null>(null);
  const [view, setView] = useState({ k: 1, x: 20, y: 20 });
  const drag = useRef<{ x: number; y: number } | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);
  const fitted = useRef(false);

  const model = useMemo(() => {
    if (!data) return null;
    const degree = new Map<string, number>();
    for (const l of data.links) {
      degree.set(l.source_id, (degree.get(l.source_id) ?? 0) + 1);
      degree.set(l.target_id, (degree.get(l.target_id) ?? 0) + 1);
    }
    const types = [...new Set(data.items.map((i) => i.type))].sort((a, b) => rank(a) - rank(b));
    const visible = data.items
      .filter((i) => !hidden.has(i.type))
      .sort((a, b) => (degree.get(b.id) ?? 0) - (degree.get(a.id) ?? 0))
      .slice(0, MAX_NODES);
    const byType = new Map<string, ArtifactItem[]>();
    for (const it of visible) byType.set(it.type, [...(byType.get(it.type) ?? []), it]);
    const cols = [...byType.keys()].sort((a, b) => rank(a) - rank(b));
    const placed = new Map<string, Placed>();
    cols.forEach((t, ci) => {
      (byType.get(t) ?? []).forEach((it, ri) => {
        placed.set(it.id, { degree: degree.get(it.id) ?? 0, item: it, x: ci * COL_W, y: ri * ROW_H });
      });
    });
    const edges = data.links.filter((l) => placed.has(l.source_id) && placed.has(l.target_id));
    const hiddenCount = data.items.length - visible.length;
    return { cols, edges, hiddenCount, placed, total: data.items.length, totalLinks: data.links.length, types };
  }, [data, hidden]);

  useEffect(() => {
    if (!model || fitted.current || !svgRef.current) return;
    const w = svgRef.current.clientWidth || 600;
    const need = Math.max(1, model.cols.length) * COL_W;
    fitted.current = true;
    setView({ k: Math.min(1, Math.max(0.25, (w - 40) / need)), x: 20, y: 24 });
  }, [model]);

  if (isLoading) return <div className="p-6 text-sm">Loading graph...</div>;
  if (error || !model) return <div className="text-destructive p-6" role="alert">Failed to load graph data: {String(error)}</div>;

  const neighbors = new Set<string>();
  if (selected) {
    neighbors.add(selected);
    for (const e of model.edges) {
      if (e.source_id === selected) neighbors.add(e.target_id);
      if (e.target_id === selected) neighbors.add(e.source_id);
    }
  }
  const sel = selected ? model.placed.get(selected)?.item : undefined;
  const maxY = Math.max(...[...model.placed.values()].map((p) => p.y), 0) + 60;

  return (
    <div className="flex h-[calc(100vh-180px)] min-h-[480px] flex-col gap-3" data-testid="graph-artifact-view">
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="font-semibold">{model.total} items, {model.totalLinks} links</span>
        {model.hiddenCount > 0 && (
          <span className="text-muted-foreground">showing top {MAX_NODES} by connections ({model.hiddenCount} more hidden)</span>
        )}
        {model.types.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setHidden((h) => { const n = new Set(h); if (n.has(t)) n.delete(t); else n.add(t); return n; })}
            className="rounded border px-2 py-0.5"
            style={{ background: hidden.has(t) ? "transparent" : TYPE_COLOR[t] ?? "#888", color: hidden.has(t) ? "inherit" : "white" }}
          >
            {t}
          </button>
        ))}
        <button type="button" className="rounded border px-2 py-0.5" onClick={() => { fitted.current = false; setView({ k: 0.99, x: 20, y: 24 }); }}>reset view</button>
      </div>
      <div className="relative flex min-h-0 flex-1 gap-3">
        <svg
          ref={svgRef}
          className="bg-card min-w-0 flex-1 cursor-grab rounded-lg border"
          onWheel={(e) => setView((v) => ({ ...v, k: Math.min(3, Math.max(0.2, v.k * (e.deltaY < 0 ? 1.1 : 0.9))) }))}
          onMouseDown={(e) => { drag.current = { x: e.clientX, y: e.clientY }; }}
          onMouseUp={() => { drag.current = null; }}
          onMouseLeave={() => { drag.current = null; }}
          onMouseMove={(e) => {
            if (!drag.current) return;
            const dx = e.clientX - drag.current.x;
            const dy = e.clientY - drag.current.y;
            drag.current = { x: e.clientX, y: e.clientY };
            setView((v) => ({ ...v, x: v.x + dx, y: v.y + dy }));
          }}
        >
          <g transform={`translate(${view.x},${view.y}) scale(${view.k})`}>
            {model.cols.map((t, ci) => (
              <text key={t} x={ci * COL_W} y={-6} fontSize={11} fontWeight={700} fill={TYPE_COLOR[t] ?? "#888"}>{t.toUpperCase()}</text>
            ))}
            {model.edges.map((e) => {
              const a = model.placed.get(e.source_id);
              const b = model.placed.get(e.target_id);
              if (!a || !b) return null;
              const on = !selected || (neighbors.has(e.source_id) && neighbors.has(e.target_id));
              const x1 = a.x + 150;
              const x2 = b.x;
              const mx = (x1 + x2) / 2;
              return (
                <path
                  key={e.id}
                  d={`M${x1},${a.y} C${mx},${a.y} ${mx},${b.y} ${x2},${b.y}`}
                  fill="none"
                  stroke={on ? "#64748b" : "#cbd5e1"}
                  strokeOpacity={on ? 0.7 : 0.15}
                  strokeWidth={on && selected ? 1.6 : 0.8}
                />
              );
            })}
            {[...model.placed.values()].map((p) => {
              const dim = selected && !neighbors.has(p.item.id);
              return (
                <g key={p.item.id} transform={`translate(${p.x},${p.y})`} opacity={dim ? 0.25 : 1} onClick={(ev) => { ev.stopPropagation(); setSelected(p.item.id === selected ? null : p.item.id); }} style={{ cursor: "pointer" }}>
                  <circle r={5} fill={TYPE_COLOR[p.item.type] ?? "#888"} stroke={p.item.id === selected ? "#000" : "none"} strokeWidth={2} />
                  <text x={9} y={4} fontSize={10} fill="currentColor">{p.item.title.length > 22 ? `${p.item.title.slice(0, 22)}...` : p.item.title}</text>
                </g>
              );
            })}
          </g>
        </svg>
        <aside className={`bg-card/95 absolute right-2 top-2 z-10 max-h-[90%] w-72 overflow-auto rounded-lg border p-3 text-xs ${sel ? "" : "pointer-events-none opacity-70"}`}>
          {sel ? (
            <div className="space-y-2">
              <div className="text-sm font-semibold">{sel.title}</div>
              <div>{sel.type} | {sel.status} | {sel.view}</div>
              <div className="text-muted-foreground whitespace-pre-wrap">{sel.description?.slice(0, 600)}</div>
              <div className="font-semibold">Linked ({neighbors.size - 1})</div>
              {model.edges.filter((e) => e.source_id === sel.id || e.target_id === sel.id).map((e) => {
                const other = model.placed.get(e.source_id === sel.id ? e.target_id : e.source_id)?.item;
                return <div key={e.id}>{e.source_id === sel.id ? "->" : "<-"} {e.type}: {other?.title}</div>;
              })}
            </div>
          ) : (
            <div className="text-muted-foreground">Click a node to highlight its trace links. Drag to pan, wheel to zoom. Toggle types above.</div>
          )}
        </aside>
      </div>
    </div>
  );
}
