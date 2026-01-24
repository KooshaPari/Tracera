import { useSearch } from "@tanstack/react-router";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui/components/Select";
import { Separator } from "@tracertm/ui/components/Separator";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import cytoscape, { type Core, type NodeSingular } from "cytoscape";
import {
	Download,
	Filter,
	Maximize2,
	Network,
	RotateCcw,
	ZoomIn,
	ZoomOut,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useItems } from "../hooks/useItems";
import { useLinks } from "../hooks/useLinks";

const typeColors: Record<string, string> = {
	requirement: "#9333ea", // purple
	feature: "#9333ea", // purple
	code: "#3b82f6", // blue
	test: "#22c55e", // green
	api: "#f59e0b", // orange
	database: "#8b5cf6", // violet
	wireframe: "#ec4899", // pink
	infrastructure: "#06b6d4", // cyan
	architecture: "#6366f1", // indigo
	security: "#ef4444", // red
	performance: "#10b981", // emerald
	monitoring: "#14b8a6", // teal
	domain: "#a855f7", // purple
	journey: "#f97316", // orange
	configuration: "#64748b", // slate
	dependency: "#84cc16", // lime
};

const statusOpacity: Record<string, number> = {
	done: 1,
	completed: 1,
	in_progress: 0.8,
	todo: 0.5,
	pending: 0.5,
	blocked: 0.6,
};

const linkTypeColors: Record<string, string> = {
	implements: "#9333ea",
	tests: "#22c55e",
	depends_on: "#f59e0b",
	traces_to: "#3b82f6",
	validates: "#10b981",
	blocks: "#ef4444",
	related_to: "#64748b",
};

