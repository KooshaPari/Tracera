/** Canonical graph edits always identify their project, including item IDs reused by imports. */
export function scopedGraphPath(kind: "items" | "links", id: string, projectId: string): string {
  if (!projectId?.trim()) throw new Error("Select a project before editing.");
  return `/api/v1/${kind}/${encodeURIComponent(id)}?project_id=${encodeURIComponent(projectId)}`;
}
export function canonicalItemPayload(data: Record<string, unknown>, create = false): Record<string, unknown> {
  const allowed = new Set(["title", "view", "type", "status", "description", ...(create ? ["projectId", "id"] : [])]);
  for (const [key, value] of Object.entries(data)) {
    if (value !== undefined && !allowed.has(key)) throw new Error(`${key} is not supported by graph editing.`);
  }
  if (create && !(typeof data.projectId === "string" && data.projectId.trim())) throw new Error("Select a project before creating a node.");
  const payload = Object.fromEntries(Object.entries(data).filter(([, value]) => value !== undefined));
  if (create) { payload.project_id = payload.projectId; delete payload.projectId; }
  return payload;
}
