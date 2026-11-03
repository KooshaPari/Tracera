// Project-specific item/link graph. These endpoints are distinct from the SWEE graph API.

import { useInfiniteQuery } from "@tanstack/react-query";
import { useParams } from "@tanstack/react-router";
import { useMemo } from "react";

import { client } from "@/api/client";
import { UnifiedGraphView } from "@/components/graph/UnifiedGraphView";
import { useAuthStore } from "@/stores/authStore";
import { Badge } from "@tracertm/ui/components/Badge";
import { Skeleton } from "@tracertm/ui/components/Skeleton";

const { getAuthHeaders, getBackendURL } = client;
let graphAuthScope = 0;

function checkedPage(body: unknown, key: "items" | "links", projectId: string, offset: number) {
  if (!body || typeof body !== "object" || Array.isArray(body))
    throw new Error("Invalid graph response");
  const record = body as Record<string, unknown>;
  const rows = record[key];
  const total = record.total;
  if (
    !Array.isArray(rows) ||
    !Number.isSafeInteger(total) ||
    typeof total !== "number" ||
    total < offset + rows.length ||
    (rows.length === 0 && total > offset)
  ) {
    throw new Error("Invalid graph page");
  }
  const ids = new Set<string>();
  for (const value of rows) {
    if (!value || typeof value !== "object" || Array.isArray(value))
      throw new Error("Invalid graph record");
    const row = value as Record<string, unknown>;
    const id = row.id;
    if (
      typeof id !== "string" ||
      !id.trim() ||
      ids.has(id) ||
      (row.projectId ?? row.project_id) !== projectId
    )
      throw new Error("Invalid graph scope");
    ids.add(id);
    if (key === "links") {
      const fields = [
        row.sourceId ?? row.source_id,
        row.targetId ?? row.target_id,
        row.type ?? row.link_type,
      ];
      if (fields.some((field) => typeof field !== "string" || !field.trim()))
        throw new Error("Invalid relationship");
    }
  }
  return { rows, total };
}

function getGraphBackendURL(): string {
  return getBackendURL("/api/v1/links");
}

interface GraphViewProps {
  projectId?: string;
}

