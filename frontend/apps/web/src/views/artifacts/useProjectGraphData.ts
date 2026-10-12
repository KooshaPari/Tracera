// Fetches every item and link of a project from the canonical API.
import { useQuery } from "@tanstack/react-query";

import { client } from "@/api/client";

const { getAuthHeaders, getBackendURL } = client;

export interface ArtifactItem {
  id: string;
  title: string;
  type: string;
  view: string;
  status: string;
  description?: string;
}
export interface ArtifactLink {
  id: string;
  source_id: string;
  target_id: string;
  type: string;
}

async function getJson(path: string): Promise<Record<string, unknown>> {
  const res = await fetch(`${getBackendURL(path)}${path}`, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`${path}: HTTP ${res.status}`);
  const ct = res.headers.get("content-type") ?? "";
  if (!ct.includes("json")) throw new Error(`${path}: non-JSON response`);
  return (await res.json()) as Record<string, unknown>;
}

async function loadAll<T>(base: string, key: string, projectId: string): Promise<T[]> {
  const out: T[] = [];
  const pid = encodeURIComponent(projectId);
  for (let guard = 0; guard < 60; guard += 1) {
    const page = await getJson(`${base}?project_id=${pid}&limit=500&skip=${out.length}`);
    const rows = (page[key] as T[] | undefined) ?? [];
    out.push(...rows);
    const total = typeof page.total === "number" ? page.total : out.length;
    if (rows.length === 0 || out.length >= total) break;
  }
  return out;
}

export function useProjectGraphData(projectId: string | undefined) {
  return useQuery({
    enabled: Boolean(projectId),
    queryKey: ["artifact-data", projectId],
    staleTime: 30_000,
    queryFn: async () => {
      const [items, links] = await Promise.all([
        loadAll<ArtifactItem>("/api/v1/items", "items", projectId ?? ""),
        loadAll<ArtifactLink>("/api/v1/links", "links", projectId ?? ""),
      ]);
      return { items, links };
    },
  });
}
