import type { Item, Link, LinkType } from "@tracertm/types";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { Separator } from "@tracertm/ui/components/Separator";
import {
	Background,
	BackgroundVariant,
	Controls,
	type Edge,
	MarkerType,
	type Node,
	type NodeTypes,
	Panel,
	ReactFlow,
	useEdgesState,
	useNodesState,
	useReactFlow,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
	Activity,
	Maximize2,
	PanelRight,
	PanelRightClose,
	RotateCcw,
	ZoomIn,
	ZoomOut,
} from "lucide-react";
import { memo, useCallback, useEffect, useMemo, useState } from "react";
import { useGraphWorker } from "./hooks/useGraphWorker";
import {
	type NodePosition,
	useVirtualization,
} from "./hooks/useVirtualization";
import { LayoutSelector } from "./layouts/LayoutSelector";
import { type LayoutType, useDAGLayout } from "./layouts/useDAGLayout";
import { NodeDetailPanel } from "./NodeDetailPanel";
import { QAEnhancedNode } from "./nodes/QAEnhancedNode";
import { type RichNodeData, RichNodePill } from "./RichNodePill";
import type { EnhancedNodeData, GraphPerspective } from "./types";
import {
	ENHANCED_TYPE_COLORS,
	LINK_STYLES,
	PERSPECTIVE_CONFIGS,
	TYPE_TO_PERSPECTIVE,
} from "./types";

// Simplified node component for LOD rendering
function SimplifiedNodePill({ data }: { data: { id: string; type: string } }) {
	const color = ENHANCED_TYPE_COLORS[data.type] ?? "#64748b";
	return (
		<div
			className="px-2 py-1 rounded-full border text-xs font-medium flex items-center justify-center"
			style={{
				backgroundColor: `${color}20`,
				borderColor: color,
				color: color,
				width: 80,
				height: 40,
			}}
		>
			{data.id.slice(0, 4)}
		</div>
	);
}

// Medium detail node component for LOD rendering
function MediumNodePill({
	data,
}: {
	data: { id: string; type: string; label?: string };
}) {
	const color = ENHANCED_TYPE_COLORS[data.type] ?? "#64748b";
	return (
		<div
			className="px-3 py-2 rounded-lg border text-xs font-medium flex flex-col items-center justify-center"
			style={{
				backgroundColor: `${color}20`,
				borderColor: color,
				color: color,
				width: 120,
				height: 60,
			}}
		>
			<div className="font-bold">{data.id.slice(0, 6)}</div>
			{data.label && (
				<div className="text-[10px] opacity-75 truncate">
					{data.label.slice(0, 12)}
				</div>
			)}
		</div>
	);
}

const customNodeTypes = {
	richPill: RichNodePill,
	simplifiedPill: SimplifiedNodePill,
	mediumPill: MediumNodePill,
	qaEnhanced: QAEnhancedNode,
} as const satisfies NodeTypes;

interface VirtualizedGraphViewProps {
	items: Item[];
	links: Link[];
	perspective?: GraphPerspective | undefined;
	onNavigateToItem?: ((itemId: string) => void) | undefined;
	showControls?: boolean | undefined;
	autoFit?: boolean | undefined;
	enableVirtualization?: boolean | undefined;
}

/**
 * Virtualized graph view for handling 1000+ nodes
 * Uses viewport culling and level-of-detail rendering
 */
