// Enhanced Graph View - Multi-perspective traceability visualization
// Features: Multiple views, rich node pills, Storybook-like UI view
/* eslint-disable max-lines-per-function, no-magic-numbers, react-perf/jsx-no-new-object-as-prop */

import type { Item, Link, LinkType } from "@tracertm/types";
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
import cytoscape from "cytoscape";
import type { Core } from "cytoscape";
import {
	Download,
	Layers,
	LayoutGrid,
	Maximize2,
	Network,
	PanelRight,
	PanelRightClose,
	RotateCcw,
	ZoomIn,
	ZoomOut,
} from "lucide-react";
import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { NodeDetailPanel } from "./NodeDetailPanel";
import { PerspectiveSelector } from "./PerspectiveSelector";
import type { EnhancedNodeData, GraphPerspective } from "./types";
import {
	ENHANCED_TYPE_COLORS,
	LINK_STYLES,
	PERSPECTIVE_CONFIGS,
	STATUS_OPACITY,
	TYPE_TO_PERSPECTIVE,
} from "./types";
import { UIComponentTree } from "./UIComponentTree";

interface EnhancedGraphViewProps {
	items: Item[];
	links: Link[];
	isLoading?: boolean;
	projectId?: string;
	onNavigateToItem?: (itemId: string) => void;
}

