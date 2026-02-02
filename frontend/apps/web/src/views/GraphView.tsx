import { useNavigate } from "@tanstack/react-router";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui/components/Select";
import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";
import { UnifiedGraphView } from "../components/graph";
import { useGraphProjection, useGraphs } from "../hooks/useGraphs";

interface GraphViewProps {
	projectId: string;
}

export function GraphView({ projectId }: GraphViewProps) {
	const navigate = useNavigate();

	// ✅ NEW: Progressive edge loading state
	const MAX_EDGES_INITIAL = 500;
	const [visibleEdgeCount, setVisibleEdgeCount] = useState(MAX_EDGES_INITIAL);

	const { data: graphsData } = useGraphs(projectId);
	const [selectedGraphId, setSelectedGraphId] = useState<string | undefined>(
		);
	const [overlayMapping, setOverlayMapping] = useState(false);

	const selectedGraph = useMemo(() => {
		if (!graphsData?.length) {return;}
		if (selectedGraphId)
			{return graphsData.find((g) => g.id === selectedGraphId);}
		return graphsData[0];
	}, [graphsData, selectedGraphId]);

	const { data: graphData, isLoading: graphLoading } = useGraphProjection(
		projectId,
		selectedGraph?.id,
	);

	const mappingGraph = useMemo(
		() => graphsData?.find((g) => g.graphType === "mapping"),
		[graphsData],
	);

	const { data: mappingData } = useGraphProjection(
		projectId,
		overlayMapping ? mappingGraph?.id : undefined,
	);

	const items = useMemo(() => {
		const nodes = graphData?.nodes || [];
		return nodes.map((node: any) => (Object.assign(node, {id:node.id,title:node.title,view:node.view,type:node.item_type||node.itemType||node.view})));
	}, [graphData]);

	const links = useMemo(() => {
		const baseLinks = (graphData?.links || []).map((link: any) => (Object.assign(link, {sourceId:link.source_item_id||link.sourceId,targetId:link.target_item_id||link.targetId,type:link.link_type||link.type})));

		if (!overlayMapping || !mappingData?.links) {
			return baseLinks;
		}

		const itemIds = new Set(items.map((item: any) => item.id));
		const overlayLinks = mappingData.links
			.map((link: any) => ({
				...link,
				sourceId: link.source_item_id || link.sourceId,
				targetId: link.target_item_id || link.targetId,
				type: link.link_type || link.type,
			}))
			.filter(
				(link: any) => itemIds.has(link.sourceId) && itemIds.has(link.targetId),
			);

		return [...baseLinks, ...overlayLinks];
	}, [graphData, mappingData, overlayMapping, items]);

	// ✅ NEW: Progressive edge loading
	const visibleLinks = links.slice(0, visibleEdgeCount);
	const canLoadMore = visibleEdgeCount < links.length;
	const handleLoadMoreEdges = () => {
		setVisibleEdgeCount((prev) => Math.min(prev + 500, links.length));
	};

	const handleNavigateToItem = (itemId: string) => {
		const item = items.find((node: any) => node.id === itemId);
		const viewType = String(item?.view || "feature").toLowerCase();
		undefined;
	};

	return (
		<div className="space-y-4 animate-in-fade-up">
			<div className="flex flex-wrap items-center gap-4">
				<div className="min-w-[220px]">
					<Select
						value={selectedGraph?.id || ""}
						onValueChange={(value) => setSelectedGraphId(value)}
					>
						<SelectTrigger>
							<SelectValue placeholder="Select graph" />
						</SelectTrigger>
						<SelectContent>
							{graphsData?.map((graph) => (
								<SelectItem key={graph.id} value={graph.id}>
									{graph.name} ({graph.graphType})
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				</div>
				<div className="flex items-center gap-2">
					<button
						type="button"
						role="switch"
						aria-checked={overlayMapping}
						onClick={() => setOverlayMapping(!overlayMapping)}
						className={cn(
							"relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50",
							overlayMapping ? "bg-primary" : "bg-muted",
						)}
					>
						<span
							className={cn(
								"inline-block h-4 w-4 transform rounded-full bg-background transition-transform",
								overlayMapping ? "translate-x-6" : "translate-x-1",
							)}
						/>
					</button>
					<span className="text-sm text-muted-foreground">
						Overlay mapping links
					</span>
				</div>
			</div>

			<UnifiedGraphView
				items={items}
				links={visibleLinks}
				isLoading={graphLoading}
				projectId={projectId}
				onNavigateToItem={handleNavigateToItem}
				canLoadMore={canLoadMore}
				visibleEdges={visibleLinks.length}
				totalEdges={links.length}
				onLoadMore={handleLoadMoreEdges}
			/>
		</div>
	);
}
