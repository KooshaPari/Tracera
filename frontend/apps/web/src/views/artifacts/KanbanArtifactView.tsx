// Kanban board: items grouped into status columns as cards.
import { useMemo, useState } from "react";

import { useProjectGraphData } from "./useProjectGraphData";

const ORDER = ["backlog", "todo", "open", "planned", "draft", "in_progress", "doing", "review", "blocked", "done", "closed", "complete", "completed"];
const TYPE_COLOR: Record<string, string> = {
  epic: "#ef4444", requirement: "#3b82f6", adr: "#a855f7", component: "#f59e0b", test: "#22c55e",
  task: "#06b6d4", user_story: "#ec4899", feature: "#eab308",
};

export function KanbanArtifactView({ projectId }: { projectId?: string | undefined }) {
  const { data, isLoading, error } = useProjectGraphData(projectId);
  const [type, setType] = useState("all");
  const [q, setQ] = useState("");
  const [open, setOpen] = useState<string>("");

  const model = useMemo(() => {
    if (!data) return null;
    const types = Array.from(new Set(data.items.map((i) => i.type))).sort();
    const linkCount = new Map<string, number>();
    for (const l of data.links) {
      linkCount.set(l.source_id, (linkCount.get(l.source_id) ?? 0) + 1);
      linkCount.set(l.target_id, (linkCount.get(l.target_id) ?? 0) + 1);
    }
    return { types, linkCount };
  }, [data]);

  if (isLoading) return <div className="p-6 text-sm">Loading board...</div>;
  if (error || !data || !model) return <div className="p-6 text-sm text-red-500">Failed to load: {String(error)}</div>;

  const items = data.items.filter(
    (i) => (type === "all" || i.type === type) && i.title.toLowerCase().includes(q.toLowerCase()),
  );
  const cols = new Map<string, typeof items>();
  for (const i of items) {
    const s = i.status || "none";
    cols.set(s, [...(cols.get(s) ?? []), i]);
  }
  const names = Array.from(cols.keys()).sort((a, b) => {
    const ia = ORDER.indexOf(a.toLowerCase());
    const ib = ORDER.indexOf(b.toLowerCase());
    return (ia < 0 ? 50 : ia) - (ib < 0 ? 50 : ib) || a.localeCompare(b);
  });

  return (
    <div className="flex h-full flex-col gap-3 p-4">
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <span className="font-semibold">Board</span>
        <span>{items.length} items</span>
        <select className="rounded border bg-transparent px-2 py-1" value={type} onChange={(e) => setType(e.target.value)}>
          <option value="all">all types</option>
          {model.types.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <input className="rounded border bg-transparent px-2 py-1" placeholder="filter" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      <div className="flex flex-1 gap-3 overflow-x-auto pb-2" style={{ minHeight: 400 }}>
        {names.map((n) => {
          const list = cols.get(n) ?? [];
          return (
            <div key={n} className="flex w-64 shrink-0 flex-col rounded-lg border bg-black/20">
              <div className="flex items-center justify-between border-b px-3 py-2 text-xs font-semibold uppercase">
                <span>{n.replace(/_/g, " ")}</span>
                <span className="opacity-70">{list.length}</span>
              </div>
              <div className="flex flex-col gap-2 overflow-y-auto p-2" style={{ maxHeight: "68vh" }}>
                {list.slice(0, 100).map((i) => (
                  <button
                    key={i.id}
                    type="button"
                    onClick={() => setOpen(open === i.id ? "" : i.id)}
                    className="rounded border bg-card p-2 text-left text-xs"
                    style={{ borderLeft: `3px solid ${TYPE_COLOR[i.type] ?? "#94a3b8"}` }}
                  >
                    <div className="font-medium">{i.title.slice(0, 90)}</div>
                    <div className="mt-1 flex gap-2 opacity-70">
                      <span>{i.type}</span>
                      <span>{model.linkCount.get(i.id) ?? 0} links</span>
                    </div>
                    {open === i.id && i.description ? <div className="mt-2 whitespace-pre-wrap opacity-90">{i.description.slice(0, 400)}</div> : null}
                  </button>
                ))}
                {list.length > 100 ? <div className="p-1 text-xs opacity-60">+{list.length - 100} more (filter to narrow)</div> : null}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default KanbanArtifactView;
