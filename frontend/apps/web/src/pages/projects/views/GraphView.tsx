// Project-specific Graph View - Unified view with sidebar navigation
// Provides separated views: traceability, page flow, component library, and perspectives
// Reads items and links from one configured API origin.

import { useInfiniteQuery } from "@tanstack/react-query";
import { useNavigate, useParams } from "@tanstack/react-router";
import { useEffect, useState } from "react";

import { client } from "@/api/client";
import { UnifiedGraphView } from "@/components/graph/UnifiedGraphView";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import { graphLinkForView, graphVisibility } from "./graphVisibility";

const { getAuthHeaders, getBackendURL } = client;

/** Both graph collections must resolve to the same backend origin. */
function getGraphBackendURL(): string {
  return getBackendURL("/api/v1/links");
}

interface GraphViewProps {
  projectId?: string;
}

export function GraphView({ projectId: projectIdProp }: GraphViewProps) {
  const { projectId } = useParams({ strict: false });
  const resolvedProjectId = projectIdProp ?? projectId;
  const navigate = useNavigate();

  // Fetch one bounded page at a time and expose the remaining work to users.
  const pageSizeItems = 200;
  const pageSizeLinks = 500;
  const [visibleNodeCount, setVisibleNodeCount] = useState(pageSizeItems);
  const [visibleEdgeCount, setVisibleEdgeCount] = useState(250);

  useEffect(() => {
    setVisibleNodeCount(pageSizeItems);
    setVisibleEdgeCount(250);
  }, [resolvedProjectId]);

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
        `${base}/api/v1/items?project_id=${encodeURIComponent(resolvedProjectId ?? "")}&limit=${pageSizeItems}&skip=${pageParam}`,
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
      return res.json();
    },
    queryKey: ["graph-items", resolvedProjectId],
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
        `${base}/api/v1/links?project_id=${encodeURIComponent(resolvedProjectId ?? "")}&limit=${pageSizeLinks}&skip=${pageParam}`,
        {
          headers: {
            "X-Bulk-Operation": "true",
            ...getAuthHeaders(),
          },
        },
      );
      if (!res.ok) {
        throw new Error("Failed to fetch links");
      }
      return res.json();
    },
    queryKey: ["graph-links", resolvedProjectId],
  });

  const items = (itemsQuery.data?.pages.flatMap((p: any) => p.items ?? []) ?? []).map(
    (item: any) => ({ ...item, projectId: resolvedProjectId }),
  );
  const rawLinks = linksQuery.data?.pages.flatMap((p: any) => p.links ?? []) ?? [];
  const itemsTotal = itemsQuery.data?.pages.at(-1)?.total ?? items.length;
  const linksTotal = linksQuery.data?.pages.at(-1)?.total ?? rawLinks.length;
  const itemsLoading = itemsQuery.isLoading || itemsQuery.isFetching;
  const linksLoading = linksQuery.isLoading || linksQuery.isFetching;
  const isPriming = (itemsLoading || linksLoading) && items.length === 0;

  // Map the API response without mutating React Query's cached pages.
  const links = rawLinks.map((link: any) => graphLinkForView(link, resolvedProjectId ?? ""));

  const { visibleItems, visibleLinks, unavailableEndpointLinks, canLoadMore } = graphVisibility(
    items,
    links,
    visibleNodeCount,
    visibleEdgeCount,
    Boolean(itemsQuery.hasNextPage),
    Boolean(linksQuery.hasNextPage),
  );

  const handleLoadMore = () => {
    setVisibleNodeCount((count) => count + pageSizeItems);
    setVisibleEdgeCount((count) => count + pageSizeLinks);
    if (itemsQuery.hasNextPage && !itemsQuery.isFetchingNextPage) {
      void itemsQuery.fetchNextPage();
    }
    if (linksQuery.hasNextPage && !linksQuery.isFetchingNextPage) {
      void linksQuery.fetchNextPage();
    }
  };

  const handleNavigateToItem = (itemId: string) => {
    if (resolvedProjectId) {
      void navigate({
        to: "/projects/$projectId/views/$viewType/$itemId",
        params: { projectId: resolvedProjectId, viewType: "items", itemId },
      });
    }
  };

  return (
    <div className="relative h-full">
      {(itemsLoading || linksLoading) && (
        <div className="absolute top-6 right-6 z-20">
          <Badge variant="outline" className="gap-2 text-xs">
            <span className="bg-primary inline-flex h-2 w-2 animate-pulse rounded-full" />
            Loading graph
          </Badge>
        </div>
      )}

      {(itemsQuery.isError || linksQuery.isError) && (
        <div role="alert" className="border border-destructive p-3 text-sm text-destructive">
          Graph data could not be loaded. {String(itemsQuery.error ?? linksQuery.error)}
        </div>
      )}

      {isPriming ? (
        <div className="space-y-4 p-6">
          <Skeleton className="h-10 w-56" />
          <Skeleton className="h-[calc(100vh-220px)] w-full" />
        </div>
      ) : (
        <>
          <div className="flex items-center gap-3 border-b px-4 py-2 text-xs text-muted-foreground">
            <span>
              Showing {visibleItems.length} of {itemsTotal} items and {visibleLinks.length} of{" "}
              {linksTotal} links
            </span>
            {canLoadMore && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={itemsQuery.isFetchingNextPage || linksQuery.isFetchingNextPage}
                onClick={handleLoadMore}
              >
                Load more
              </Button>
            )}
            {unavailableEndpointLinks > 0 && (
              <span>{unavailableEndpointLinks} links reference items not available here</span>
            )}
          </div>
          <UnifiedGraphView
            items={visibleItems}
            links={visibleLinks}
            isLoading={itemsQuery.isLoading || linksQuery.isLoading}
            projectId={resolvedProjectId}
            onNavigateToItem={handleNavigateToItem}
          />
        </>
      )}
    </div>
  );
}