function EnhancedGraphViewComponent({
	items,
	links,
	isLoading = false,
	onNavigateToItem,
}: EnhancedGraphViewProps) {
	// State
	const [perspective, setPerspective] = useState<GraphPerspective>("all");
	const [layout, setLayout] = useState<
		"cose" | "breadthfirst" | "circle" | "elk"
	>("cose");
	const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
	const [showDetailPanel, setShowDetailPanel] = useState(true);
	const [showUITree, setShowUITree] = useState(false);

	// Refs
	const containerRef = useRef<HTMLDivElement>(null);
	const cyRef = useRef<Core | null>(null);

	// Build enhanced node data with perspective info
	const enhancedNodes = useMemo((): EnhancedNodeData[] => {
		const itemMap = new Map(items.map((item) => [item.id, item]));

		// Count connections for each item
		const incomingCount = new Map<string, number>();
		const outgoingCount = new Map<string, number>();
		const connectionsByType = new Map<string, Record<LinkType, number>>();

		for (const link of links) {
			// Incoming
			incomingCount.set(
				link.targetId,
				(incomingCount.get(link.targetId) || 0) + 1,
			);
			// Outgoing
			outgoingCount.set(
				link.sourceId,
				(outgoingCount.get(link.sourceId) || 0) + 1,
			);

			// By type
			if (!connectionsByType.has(link.targetId)) {
				connectionsByType.set(link.targetId, {} as Record<LinkType, number>);
			}
			const targetTypes = connectionsByType.get(link.targetId)!;
			targetTypes[link.type] = (targetTypes[link.type] || 0) + 1;

			if (!connectionsByType.has(link.sourceId)) {
				connectionsByType.set(link.sourceId, {} as Record<LinkType, number>);
			}
			const sourceTypes = connectionsByType.get(link.sourceId)!;
			sourceTypes[link.type] = (sourceTypes[link.type] || 0) + 1;
		}

		return items.map((item) => {
			const itemType = (item.type || item.view || "item").toLowerCase();
			const perspectives = TYPE_TO_PERSPECTIVE[itemType] || ["all"];
			const incoming = incomingCount.get(item.id) || 0;
			const outgoing = outgoingCount.get(item.id) || 0;

			// Check if has children
			const hasChildren = items.some((i) => i.parentId === item.id);

			// Calculate depth (simplified - based on parent chain)
			let depth = 0;
			let currentId = item.parentId;
			while (currentId && depth < 10) {
				depth += 1;
				const parent = itemMap.get(currentId);
				currentId = parent?.parentId;
			}

			return {
				connections: {
					byType:
						connectionsByType.get(item.id) || ({} as Record<LinkType, number>),
					incoming,
					outgoing,
					total: incoming + outgoing,
				},
				depth,
				hasChildren,
				id: item.id,
				item,
				label: item.title || "Untitled",
				parentId: item.parentId,
				perspective: perspectives,
				status: item.status,
				type: itemType,
				uiPreview: item.metadata?.["screenshotUrl"]
					? {
							componentCode: item.metadata["code"] as string | undefined,
							interactiveWidgetUrl: item.metadata["interactiveUrl"] as
								| string
								| undefined,
							screenshotUrl: item.metadata["screenshotUrl"] as string,
						}
					: undefined,
			} as EnhancedNodeData;
		});
	}, [items, links]);

	// Filter nodes by perspective
	const filteredNodes = useMemo(() => {
		if (perspective === "all") {
			return enhancedNodes;
		}

		const config = PERSPECTIVE_CONFIGS.find((c) => c.id === perspective);
		if (!config || config.includeTypes.length === 0) {
			return enhancedNodes;
		}

		return enhancedNodes.filter((node) => {
			const nodeType = node.type.toLowerCase();
			// Check if type is in includeTypes or if node has this perspective
			return (
				config.includeTypes.some(
					(t) => nodeType.includes(t) || t.includes(nodeType),
				) || node.perspective.includes(perspective)
			);
		});
	}, [enhancedNodes, perspective]);

	// Filter links to only include those between filtered nodes
	const filteredLinks = useMemo(() => {
		const nodeIds = new Set(filteredNodes.map((n) => n.id));
		return links.filter(
			(link) => nodeIds.has(link.sourceId) && nodeIds.has(link.targetId),
		);
	}, [links, filteredNodes]);

	// Count items by perspective for the selector
	const perspectiveCounts = useMemo(() => {
		const counts: Record<GraphPerspective, number> = {
			all: enhancedNodes.length,
			business: 0,
			performance: 0,
			product: 0,
			security: 0,
			technical: 0,
			ui: 0,
		};

		for (const node of enhancedNodes) {
			for (const p of node.perspective) {
				if (p !== "all") {
					counts[p] = (counts[p] || 0) + 1;
				}
			}
		}

		return counts;
	}, [enhancedNodes]);

	// Selected node data
	const selectedNode = useMemo(() => {
		if (!selectedNodeId) {
			return null;
		}
		return filteredNodes.find((n) => n.id === selectedNodeId) || null;
	}, [filteredNodes, selectedNodeId]);

	// Links for selected node
	const { incomingLinks, outgoingLinks, relatedItems } = useMemo(() => {
		if (!selectedNodeId) {
			return { incomingLinks: [], outgoingLinks: [], relatedItems: [] };
		}

		const incoming = links.filter((l) => l.targetId === selectedNodeId);
		const outgoing = links.filter((l) => l.sourceId === selectedNodeId);

		const relatedIds = new Set([
			...incoming.map((l) => l.sourceId),
			...outgoing.map((l) => l.targetId),
		]);

		return {
			incomingLinks: incoming,
			outgoingLinks: outgoing,
			relatedItems: items.filter((i) => relatedIds.has(i.id)),
		};
	}, [selectedNodeId, links, items]);

	// Initialize Cytoscape
	const initCytoscape = useCallback(() => {
		if (!containerRef.current || filteredNodes.length === 0) {
			return;
		}

		// Destroy existing instance
		if (cyRef.current) {
			cyRef.current.destroy();
		}

		// Convert to Cytoscape format
		const cytoscapeNodes = filteredNodes.map((node) => ({
			data: {
				connectionCount: node.connections.total,
				id: node.id,
				label: node.label,
				status: node.status,
				type: node.type,
			},
		}));

		const cytoscapeEdges = filteredLinks.map((link) => ({
			data: {
				id: link.id,
				label: link.type.replace(/_/g, " "),
				source: link.sourceId,
				target: link.targetId,
				type: link.type,
			},
		}));

		// Get perspective color for active perspective
		const perspectiveConfig = PERSPECTIVE_CONFIGS.find(
			(c) => c.id === perspective,
		);

		cyRef.current = cytoscape({
			container: containerRef.current,
			elements: [...cytoscapeNodes, ...cytoscapeEdges],
			layout: {
				name: layout === "elk" ? "breadthfirst" : layout,
				animate: true,
				animationDuration: 500,
				...(layout === "breadthfirst" || layout === "elk"
					? {
							directed: true,
							padding: 50,
							spacingFactor: 1.5,
						}
					: {}),
				...(layout === "cose"
					? {
							edgeElasticity: () => 100,
							gravity: 0.25,
							idealEdgeLength: () => 100,
							nodeRepulsion: () => 8000,
						}
					: {}),
			},
			maxZoom: 4,
			minZoom: 0.1,
			style: [
				{
					selector: "node",
					style: {
						// Block pill shape (rounded rectangle)
						shape: "round-rectangle",
						width: (ele: cytoscape.NodeSingular) => {
							const label = ele.data("label") || "";
							return Math.max(100, Math.min(180, label.length * 6 + 40));
						},
						height: 50,
						"background-color": (ele: cytoscape.NodeSingular) =>
							ENHANCED_TYPE_COLORS[ele.data("type")] || "#64748b",
						"background-opacity": (ele: cytoscape.NodeSingular) =>
							STATUS_OPACITY[ele.data("status")] || 1,
						// Label styling
						label: "data(label)",
						color: "#fff",
						"text-outline-color": (ele: cytoscape.NodeSingular) =>
							ENHANCED_TYPE_COLORS[ele.data("type")] || "#64748b",
						"text-outline-width": 2,
						"font-size": 11,
						"font-weight": "bold",
						"text-valign": "center",
						"text-halign": "center",
						"text-wrap": "ellipsis",
						"text-max-width": "140px",
						// Border for visual depth
						"border-width": 2,
						"border-color": (ele: cytoscape.NodeSingular) => {
							const color = ENHANCED_TYPE_COLORS[ele.data("type")] || "#64748b";
							return color;
						},
						"border-opacity": 0.3,
					},
				},
				{
					selector: "edge",
					style: {
						width: 2,
						"line-color": (ele: cytoscape.EdgeSingular) =>
							LINK_STYLES[ele.data("type")]?.color || "#94a3b8",
						"target-arrow-color": (ele: cytoscape.EdgeSingular) =>
							LINK_STYLES[ele.data("type")]?.color || "#94a3b8",
						"target-arrow-shape": (ele: cytoscape.EdgeSingular) =>
							LINK_STYLES[ele.data("type")]?.arrow ? "triangle" : "none",
						"line-style": (ele: cytoscape.EdgeSingular) =>
							LINK_STYLES[ele.data("type")]?.dashed ? "dashed" : "solid",
						"curve-style": "bezier",
						opacity: 0.6,
						// Edge labels
						label: "data(label)",
						"font-size": 9,
						"text-rotation": "autorotate",
						"text-margin-y": -10,
						color: "#94a3b8",
						"text-background-color": "#1a1a2e",
						"text-background-opacity": 0.8,
						"text-background-padding": "2px",
					},
				},
				{
					selector: "node:selected",
					style: {
						"border-color": "#fff",
						"border-opacity": 1,
						"border-width": 4,
						"overlay-color": "#fff",
						"overlay-opacity": 0.1,
					},
				},
				{
					selector: "edge:selected",
					style: {
						opacity: 1,
						width: 4,
					},
				},
				{
					selector: "node.highlighted",
					style: {
						"border-color": perspectiveConfig?.color || "#fff",
						"border-opacity": 1,
						"border-width": 3,
					},
				},
				{
					selector: "edge.highlighted",
					style: {
						opacity: 1,
						width: 3,
					},
				},
				{
					selector: "node.faded",
					style: {
						opacity: 0.3,
					},
				},
				{
					selector: "edge.faded",
					style: {
						opacity: 0.15,
					},
				},
			],
			wheelSensitivity: 0.3,
		});

		// Event handlers
		cyRef.current.on("tap", "node", (evt) => {
			const nodeId = evt.target.id();
			setSelectedNodeId(nodeId);
			setShowDetailPanel(true);

			// Highlight connected nodes and edges
			const node = evt.target;
			const neighborhood = node.closedNeighborhood();

			cyRef.current!.elements().addClass("faded");
			neighborhood.removeClass("faded");
			neighborhood.addClass("highlighted");
		});

		cyRef.current.on("tap", (evt) => {
			if (evt.target === cyRef.current) {
				setSelectedNodeId(null);
				cyRef.current!.elements().removeClass("faded highlighted");
			}
		});

		// Fit to viewport
		cyRef.current.fit(undefined, 50);
	}, [filteredNodes, filteredLinks, layout, perspective]);

	// Effect to initialize/reinitialize cytoscape
	useEffect(() => {
		initCytoscape();
		return () => {
			cyRef.current?.destroy();
		};
	}, [initCytoscape]);

	// Handle layout change
	const handleLayoutChange = (newLayout: typeof layout) => {
		setLayout(newLayout);
	};

	// Handle perspective change
	const handlePerspectiveChange = (newPerspective: GraphPerspective) => {
		setPerspective(newPerspective);
		setSelectedNodeId(null);

		// Auto-show UI tree for UI perspective
		setShowUITree(newPerspective === "ui");

		// Update layout preference
		const config = PERSPECTIVE_CONFIGS.find((c) => c.id === newPerspective);
		if (config?.layoutPreference) {
			setLayout(config.layoutPreference);
		}
	};

	// Zoom controls
	const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.3);
	const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() / 1.3);
	const handleFit = () => {
		cyRef.current?.fit(undefined, 50);
		cyRef.current?.elements().removeClass("faded highlighted");
	};
	const handleReset = () => {
		setPerspective("all");
		setLayout("cose");
		setSelectedNodeId(null);
		setShowUITree(false);
		cyRef.current?.elements().removeClass("faded highlighted");
	};

	// Export
	const handleExport = () => {
		if (!cyRef.current) {
			return;
		}
		const png = cyRef.current.png({ bg: "#1a1a2e", full: true, scale: 2 });
		const link = document.createElement("a");
		link.download = `graph-${perspective}-${new Date().toISOString()}.png`;
		link.href = png;
		link.click();
	};

	// Focus on specific node
	const handleFocusNode = (nodeId: string) => {
		const node = cyRef.current?.getElementById(nodeId);
		if (node && node.length > 0) {
			setSelectedNodeId(nodeId);

			// Center on node
			cyRef.current?.animate({
				center: { eles: node },
				duration: 300,
				zoom: 1.5,
			});

			// Highlight
			cyRef.current!.elements().addClass("faded");
			const neighborhood = node.closedNeighborhood();
			neighborhood.removeClass("faded");
			neighborhood.addClass("highlighted");
		}
	};

	// Loading state
	if (isLoading) {
		return (
			<div className="space-y-6">
				<Skeleton className="h-12 w-full" />
				<Skeleton className="h-14 w-full" />
				<Skeleton className="h-[calc(100vh-300px)]" />
			</div>
		);
	}

	// Empty state
	if (items.length === 0) {
		return (
			<div className="space-y-6">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">
						Traceability Graph
					</h1>
					<p className="mt-2 text-muted-foreground">
						Multi-perspective visualization of item relationships
					</p>
				</div>
				<Card className="p-12">
					<div className="text-center">
						<Network className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
						<p className="text-muted-foreground">No items to visualize</p>
						<p className="text-sm text-muted-foreground mt-1">
							Create items and links to see the traceability graph
						</p>
					</div>
				</Card>
			</div>
		);
	}

	return (
		<div className="space-y-4">
			{/* Header */}
			<div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
						<Network className="h-8 w-8" />
						Traceability Graph
					</h1>
					<p className="mt-1 text-muted-foreground">
						{filteredNodes.length} items \u00b7 {filteredLinks.length}{" "}
						connections
					</p>
				</div>

				{/* Quick stats */}
				<div className="flex items-center gap-3">
					{perspective !== "all" && (
						<Badge
							variant="outline"
							className="px-3 py-1"
							style={{
								backgroundColor: `${PERSPECTIVE_CONFIGS.find((c) => c.id === perspective)?.color}20`,
								borderColor: PERSPECTIVE_CONFIGS.find(
									(c) => c.id === perspective,
								)?.color,
							}}
						>
							{PERSPECTIVE_CONFIGS.find((c) => c.id === perspective)?.label}
						</Badge>
					)}
				</div>
			</div>

			{/* Perspective Selector */}
			<PerspectiveSelector
				currentPerspective={perspective}
				onPerspectiveChange={handlePerspectiveChange}
				itemCounts={perspectiveCounts}
			/>

			{/* Controls */}
			<Card className="p-3">
				<div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
					<div className="flex flex-wrap items-center gap-2">
						{/* Layout selector */}
						<Select
							value={layout}
							onValueChange={(v) => handleLayoutChange(v as typeof layout)}
						>
							<SelectTrigger className="w-[160px] h-9">
								<Layers className="h-4 w-4 mr-2" />
								<SelectValue />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="cose">Force-directed</SelectItem>
								<SelectItem value="breadthfirst">Hierarchical</SelectItem>
								<SelectItem value="circle">Circular</SelectItem>
								<SelectItem value="elk">Directed Graph</SelectItem>
							</SelectContent>
						</Select>

						<Separator orientation="vertical" className="h-6" />

						{/* UI Tree toggle (for UI perspective) */}
						<Button
							variant={showUITree ? "default" : "outline"}
							size="sm"
							onClick={() => setShowUITree(!showUITree)}
							className="h-9"
						>
							<LayoutGrid className="h-4 w-4 mr-2" />
							UI Library
						</Button>

						{/* Detail panel toggle */}
						<Button
							variant="ghost"
							size="sm"
							onClick={() => setShowDetailPanel(!showDetailPanel)}
							className="h-9"
						>
							{showDetailPanel ? (
								<PanelRightClose className="h-4 w-4" />
							) : (
								<PanelRight className="h-4 w-4" />
							)}
						</Button>
					</div>

					<div className="flex items-center gap-2">
						{/* Zoom controls */}
						<div className="flex items-center gap-1 rounded-md border p-1">
							<Button
								variant="ghost"
								size="sm"
								onClick={handleZoomIn}
								className="h-7 w-7 p-0"
							>
								<ZoomIn className="h-4 w-4" />
							</Button>
							<Button
								variant="ghost"
								size="sm"
								onClick={handleZoomOut}
								className="h-7 w-7 p-0"
							>
								<ZoomOut className="h-4 w-4" />
							</Button>
							<Button
								variant="ghost"
								size="sm"
								onClick={handleFit}
								className="h-7 w-7 p-0"
							>
								<Maximize2 className="h-4 w-4" />
							</Button>
							<Button
								variant="ghost"
								size="sm"
								onClick={handleReset}
								className="h-7 w-7 p-0"
							>
								<RotateCcw className="h-4 w-4" />
							</Button>
						</div>

						<Button
							variant="outline"
							size="sm"
							onClick={handleExport}
							className="h-9"
						>
							<Download className="h-4 w-4 mr-2" />
							Export
						</Button>
					</div>
				</div>
			</Card>

			{/* Main content area */}
			<div className="flex gap-4" style={{ height: "calc(100vh - 340px)" }}>
				{/* UI Component Tree (left panel) */}
				{showUITree && (
					<div className="w-80 shrink-0">
						<UIComponentTree
							items={items}
							links={links}
							onSelectItem={handleFocusNode}
							selectedItemId={selectedNodeId}
						/>
					</div>
				)}

				{/* Graph Container (center) */}
				<Card className="flex-1 p-0 overflow-hidden">
					<div ref={containerRef} className="w-full h-full bg-background" />
				</Card>

				{/* Node Detail Panel (right) */}
				{showDetailPanel && selectedNode && (
					<NodeDetailPanel
						node={selectedNode}
						relatedItems={relatedItems}
						incomingLinks={incomingLinks}
						outgoingLinks={outgoingLinks}
						onClose={() => {
							setSelectedNodeId(null);
							cyRef.current?.elements().removeClass("faded highlighted");
						}}
						onNavigateToItem={onNavigateToItem || (() => {})}
						onFocusNode={handleFocusNode}
					/>
				)}
			</div>

			{/* Legend */}
			<Card className="p-3">
				<div className="flex flex-wrap items-center gap-4 text-xs">
					<span className="text-muted-foreground font-medium">Types:</span>
					{Object.entries(ENHANCED_TYPE_COLORS)
						.filter(([type]) => filteredNodes.some((n) => n.type === type))
						.slice(0, 10)
						.map(([type, color]) => (
							<div key={type} className="flex items-center gap-1.5">
								<div
									className="h-3 w-6 rounded"
									style={{ backgroundColor: color }}
								/>
								<span className="capitalize">{type.replaceAll(/_/g, " ")}</span>
							</div>
						))}

					<Separator orientation="vertical" className="h-4" />

					<span className="text-muted-foreground font-medium">Links:</span>
					{Object.entries(LINK_STYLES)
						.slice(0, 5)
						.map(([type, style]) => (
							<div key={type} className="flex items-center gap-1.5">
								<div
									className="h-0.5 w-6"
									style={{
										backgroundColor: style.color,
										borderStyle: style.dashed ? "dashed" : "solid",
									}}
								/>
								<span>{type.replaceAll(/_/g, " ")}</span>
							</div>
						))}
				</div>
			</Card>
		</div>
	);
}

export const EnhancedGraphView = memo(EnhancedGraphViewComponent);