export function GraphView() {
	const searchParams = useSearch({ strict: false }) as any;
	const projectFilter = searchParams?.project || undefined;

	const { data: itemsData, isLoading: itemsLoading } = useItems({
		projectId: projectFilter,
	});
	const { data: linksData, isLoading: linksLoading } = useLinks({
		projectId: projectFilter,
	});
	// Extract arrays from new hook structure
	const items = itemsData?.items || [];
	const links = linksData?.links || [];

	const containerRef = useRef<HTMLDivElement>(null);
	const cyRef = useRef<Core | null>(null);
	const [selectedNode, setSelectedNode] = useState<NodeSingular | null>(null);
	const [layout, setLayout] = useState<"cose" | "breadthfirst" | "circle">(
		"cose",
	);
	const [filterType, setFilterType] = useState<string | null>(null);

	const initCytoscape = useCallback(() => {
		if (!containerRef.current || !items || !links) return;

		// Convert items to Cytoscape nodes
		const cytoscapeNodes = items.map((item) => {
			// Use type or view field, with fallback
			const itemType = (item.type || item.view || "item").toLowerCase();
			return {
				data: {
					id: item.id,
					label: item.title || "Untitled",
					type: itemType,
					status: item.status || "pending",
					item: item, // Store full item for details
				},
			};
		});

		// Convert links to Cytoscape edges
		const cytoscapeEdges = links.map((link) => ({
			data: {
				id: link.id,
				source: link.sourceId,
				target: link.targetId,
				type: link.type,
				label: link.type.replace(/_/g, " "),
			},
		}));

		// Filter nodes by type if filter is active
		const filteredNodes = filterType
			? cytoscapeNodes.filter((n) => n.data.type === filterType)
			: cytoscapeNodes;

		const filteredNodeIds = new Set(filteredNodes.map((n) => n.data.id));
		const filteredEdges = cytoscapeEdges.filter(
			(e) =>
				filteredNodeIds.has(e.data.source) &&
				filteredNodeIds.has(e.data.target),
		);

		// Destroy existing instance
		if (cyRef.current) {
			cyRef.current.destroy();
		}

		cyRef.current = cytoscape({
			container: containerRef.current,
			elements: [...filteredNodes, ...filteredEdges],
			style: [
				{
					selector: "node",
					style: {
						"background-color": (ele: any) =>
							typeColors[ele.data("type")] || "#64748b",
						"background-opacity": (ele: any) =>
							statusOpacity[ele.data("status")] || 1,
						label: "data(label)",
						color: "#fff",
						"text-outline-color": (ele: any) =>
							typeColors[ele.data("type")] || "#64748b",
						"text-outline-width": 2,
						"font-size": 12,
						width: 60,
						height: 60,
						"text-valign": "bottom",
						"text-margin-y": 8,
						"text-wrap": "wrap",
						"text-max-width": 80,
					},
				},
				{
					selector: "edge",
					style: {
						width: 2,
						"line-color": (ele: any) =>
							linkTypeColors[ele.data("type")] || "#94a3b8",
						"target-arrow-color": (ele: any) =>
							linkTypeColors[ele.data("type")] || "#94a3b8",
						"target-arrow-shape": "triangle",
						"curve-style": "bezier",
						opacity: 0.7,
						label: "data(label)",
						"font-size": 10,
						"text-rotation": "autorotate",
						"text-margin-y": -10,
					},
				},
				{
					selector: "node:selected",
					style: {
						"border-width": 4,
						"border-color": "#fff",
						"overlay-opacity": 0.2,
					},
				},
				{
					selector: "edge:selected",
					style: {
						width: 4,
						opacity: 1,
					},
				},
			],
			layout: {
				name: layout,
				animate: true,
				animationDuration: 500,
				...(layout === "breadthfirst" && {
					directed: true,
					spacingFactor: 1.5,
				}),
			},
			minZoom: 0.2,
			maxZoom: 3,
		});

		cyRef.current.on("tap", "node", (evt) => setSelectedNode(evt.target));
		cyRef.current.on("tap", (evt) => {
			if (evt.target === cyRef.current) setSelectedNode(null);
		});

		// Fit to viewport
		cyRef.current.fit(undefined, 50);
	}, [items, links, layout, filterType]);

	useEffect(() => {
		initCytoscape();
		return () => {
			cyRef.current?.destroy();
		};
	}, [initCytoscape]);

	const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.2);
	const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() / 1.2);
	const handleFit = () => cyRef.current?.fit(undefined, 50);
	const handleReset = () => {
		setFilterType(null);
		setLayout("cose");
	};

	const handleExport = () => {
		if (!cyRef.current) return;
		const png = cyRef.current.png({ full: true, scale: 2 });
		const link = document.createElement("a");
		link.download = `graph-${new Date().toISOString()}.png`;
		link.href = png;
		link.click();
	};

	if (itemsLoading || linksLoading) {
		return (
			<div className="space-y-6">
				<Skeleton className="h-12 w-full" />
				<Skeleton className="h-[calc(100vh-200px)]" />
			</div>
		);
	}

	if (!items || items.length === 0) {
		return (
			<div className="space-y-6">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Graph View</h1>
					<p className="mt-2 text-muted-foreground">
						Visualize item relationships
					</p>
				</div>
				<Card className="p-12">
					<div className="text-center">
						<Network className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
						<p className="text-muted-foreground">No items to visualize</p>
					</div>
				</Card>
			</div>
		);
	}

	const uniqueTypes = Array.from(
		new Set(
			items.map((item) => item.type || item.view || "item").filter(Boolean),
		),
	);

	return (
		<div className="space-y-6">
			{/* Header */}
			<div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Graph View</h1>
					<p className="mt-2 text-muted-foreground">
						Interactive visualization of item relationships and dependencies
					</p>
				</div>
			</div>

			{/* Controls */}
			<Card className="p-4">
				<div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
					<div className="flex flex-wrap items-center gap-2">
						<Select
							value={layout}
							onValueChange={(v) => setLayout(v as typeof layout)}
						>
							<SelectTrigger className="w-[180px]">
								<SelectValue />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="cose">Force-directed</SelectItem>
								<SelectItem value="circle">Circle</SelectItem>
								<SelectItem value="breadthfirst">Hierarchical</SelectItem>
							</SelectContent>
						</Select>

						<Select
							value={filterType || "all"}
							onValueChange={(v) => setFilterType(v === "all" ? null : v)}
						>
							<SelectTrigger className="w-[180px]">
								<Filter className="mr-2 h-4 w-4" />
								<SelectValue placeholder="All Types" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="all">All Types</SelectItem>
								{uniqueTypes.map((type) => (
									<SelectItem key={type} value={type.toLowerCase()}>
										{type}
									</SelectItem>
								))}
							</SelectContent>
						</Select>
					</div>

					<div className="flex items-center gap-2">
						<div className="flex items-center gap-1 rounded-md border p-1">
							<Button
								variant="ghost"
								size="sm"
								onClick={handleZoomIn}
								className="h-8 w-8 p-0"
							>
								<ZoomIn className="h-4 w-4" />
							</Button>
							<Button
								variant="ghost"
								size="sm"
								onClick={handleZoomOut}
								className="h-8 w-8 p-0"
							>
								<ZoomOut className="h-4 w-4" />
							</Button>
							<Button
								variant="ghost"
								size="sm"
								onClick={handleFit}
								className="h-8 w-8 p-0"
							>
								<Maximize2 className="h-4 w-4" />
							</Button>
							<Button
								variant="ghost"
								size="sm"
								onClick={handleReset}
								className="h-8 w-8 p-0"
							>
								<RotateCcw className="h-4 w-4" />
							</Button>
						</div>
						<Button variant="outline" onClick={handleExport}>
							<Download className="mr-2 h-4 w-4" />
							Export
						</Button>
					</div>
				</div>
			</Card>

			{/* Graph Container */}
			<div className="flex gap-4">
				<Card className="p-0 flex-1 h-[calc(100vh-300px)] overflow-hidden">
					<div ref={containerRef} className="w-full h-full bg-background" />
				</Card>

				{/* Node Details Panel */}
				{selectedNode && (
					<Card className="w-80 p-4">
						<div className="space-y-4">
							<div>
								<h3 className="font-semibold text-lg">
									{selectedNode.data("label")}
								</h3>
								<div className="mt-2 flex flex-wrap gap-2">
									<Badge
										variant="outline"
										className="text-xs"
										style={{
											backgroundColor: `${typeColors[selectedNode.data("type")]}20`,
											color: typeColors[selectedNode.data("type")],
											borderColor: typeColors[selectedNode.data("type")],
										}}
									>
										{selectedNode.data("type")}
									</Badge>
									<Badge variant="secondary" className="text-xs">
										{selectedNode.data("status")}
									</Badge>
								</div>
							</div>

							<Separator />

							<div className="space-y-3 text-sm">
								<div className="flex justify-between">
									<span className="text-muted-foreground">Connections</span>
									<span className="font-medium">
										{selectedNode.connectedEdges().length}
									</span>
								</div>
								<div className="flex justify-between">
									<span className="text-muted-foreground">Neighbors</span>
									<span className="font-medium">
										{selectedNode.neighborhood("node").length}
									</span>
								</div>
							</div>

							{selectedNode.neighborhood("node").length > 0 && (
								<>
									<Separator />
									<div>
										<p className="text-xs font-medium text-muted-foreground mb-2">
											Connected to:
										</p>
										<ul className="space-y-1.5">
											{selectedNode
												.neighborhood("node")
												.map((n: NodeSingular) => (
													<li
														key={n.id()}
														className="flex items-center gap-2 text-sm"
													>
														<span
															className="h-2 w-2 rounded-full"
															style={{
																backgroundColor: typeColors[n.data("type")],
															}}
														/>
														<span className="truncate">{n.data("label")}</span>
													</li>
												))}
										</ul>
									</div>
								</>
							)}
						</div>
					</Card>
				)}
			</div>

			{/* Legend */}
			<Card className="p-4">
				<div className="flex flex-wrap items-center gap-6 text-sm">
					<div className="flex items-center gap-2">
						<span className="text-xs font-medium text-muted-foreground">
							Types:
						</span>
					</div>
					{uniqueTypes.slice(0, 8).map((type) => (
						<div key={type} className="flex items-center gap-2">
							<span
								className="h-3 w-3 rounded-full"
								style={{ backgroundColor: typeColors[type.toLowerCase()] }}
							/>
							<span>{type}</span>
						</div>
					))}
					{uniqueTypes.length > 8 && (
						<span className="text-muted-foreground">
							+{uniqueTypes.length - 8} more
						</span>
					)}
					<Separator orientation="vertical" className="h-4" />
					<div className="flex items-center gap-2">
						<span className="text-xs font-medium text-muted-foreground">
							Links:
						</span>
					</div>
					{Object.entries(linkTypeColors)
						.slice(0, 4)
						.map(([type, color]) => (
							<div key={type} className="flex items-center gap-2">
								<div className="h-0.5 w-6" style={{ backgroundColor: color }} />
								<span className="text-xs">{type.replace(/_/g, " ")}</span>
							</div>
						))}
				</div>
			</Card>
		</div>
	);
}
