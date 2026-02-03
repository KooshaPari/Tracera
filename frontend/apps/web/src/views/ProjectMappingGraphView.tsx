import { useNavigate, useParams } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { UnifiedGraphView } from "../components/graph";
import { useGraphProjection, useGraphs } from "../hooks/useGraphs";

export function ProjectMappingGraphView() {
	const { projectId } = useParams({ strict: false }) as { projectId?: string };
	const navigate = useNavigate();

	// ✅ NEW: Progressive edge loading state
	const MAX_EDGES_INITIAL = 500;
	const [visibleEdgeCount, setVisibleEdgeCount] = useState(MAX_EDGES_INITIAL);

	const { data: graphsData } = useGraphs(projectId);
	const mappingGraph = useMemo(
		() => graphsData?.find((g) => g.graphType === "mapping") || graphsData?.[0],
		[graphsData],
	);

	const { data: graphData, isLoading } = useGraphProjection(
		projectId,
		mappingGraph?.id,
	);

	const items = useMemo(() => {
		const nodes = graphData?.nodes || [];
		return nodes.map((node: any) =>
			Object.assign(node, {
				id: node.id,
				title: node.title,
				type: node.item_type || node.itemType || node.view,
				view: node.view,
			}),
		);
	}, [graphData]);

	const links = useMemo(
		() =>
			(graphData?.links || []).map((link: any) =>
				Object.assign(link, {
					sourceId: link.source_item_id || link.sourceId,
					targetId: link.target_item_id || link.targetId,
					type: link.link_type || link.type,
				}),
			),
		[graphData],
	);

	// ✅ NEW: Progressive edge loading
	const visibleLinks = links.slice(0, visibleEdgeCount);
	const canLoadMore = visibleEdgeCount < links.length;
	const handleLoadMoreEdges = () => {
		setVisibleEdgeCount((prev) => Math.min(prev + 500, links.length));
	};

	const handleNavigateToItem = (itemId: string) => {};

	return (
		<UnifiedGraphView
			items={items}
			links={visibleLinks}
			isLoading={isLoading}
			projectId={projectId ?? ""}
			onNavigateToItem={handleNavigateToItem}
			defaultView="components"
			canLoadMore={canLoadMore}
			visibleEdges={visibleLinks.length}
			totalEdges={links.length}
			onLoadMore={handleLoadMoreEdges}
		/>
	);
}