export function GraphView({ projectId: projectIdProp }: GraphViewProps) {
  const { projectId } = useParams({ strict: false });
  const resolvedProjectId = projectIdProp ?? projectId;
  const token = useAuthStore((state) => state.token);
  const accountId = useAuthStore((state) => state.account?.id);
  const userId = useAuthStore((state) => state.user?.id);
  const effectiveAuthorization = getAuthHeaders().Authorization;
  // Do not expose the bearer token in the query key. A new scope prevents
  // records fetched under one authenticated session from being reused by another.
  const authScope = useMemo(() => {
    graphAuthScope += 1;
    return graphAuthScope;
  }, [token, accountId, userId, effectiveAuthorization]);

  const pageSizeItems = 100; // The Rust item endpoint accepts at most 100.
  const pageSizeLinks = 500;

  // This is a bounded preview, not a complete product graph.
  const MAX_NODES = 200;
  const MAX_EDGES = 250;

  const itemsQuery = useInfiniteQuery<{ items?: unknown[]; total?: number }>({
    enabled: Boolean(resolvedProjectId),
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.reduce((sum: number, p) => sum + (p.items?.length ?? 0), 0);
      const total = lastPage.total ?? 0;
      return loaded < total ? loaded : undefined;
    },
    initialPageParam: 0,
    queryFn: async ({ pageParam }) => {
      const base = getGraphBackendURL();
      const res = await fetch(
        `${base}/api/v1/items?${new URLSearchParams({ project_id: resolvedProjectId ?? "", limit: String(pageSizeItems), offset: String(pageParam) })}`,
        {
          headers: {
            "X-Bulk-Operation": "true",
            ...getAuthHeaders(),
          },
        },
      );
      if (!res.ok) {
        throw new Error("Failed to fetch items");
      }
      const page = checkedPage(
        await res.json(),
        "items",
        resolvedProjectId ?? "",
        Number(pageParam),
      );
      return { items: page.rows, total: page.total };
    },
    queryKey: ["graph-items", resolvedProjectId, authScope],
  });

  const linksQuery = useInfiniteQuery<{ links?: unknown[]; total?: number }>({
    enabled: Boolean(resolvedProjectId),
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.reduce((sum: number, p) => sum + (p.links?.length ?? 0), 0);
      const total = lastPage.total ?? 0;
      return loaded < total ? loaded : undefined;
    },
    initialPageParam: 0,
    queryFn: async ({ pageParam }) => {
      const base = getGraphBackendURL();
      const res = await fetch(
        `${base}/api/v1/links?${new URLSearchParams({ project_id: resolvedProjectId ?? "", limit: String(pageSizeLinks), skip: String(pageParam) })}`,
        {
          headers: {
            "X-Bulk-Operation": "true", // Python backend skips rate limit when present
            ...getAuthHeaders(),
          },
        },
      );
      if (!res.ok) {
        throw new Error("Failed to fetch links");
      }
      const page = checkedPage(
        await res.json(),
        "links",
        resolvedProjectId ?? "",
        Number(pageParam),
      );
      return { links: page.rows, total: page.total };
    },
    queryKey: ["graph-links", resolvedProjectId, authScope],
  });

  const items = itemsQuery.data?.pages.flatMap((p: any) => p.items ?? []) ?? [];
  const rawLinks = linksQuery.data?.pages.flatMap((p: any) => p.links ?? []) ?? [];
  const itemsLoading = itemsQuery.isLoading || itemsQuery.isFetching;
  const linksLoading = linksQuery.isLoading || linksQuery.isFetching;
  const isPriming =
    !itemsQuery.data || !linksQuery.data || itemsQuery.isLoading || linksQuery.isLoading;

  // Map snake_case API response to camelCase for graph components
  const links = rawLinks.map((link: any) =>
    Object.assign(link, {
      sourceId: link.source_id ?? link.sourceId,
      targetId: link.target_id ?? link.targetId,
      type: link.link_type ?? link.type,
    }),
  );

  const visibleItems = items.slice(0, MAX_NODES);
  const visibleNodeIds = new Set(visibleItems.map((i: any) => i.id));
  const visibleLinks = links
    .filter((l: any) => visibleNodeIds.has(l.sourceId) && visibleNodeIds.has(l.targetId))
    .slice(0, MAX_EDGES);

  if (!resolvedProjectId) {
    return (
      <div role="alert" className="p-6">
        Select a project to view its graph.
      </div>
    );
  }
  if (itemsQuery.isError || linksQuery.isError) {
    return (
      <div role="alert" className="p-6">
        Graph data is unavailable. Items or relationships could not be loaded.
      </div>
    );
  }
  const itemsTotal = itemsQuery.data?.pages[0]?.total;
  const linksTotal = linksQuery.data?.pages[0]?.total;
  const incomplete =
    typeof itemsTotal === "number" &&
    typeof linksTotal === "number" &&
    (visibleItems.length < itemsTotal || visibleLinks.length < linksTotal);

  return (
    <div className="relative h-full">
      {!isPriming && <p className="p-3">Graph preview: item navigation is unavailable.</p>}
      {incomplete && (
        <p role="status" className="p-3">
          Partial graph: showing {visibleItems.length} of {itemsTotal} items and{" "}
          {visibleLinks.length} of {linksTotal} relationships. Additional data or relationships
          outside the visible items are not shown.
        </p>
      )}
      {(itemsLoading || linksLoading) && (
        <div className="absolute top-6 right-6 z-20">
          <Badge variant="outline" className="gap-2 text-xs">
            <span className="bg-primary inline-flex h-2 w-2 animate-pulse rounded-full" />
            Loading graph
          </Badge>
        </div>
      )}

      {isPriming ? (
        <div className="space-y-4 p-6">
          <Skeleton className="h-10 w-56" />
          <Skeleton className="h-[calc(100vh-220px)] w-full" />
        </div>
      ) : (
        <UnifiedGraphView
          items={visibleItems}
          links={visibleLinks}
          isLoading={itemsLoading || linksLoading}
          projectId={resolvedProjectId}
        />
      )}
    </div>
  );
}
