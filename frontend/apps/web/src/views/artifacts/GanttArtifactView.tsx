// Gantt: scheduled bars per work item, grouped under parents, ordered in sequence.
// Items carry no dates, so the axis is sequence steps and bars show status.
import { useMemo, useState } from "react";

import { useProjectGraphData } from "./useProjectGraphData";

const WORK = ["epic", "feature", "user_story", "task"];
const ROW = 16;
const LABEL = 300;
const STEP = 14;
const DONE = new Set(["done", "closed", "complete", "completed", "resolved"]);

export function GanttArtifactView({ projectId }: { projectId?: string | undefined }) {
  const { data, isLoading, error } = useProjectGraphData(projectId);
  const [open, setOpen] = useState<Set<string>>(new Set());

  const model = useMemo(() => {
    if (!data) return null;
    const work = data.items.filter((i) => WORK.includes(i.type));
    const ids = new Set(work.map((i) => i.id));
    const parent = new Map<string, string>();
    for (const l of data.links) {
      if (l.type === "part_of" && ids.has(l.source_id) && ids.has(l.target_id)) parent.set(l.source_id, l.target_id);
    }
    const kids = new Map<string, string[]>();
    for (const [c, p] of parent) kids.set(p, [...(kids.get(p) ?? []), c]);
    const byId = new Map(work.map((i) => [i.id, i]));
    const roots = work.filter((i) => !parent.has(i.id));
    return { byId, kids, roots };
  }, [data]);

  if (isLoading) return <div className="p-6 text-sm">Loading gantt...</div>;
  if (error || !model) return <div className="p-6 text-sm text-red-500">Failed to load: {String(error)}</div>;

  const rows: { id: string; depth: number; start: number; len: number }[] = [];
  const walk = (id: string, depth: number, start: number): number => {
    const ch = model.kids.get(id) ?? [];
    let cursor = start;
    const at = rows.length;
    rows.push({ id, depth, start, len: 1 });
    if (open.has(id) || depth === 0) {
      for (const c of ch) cursor = walk(c, depth + 1, cursor);
    } else {
      cursor = start + Math.max(1, ch.length);
    }
    const row = rows[at];
    if (row) row.len = Math.max(1, cursor - start);
    return cursor;
  };
  let t = 0;
  for (const r of model.roots.slice(0, 400)) t = walk(r.id, 0, t > 0 ? 0 : 0);
  const maxEnd = Math.max(1, ...rows.map((r) => r.start + r.len));
  const width = LABEL + maxEnd * STEP + 30;
  const height = rows.length * ROW + 24;
  const toggle = (id: string) => {
    const n = new Set(open);
    if (n.has(id)) n.delete(id);
    else n.add(id);
    setOpen(n);
  };

  return (
    <div className="flex h-full flex-col gap-2 p-4 text-sm">
      <div className="flex items-center gap-4">
        <span className="font-semibold">Gantt</span>
        <span>{rows.length} rows</span>
        <span className="text-xs opacity-70">Items carry no dates; the axis is sequence steps. Click a row to expand its children.</span>
      </div>
      <div className="overflow-auto rounded border" style={{ maxHeight: "72vh" }}>
        <svg width={width} height={height}>
          {Array.from({ length: Math.ceil(maxEnd / 5) + 1 }, (_, i) => (
            <g key={i}>
              <line x1={LABEL + i * 5 * STEP} x2={LABEL + i * 5 * STEP} y1={14} y2={height} stroke="#ffffff14" />
              <text x={LABEL + i * 5 * STEP + 2} y={10} fontSize={8} fill="#94a3b8">{`step ${i * 5}`}</text>
            </g>
          ))}
          {rows.map((r, i) => {
            const it = model.byId.get(r.id);
            if (!it) return null;
            const done = DONE.has((it.status || "").toLowerCase());
            const y = 18 + i * ROW;
            const parentRow = (model.kids.get(r.id)?.length ?? 0) > 0;
            return (
              <g key={r.id} onClick={() => parentRow && toggle(r.id)} style={{ cursor: parentRow ? "pointer" : "default" }}>
                <text x={6 + r.depth * 12} y={y + 10} fontSize={9} fill="#cbd5e1">{`${parentRow ? (open.has(r.id) || r.depth === 0 ? "v " : "> ") : ""}${it.title.slice(0, 46 - r.depth * 2)}`}</text>
                <rect
                  x={LABEL + r.start * STEP}
                  y={y + 2}
                  width={Math.max(6, r.len * STEP - 2)}
                  height={ROW - 5}
                  rx={2}
                  fill={done ? "#22c55e" : parentRow ? "#3b82f6" : "#64748b"}
                >
                  <title>{`${it.title} (${it.type}, ${it.status})`}</title>
                </rect>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}

export default GanttArtifactView;