function VirtualizedGraphViewComponent({
	items,
	links,
	perspective: externalPerspective,
	onNavigateToItem,
	showControls = true,
	autoFit = true,
	enableVirtualization = true,
}: VirtualizedGraphViewProps) {
	// Perspective management
	const [internalPerspective, setInternalPerspective] =
		useState<GraphPerspective>("all");
	const perspective = externalPerspective ?? internalPerspective;
	const setPerspective =
		externalPerspective !== undefined ? () => {} : setInternalPerspective;

	const [layout, setLayout] = useState<LayoutType>("flow-chart");
	const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
	const [showDetailPanel, setShowDetailPanel] = useState(true);
	const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

	// Virtualization state
	const [viewport, setViewport] = useState({
		x: 0,
		y: 0,
		width: 1000,
		height: 600,
		zoom: 1,
	});

	const { fitView, zoomIn, zoomOut, getViewport } = useReactFlow();
	useGraphWorker();

	// Build enhanced node data
	const enhancedNodes = useMemo((): EnhancedNodeData[] => {
		const itemMap = new Map(items.map((item) => [item.id, item]));
		const incomingCount = new Map<string, number>();
		const outgoingCount = new Map<string, number>();
		const connectionsByType = new Map<string, Record<LinkType, number>>();

		for (const link of links) {
			incomingCount.set(
				link.targetId,
				(incomingCount.get(link.targetId) || 0) + 1,
			);
			outgoingCount.set(
				link.sourceId,
				(outgoingCount.get(link.sourceId) || 0) + 1,
			);

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
			const hasChildren = items.some((i) => i.parentId === item.id);

			let depth = 0;
			let currentId = item.parentId;
			while (currentId && depth < 10) {
				depth++;
				const parent = itemMap.get(currentId);
				currentId = parent?.parentId;
			}

			return {
				id: item.id,
				item,
				type: itemType,
				status: item.status,
				label: item.title || "Untitled",
				perspective: perspectives,
				connections: {
					incoming,
					outgoing,
					total: incoming + outgoing,
					byType:
						connectionsByType.get(item.id) || ({} as Record<LinkType, number>),
				},
				depth,
				hasChildren,
				parentId: item.parentId,
				uiPreview: item.metadata?.screenshotUrl
					? {
							screenshotUrl: item.metadata.screenshotUrl as string,
							thumbnailUrl: item.metadata.thumbnailUrl as string | undefined,
							interactiveWidgetUrl: item.metadata.interactiveUrl as
								| string
								| undefined,
							componentCode: item.metadata.code as string | undefined,
						}
					: undefined,
			} as EnhancedNodeData;
		});
	}, [items, links]);

	// Filter nodes by perspective
	const filteredNodes = useMemo(() => {
		if (perspective === "all") return enhancedNodes;

		const config = PERSPECTIVE_CONFIGS.find((c) => c.id === perspective);
		if (!config || config.includeTypes.length === 0) return enhancedNodes;

		return enhancedNodes.filter((node) => {
			const nodeType = node.type.toLowerCase();
			return (
				config.includeTypes.some(
					(t) => nodeType.includes(t) || t.includes(nodeType),
				) || node.perspective.includes(perspective)
			);
		});
	}, [enhancedNodes, perspective]);

	// Filter links
	const filteredLinks = useMemo(() => {
		const nodeIds = new Set(filteredNodes.map((n) => n.id));
		return links.filter(
			(link) => nodeIds.has(link.sourceId) && nodeIds.has(link.targetId),
		);
	}, [links, filteredNodes]);

	// Create node data
	const createNodeData = useCallback(
		(node: EnhancedNodeData): RichNodeData => ({
			id: node.id,
			item: node.item,
			type: node.type,
			status: node.status,
			label: node.label,
			description: node.item.description ?? undefined,
			uiPreview: node.uiPreview ?? undefined,
			connections: node.connections,
			isExpanded: expandedNodes.has(node.id),
			showPreview: perspective === "ui",
			onSelect: setSelectedNodeId,
			onExpand: (id) => {
				setExpandedNodes((prev) => {
					const next = new Set(prev);
					if (next.has(id)) next.delete(id);
					else next.add(id);
					return next;
				});
			},
			onNavigate: onNavigateToItem ?? undefined,
		}),
		[expandedNodes, perspective, onNavigateToItem],
	);

	// Nodes for layout
	const nodesForLayout = useMemo((): Node<RichNodeData>[] => {
		return filteredNodes.map((node) => ({
			id: node.id,
			type: "richPill",
			position: { x: 0, y: 0 },
			data: createNodeData(node),
		}));
	}, [filteredNodes, createNodeData]);

	// Use DAG layout
	const { nodes: dagreLaidoutNodes } = useDAGLayout<RichNodeData>(
		nodesForLayout,
		filteredLinks.map((link) => ({
			id: link.id,
			source: link.sourceId,
			target: link.targetId,
		})),
		layout,
		{
			nodeWidth: 200,
			nodeHeight: 120,
			rankSep: 100,
			nodeSep: 60,
			marginX: 40,
			marginY: 40,
		},
	);

	// Setup virtualization
	const nodePositions: NodePosition[] = useMemo(
		() =>
			dagreLaidoutNodes.map((node) => ({
				id: node.id,
				x: node.position.x,
				y: node.position.y,
				width: 200,
				height: 120,
			})),
		[dagreLaidoutNodes],
	);

	const { visibleNodeIds, lodLevel, metrics } = useVirtualization(
		nodePositions,
		viewport,
		{
			enableLOD: enableVirtualization,
			nodeWidth: 200,
			nodeHeight: 120,
			padding: 300,
		},
	);

	// Prepare visible nodes
	const initialNodes = useMemo((): Node<RichNodeData>[] => {
		if (!enableVirtualization) {
			return dagreLaidoutNodes;
		}

		return dagreLaidoutNodes
			.filter((node) => visibleNodeIds.has(node.id))
			.map((node) => ({
				...node,
				type:
					lodLevel === "high"
						? "richPill"
						: lodLevel === "medium"
							? "mediumPill"
							: "simplifiedPill",
			}));
	}, [dagreLaidoutNodes, visibleNodeIds, enableVirtualization, lodLevel]);

	const initialEdges = useMemo((): Edge[] => {
		if (!enableVirtualization) {
			const defaultStyle = { color: "#64748b", dashed: true, arrow: false };
			return filteredLinks.map((link) => {
				const linkStyle = LINK_STYLES[link.type] ?? defaultStyle;
				return {
					id: link.id,
					source: link.sourceId,
					target: link.targetId,
					type: "smoothstep",
					animated: link.type === "depends_on" || link.type === "blocks",
					style: {
						stroke: linkStyle.color,
						strokeWidth: 2,
						...(linkStyle.dashed && { strokeDasharray: "5,5" }),
					},
					label: link.type.replace(/_/g, " "),
					labelStyle: { fontSize: 10, fill: linkStyle.color },
					labelBgStyle: { fill: "rgba(26, 26, 46, 0.9)" },
					labelBgPadding: [4, 2] as [number, number],
					markerEnd: linkStyle.arrow
						? {
								type: MarkerType.ArrowClosed,
								color: linkStyle.color,
							}
						: undefined,
				} as Edge;
			});
		}

		// For virtualized view, only show edges between visible nodes
		const defaultStyle = { color: "#64748b", dashed: true, arrow: false };
		return filteredLinks
			.filter(
				(link) =>
					visibleNodeIds.has(link.sourceId) &&
					visibleNodeIds.has(link.targetId),
			)
			.map((link) => {
				const linkStyle = LINK_STYLES[link.type] ?? defaultStyle;
				return {
					id: link.id,
					source: link.sourceId,
					target: link.targetId,
					type: "smoothstep",
					animated: false, // Disable animation for large graphs
					style: {
						stroke: linkStyle.color,
						strokeWidth: 1,
						...(linkStyle.dashed && { strokeDasharray: "5,5" }),
					},
					markerEnd: linkStyle.arrow
						? {
								type: MarkerType.ArrowClosed,
								color: linkStyle.color,
							}
						: undefined,
				} as Edge;
			});
	}, [filteredLinks, visibleNodeIds, enableVirtualization]);

	const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
	const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

	// Update nodes when data changes
	useEffect(() => {
		setNodes(initialNodes);
	}, [initialNodes, setNodes]);

	useEffect(() => {
		setEdges(initialEdges);
	}, [initialEdges, setEdges]);

	// Auto-fit on initial load
	useEffect(() => {
		if (autoFit && nodes.length > 0) {
			const timer = setTimeout(() => {
				fitView({ padding: 0.2, duration: 300 });
			}, 100);
			return () => clearTimeout(timer);
		}
		return undefined;
	}, [autoFit, fitView, nodes.length]);

	// Update viewport on move/zoom
	const handleMove = useCallback(() => {
		const vp = getViewport();
		setViewport({
			x: vp.x,
			y: vp.y,
			width: 1000, // This should come from container
			height: 600,
			zoom: vp.zoom,
		});
	}, [getViewport]);

	// Selected node data
	const selectedNode = useMemo(() => {
		if (!selectedNodeId) return null;
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

	// Handlers
	const handleFit = () => fitView({ padding: 0.2, duration: 300 });
	const handleReset = () => {
		setPerspective("all");
		setLayout("flow-chart");
		setSelectedNodeId(null);
		setExpandedNodes(new Set());
	};

	const handleFocusNode = (nodeId: string) => {
		setSelectedNodeId(nodeId);
		const node = nodes.find((n) => n.id === nodeId);
		if (node) {
			fitView({ nodes: [node], padding: 0.5, duration: 300 });
		}
	};

	return (
		<div className="h-full flex flex-col">
			{/* Controls */}
			{showControls && (
				<Card className="mb-3 p-2">
					<div className="flex items-center justify-between gap-3">
						<div className="flex items-center gap-2">
							<LayoutSelector
								value={layout}
								onChange={setLayout}
								variant="select"
								className="w-[200px] h-8"
							/>

							<Separator orientation="vertical" className="h-6" />

							<Button
								variant="ghost"
								size="sm"
								onClick={() => setShowDetailPanel(!showDetailPanel)}
								className="h-8"
							>
								{showDetailPanel ? (
									<PanelRightClose className="h-4 w-4" />
								) : (
									<PanelRight className="h-4 w-4" />
								)}
							</Button>
						</div>

						<div className="flex items-center gap-2">
							{/* Performance metrics */}
							{enableVirtualization && (
								<div className="flex items-center gap-2 text-xs text-muted-foreground">
									<Activity className="h-3 w-3" />
									<span>
										{metrics.visibleNodeCount}/{metrics.totalNodeCount} · LOD:{" "}
										{lodLevel}
									</span>
								</div>
							)}

							<Separator orientation="vertical" className="h-6" />

							<div className="flex items-center gap-1 rounded-md border p-0.5">
								<Button
									variant="ghost"
									size="sm"
									onClick={() => zoomIn()}
									className="h-7 w-7 p-0"
								>
									<ZoomIn className="h-4 w-4" />
								</Button>
								<Button
									variant="ghost"
									size="sm"
									onClick={() => zoomOut()}
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
						</div>
					</div>
				</Card>
			)}

			{/* Graph area */}
			<div className="flex-1 flex gap-3">
				<Card className="flex-1 p-0 overflow-hidden">
					<ReactFlow
						nodes={nodes}
						edges={edges}
						onNodesChange={onNodesChange}
						onEdgesChange={onEdgesChange}
						onMove={handleMove}
						nodeTypes={customNodeTypes}
						fitView={autoFit}
						minZoom={0.1}
						maxZoom={2}
						proOptions={{ hideAttribution: true }}
						className="bg-background"
					>
						<Background
							variant={BackgroundVariant.Dots}
							gap={20}
							size={1}
							color="#374151"
						/>
						<Controls showInteractive={false} />
						<Panel position="bottom-left" className="!m-2">
							<div className="flex flex-wrap gap-2 text-[10px] bg-card/90 backdrop-blur-sm p-2 rounded-lg border">
								{Object.entries(ENHANCED_TYPE_COLORS)
									.filter(([type]) =>
										filteredNodes.some((n) => n.type === type),
									)
									.slice(0, 8)
									.map(([type, color]) => (
										<div key={type} className="flex items-center gap-1">
											<div
												className="h-2.5 w-5 rounded"
												style={{ backgroundColor: color }}
											/>
											<span className="capitalize">
												{type.replace(/_/g, " ")}
											</span>
										</div>
									))}
							</div>
						</Panel>
						<Panel position="top-right" className="!m-2">
							<Badge variant="secondary" className="text-xs">
								{enableVirtualization
									? `${metrics.visibleNodeCount}/${metrics.totalNodeCount} nodes`
									: `${filteredNodes.length} nodes`}{" "}
								· {filteredLinks.length} edges
							</Badge>
						</Panel>
					</ReactFlow>
				</Card>

				{/* Node Detail Panel */}
				{showDetailPanel && selectedNode && (
					<NodeDetailPanel
						node={selectedNode}
						relatedItems={relatedItems}
						incomingLinks={incomingLinks}
						outgoingLinks={outgoingLinks}
						onClose={() => setSelectedNodeId(null)}
						onNavigateToItem={onNavigateToItem || (() => {})}
						onFocusNode={handleFocusNode}
					/>
				)}
			</div>
		</div>
	);
}

export const VirtualizedGraphView = memo(VirtualizedGraphViewComponent);
