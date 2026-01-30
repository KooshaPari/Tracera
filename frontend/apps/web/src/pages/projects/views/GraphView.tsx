// Project-specific Graph View - Unified view with sidebar navigation
// Provides separated views: traceability, page flow, component library, and perspectives

import { useNavigate, useParams } from "@tanstack/react-router";
import { useInfiniteQuery } from "@tanstack/react-query";
import { UnifiedGraphView } from "../../../components/graph";
import { useEffect, useState } from "react";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import { Badge } from "@tracertm/ui/components/Badge";

export function GraphView() {
	const { projectId } = useParams({ strict: false }) as { projectId?: string };
	const navigate = useNavigate();

	const pageSizeItems = 500;
	const pageSizeLinks = 2000;

	// ✅ NEW: Progressive edge loading state
	const MAX_EDGES_INITIAL = 500;
	const [visibleEdgeCount, setVisibleEdgeCount] = useState(MAX_EDGES_INITIAL);

	const itemsQuery = useInfiniteQuery<{ items?: unknown[]; total?: number }>({
		queryKey: ["graph-items", projectId],
		queryFn: async ({ pageParam }) => {
			const res = await fetch(
				`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/v1/items?project_id=${projectId}&limit=${pageSizeItems}&skip=${pageParam}`,
				{ headers: { "X-Bulk-Operation": "true" } },
			);
			if (!res.ok) throw new Error("Failed to fetch items");
			return res.json();
		},
		initialPageParam: 0,
		getNextPageParam: (lastPage, allPages) => {
			const loaded = allPages.reduce(
				(sum: number, p) => sum + (p.items?.length || 0),
				0,
			);
			const total = lastPage.total || 0;
			return loaded < total ? loaded : undefined;
		},
		enabled: Boolean(projectId),
	});

	const linksQuery = useInfiniteQuery<{ links?: unknown[]; total?: number }>({
		queryKey: ["graph-links", projectId],
		queryFn: async ({ pageParam }) => {
			const res = await fetch(
				`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/v1/links?project_id=${projectId}&exclude_types=implements&limit=${pageSizeLinks}&skip=${pageParam}`,
				{ headers: { "X-Bulk-Operation": "true" } },
			);
			if (!res.ok) throw new Error("Failed to fetch links");
			return res.json();
		},
		initialPageParam: 0,
		getNextPageParam: (lastPage, allPages) => {
			const loaded = allPages.reduce(
				(sum: number, p) => sum + (p.links?.length || 0),
				0,
			);
			const total = lastPage.total || 0;
			return loaded < total ? loaded : undefined;
		},
		enabled: Boolean(projectId),
	});

	useEffect(() => {
		if (itemsQuery.hasNextPage && !itemsQuery.isFetchingNextPage) {
			itemsQuery.fetchNextPage();
		}
	}, [itemsQuery.hasNextPage, itemsQuery.isFetchingNextPage]);

	useEffect(() => {
		if (linksQuery.hasNextPage && !linksQuery.isFetchingNextPage) {
			linksQuery.fetchNextPage();
		}
	}, [linksQuery.hasNextPage, linksQuery.isFetchingNextPage]);

	const items = itemsQuery.data?.pages.flatMap((p: any) => p.items || []) || [];
	const links = linksQuery.data?.pages.flatMap((p: any) => p.links || []) || [];
	const itemsTotal =
		itemsQuery.data?.pages?.[itemsQuery.data.pages.length - 1]?.total ?? 0;
	const linksTotal =
		linksQuery.data?.pages?.[linksQuery.data.pages.length - 1]?.total ?? 0;
	const itemsLoading = itemsQuery.isLoading || itemsQuery.isFetching;
	const linksLoading = linksQuery.isLoading || linksQuery.isFetching;
	const isPriming = (itemsLoading || linksLoading) && items.length === 0;

	// ✅ NEW: Progressive edge loading
	const visibleLinks = links.slice(0, visibleEdgeCount);
	const canLoadMore = visibleEdgeCount < links.length;
	const handleLoadMoreEdges = () => {
		setVisibleEdgeCount((prev) => Math.min(prev + 500, links.length));
	};

	const handleNavigateToItem = (itemId: string) => {
		navigate({ to: "/items/$itemId", params: { itemId } });
	};

	return (
		<div className="relative h-full">
			{(itemsLoading || linksLoading) && (
				<div className="absolute right-6 top-6 z-20">
					<Badge variant="outline" className="gap-2 text-xs">
						<span className="inline-flex h-2 w-2 animate-pulse rounded-full bg-primary" />
						Loading graph
						<span className="text-muted-foreground">
							{items.length}/{itemsTotal || "?"} items · {links.length}/
							{linksTotal || "?"} links
						</span>
					</Badge>
				</div>
			)}

			{isPriming ? (
				<div className="p-6 space-y-4">
					<Skeleton className="h-10 w-56" />
					<Skeleton className="h-[calc(100vh-220px)] w-full" />
				</div>
			) : (
				<UnifiedGraphView
					items={items}
					links={visibleLinks}
					isLoading={itemsLoading || linksLoading}
					projectId={projectId}
					onNavigateToItem={handleNavigateToItem}
					canLoadMore={canLoadMore}
					visibleEdges={visibleLinks.length}
					totalEdges={links.length}
					onLoadMore={handleLoadMoreEdges}
				/>
			)}
		</div>
	);
}
