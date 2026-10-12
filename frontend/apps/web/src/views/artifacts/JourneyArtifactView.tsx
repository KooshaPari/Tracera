// Journey swimlane: lanes per artifact type, steps ordered left to right by distance from entry points.
import { useMemo, useState } from "react";

import { useProjectGraphData } from "./useProjectGraphData";

const LANE_ORDER = ["epic", "user_story", "feature", "requirement", "adr", "task", "component", "test"];
const COLORS: Record<string, string> = {
  epic: "#ef4444", requirement: "#3b82f6", adr: "#a855f7", component: "#f59e0b", test: "#22c55e",
  task: "#06b6d4", user_story: "#ec4899", feature: "#eab308",
};
const STEP_W = 54;
const LANE_H = 120;
const HEAD_W = 110;

export function JourneyArtifactView({ projectId }: { projectId?: string | undefined }) {
  const { data, isLoading, error } = useProjectGraphData(projectId);
  const [sel, setSel] = useState("");

  const model = useMemo(() => {
    if (!data) return null;
    const adj = new Map<string, string[]>();
    for (const l of data.links) {
      adj.set(l.source_id, [...(adj.get(l.source_id) ?? []), l.target_id]);
      adj.set(l.target_id, [...(adj.get(l.target_id) ?? []), l.source_id]);
    }
    const byId = new Map(data.items.map((i) => [i.id, i]));
    const types = Array.from(new Set(data.items.map((i) => i.type))).sort(
      (a, b) => (LANE_ORDER.indexOf(a) < 0 ? 99 : LANE_ORDER.indexOf(a)) - (LANE_ORDER.indexOf(b) < 0 ? 99 : LANE_ORDER.indexOf(b)),
    );
    const entry = types[0] ?? "";
    const level = new Map<string, number>();
    let frontier = data.items.filter((i) => i.type === entry && (adj.get(i.id)?.length ?? 0) > 0).map((i) => i.id);
    frontier.forEach((id) => level.set(id, 0));
    while (frontier.length) {
      const next: string[] = [];
      for (const id of frontier) {
        for (const n of adj.get(id) ?? []) {
          if (!level.has(n)) {
            level.set(n, (level.get(id) ?? 0) + 1);
            next.push(n);
          }
        }
      }
      frontier = next;
    }
    const slots = new Map<string, number>();
    const placed = data.items
      .filter((i) => level.has(i.id))
      .sort((a, b) => (adj.get(b.id)?.length ?? 0) - (adj.get(a.id)?.length ?? 0))
      .slice(0, 260)
      .map((i) => {
        const key = `${i.type}|${level.get(i.id)}`;
        const n = slots.get(key) ?? 0;
        slots.set(key, n + 1);
        return { item: i, lane: types.indexOf(i.type), col: level.get(i.id) ?? 0, slot: n };
      });
    const pos = new Map(placed.map((p) => [p.item.id, p]));
    const maxCol = Math.max(0, ...placed.map((p) => p.col));
    const maxSlot = Math.max(1, ...placed.map((p) => p.slot + 1));
    return { types, placed, pos, maxCol, maxSlot, adj, byId, links: data.links };
  }, [data]);

  if (isLoading) return <div className="p-6 text-sm">Loading journey...</div>;
  if (error || !model) return <div className="p-6 text-sm text-red-500">Failed to load: {String(error)}</div>;

  const colW = Math.max(STEP_W, 14 * Math.min(model.maxSlot, 8));
  const laneH = Math.max(LANE_H, 14 * Math.min(model.maxSlot, 8) + 24);
  const px = (p: { col: number; slot: number }) => HEAD_W + p.col * colW + 12 + (p.slot % 8) * 12;
  const py = (p: { lane: number; slot: number }) => p.lane * laneH + 28 + Math.floor(p.slot / 8) * 12;
  const width = HEAD_W + (model.maxCol + 1) * colW + 40;
  const height = model.types.length * laneH + 20;
  const selected = model.byId.get(sel);
  const nbrs = new Set(sel ? model.adj.get(sel) ?? [] : []);

  return (
    <div className="flex h-full flex-col gap-2 p-4 text-sm">
      <div className="flex items-center gap-4">
        <span className="font-semibold">Journey map</span>
        <span>{model.placed.length} steps across {model.types.length} lanes, entry lane: {model.types[0]}</span>
      </div>
      <div className="min-h-[20px] text-xs opacity-80">{selected ? `${selected.type}: ${selected.title}` : "Click a step to trace its path. Steps move right with each hop from the entry lane."}</div>
      <div className="overflow-auto rounded border" style={{ maxHeight: "70vh" }}>
        <svg width={width} height={height}>
          {model.types.map((t, i) => (
            <g key={t}>
              <rect x={0} y={i * laneH} width={width} height={laneH} fill={i % 2 ? "#ffffff06" : "#ffffff0d"} />
              <text x={8} y={i * laneH + 18} fontSize={11} fontWeight={600} fill={COLORS[t] ?? "#94a3b8"}>{t}</text>
            </g>
          ))}
          {Array.from({ length: model.maxCol + 1 }, (_, c) => (
            <text key={c} x={HEAD_W + c * colW + 12} y={10} fontSize={8} fill="#94a3b8">{`hop ${c}`}</text>
          ))}
          {model.links.map((l) => {
            const a = model.pos.get(l.source_id);
            const b = model.pos.get(l.target_id);
            if (!a || !b) return null;
            const hot = sel && (l.source_id === sel || l.target_id === sel);
            if (sel && !hot) return null;
            return (
              <path
                key={l.id}
                d={`M${px(a)} ${py(a)} C${px(a) + 30} ${py(a)} ${px(b) - 30} ${py(b)} ${px(b)} ${py(b)}`}
                stroke={hot ? "#facc15" : "#94a3b822"}
                fill="none"
                strokeWidth={hot ? 1.5 : 0.5}
              />
            );
          })}
          {model.placed.map((p) => (
            <circle
              key={p.item.id}
              cx={px(p)}
              cy={py(p)}
              r={sel === p.item.id ? 6 : 4.5}
              fill={COLORS[p.item.type] ?? "#94a3b8"}
              opacity={!sel || sel === p.item.id || nbrs.has(p.item.id) ? 1 : 0.3}
              onClick={() => setSel(sel === p.item.id ? "" : p.item.id)}
              style={{ cursor: "pointer" }}
            >
              <title>{p.item.title}</title>
            </circle>
          ))}
        </svg>
      </div>
    </div>
  );
}

export default JourneyArtifactView;
