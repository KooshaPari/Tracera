// DAG Layout Hook using ELKjs for proper directed acyclic graph visualization
// Provides intuitive layout names and algorithms
// D2: When node count > LAYOUT_WORKER_THRESHOLD and layout is ELK, runs layout in Web Worker

import type { Edge, Node } from "@xyflow/react";
import type { ElkExtendedEdge, ElkNode } from "elkjs";
import * as ELKModule from "elkjs/lib/elk.bundled.js";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ElkOptionsPayload, LayoutResponse } from "./graphLayout.worker";

// D2: Use worker for ELK layout when node count exceeds this (keeps main thread responsive)
const LAYOUT_WORKER_THRESHOLD = 150;

// Handle CJS/ESM interop - elkjs exports as CJS but Vite expects ESM
const ELK = (ELKModule as any).default || ELKModule;
const elk = new ELK();

// Direction mapping from dagre convention to ELK
const DIRECTION_MAP: Record<string, string> = {
	TB: "DOWN",
	BT: "UP",
	LR: "RIGHT",
	RL: "LEFT",
};

// ============================================================================
// LAYOUT TYPES WITH INTUITIVE NAMES
// ============================================================================

export type LayoutType =
	| "flow-chart" // Top-to-bottom DAG (requirements traceability)
	| "timeline" // Left-to-right DAG (process flows)
	| "tree" // Hierarchical tree (component hierarchies)
	| "organic-network" // Force-directed (exploratory)
	| "mind-map" // Radial from center
	| "gallery" // Grid layout
	| "wheel" // Circular arrangement
	| "compact"; // Dense grid

export interface LayoutConfig {
	id: LayoutType;
	label: string;
	description: string;
	icon: string; // Lucide icon name
	algorithm: "elk" | "d3-force" | "d3-radial" | "grid" | "circular";
	bestFor: string[];
}

export const LAYOUT_CONFIGS: LayoutConfig[] = [
	{
		id: "flow-chart",
		label: "Flow Chart",
		description: "Top-to-bottom directed flow",
		icon: "ArrowDown",
		algorithm: "elk",
		bestFor: [
			"Requirements traceability",
			"Linear flows",
			"Waterfall processes",
		],
	},
	{
		id: "timeline",
		label: "Timeline",
		description: "Left-to-right progression",
		icon: "ArrowRight",
		algorithm: "elk",
		bestFor: ["Process flows", "User journeys", "Sequential tasks"],
	},
	{
		id: "tree",
		label: "Tree",
		description: "Hierarchical tree structure",
		icon: "GitBranch",
		algorithm: "elk",
		bestFor: ["Component trees", "Org charts", "File systems"],
	},
	{
		id: "organic-network",
		label: "Organic Network",
		description: "Natural clustering by relationships",
		icon: "Network",
		algorithm: "d3-force",
		bestFor: [
			"Exploratory analysis",
			"Relationship discovery",
			"Unknown structures",
		],
	},
	{
		id: "mind-map",
		label: "Mind Map",
		description: "Radial layout from center",
		icon: "CircleDot",
		algorithm: "d3-radial",
		bestFor: ["Brainstorming", "Centered exploration", "Topic mapping"],
	},
	{
		id: "gallery",
		label: "Gallery",
		description: "Grid for quick overview",
		icon: "LayoutGrid",
		algorithm: "grid",
		bestFor: ["Quick overview", "Many items", "Visual scanning"],
	},
	{
		id: "wheel",
		label: "Wheel",
		description: "Circular arrangement",
		icon: "Circle",
		algorithm: "circular",
		bestFor: ["Cyclic processes", "Stakeholder maps", "Peer relationships"],
	},
	{
		id: "compact",
		label: "Compact",
		description: "Dense space-efficient grid",
		icon: "Minimize2",
		algorithm: "grid",
		bestFor: ["Large datasets", "Dense views", "Minimized space"],
	},
];

// ============================================================================
// ELK LAYOUT ALGORITHM
// ============================================================================

interface ElkOptions {
	direction: "TB" | "LR" | "BT" | "RL";
	nodeWidth: number;
	nodeHeight: number;
	rankSep: number;
	nodeSep: number;
	marginX: number;
	marginY: number;
}

async function applyElkLayout<T extends Record<string, unknown>>(
	nodes: Node<T>[],
	edges: Edge[],
	options: ElkOptions,
): Promise<Node<T>[]> {
	if (nodes.length === 0) return [];

	const graph: ElkNode = {
		id: "root",
		layoutOptions: {
			"elk.algorithm": "layered",
			"elk.direction": DIRECTION_MAP[options.direction] || "DOWN",
			"elk.spacing.nodeNode": String(options.nodeSep),
			"elk.layered.spacing.nodeNodeBetweenLayers": String(options.rankSep),
			"elk.padding": `[left=${options.marginX}, top=${options.marginY}, right=${options.marginX}, bottom=${options.marginY}]`,
		},
		children: nodes.map((n) => ({
			id: n.id,
			width: options.nodeWidth,
			height: options.nodeHeight,
		})),
		edges: edges.map((e) => ({
			id: e.id,
			sources: [e.source],
			targets: [e.target],
		})) as ElkExtendedEdge[],
	};

	const result = await elk.layout(graph);

	// Map positions back to nodes
	const positionMap = new Map<string, { x: number; y: number }>();
	for (const child of result.children || []) {
		if (child.x !== undefined && child.y !== undefined) {
			positionMap.set(child.id, { x: child.x, y: child.y });
		}
	}

	return nodes.map((node) => {
		const pos = positionMap.get(node.id);
		if (!pos) return node;

		return {
			...node,
			position: {
				x: pos.x,
				y: pos.y,
			},
		};
	});
}

// D2: Run ELK layout in Web Worker (off main thread)
function runElkLayoutInWorker<T extends Record<string, unknown>>(
	nodes: Node<T>[],
	edges: Edge[],
	options: ElkOptions,
): Promise<Node<T>[]> {
	if (typeof Worker === "undefined") {
		return applyElkLayout(nodes, edges, options);
	}

	return new Promise((resolve, reject) => {
		const worker = new Worker(
			new URL("./graphLayout.worker.ts", import.meta.url),
			{ type: "module" },
		);

		const onMessage = (ev: MessageEvent<LayoutResponse | { type: "error"; error: string }>) => {
			worker.terminate();
			if (ev.data.type === "result") {
				const positionMap = new Map(
					ev.data.positions.map((p) => [p.id, { x: p.x, y: p.y }]),
				);
				resolve(
					nodes.map((node) => {
						const pos = positionMap.get(node.id);
						if (!pos) return node;
						return { ...node, position: pos };
					}),
				);
			} else {
				reject(new Error(ev.data.error ?? "Layout worker error"));
			}
		};

		worker.addEventListener("message", onMessage);
		worker.addEventListener("error", () => {
			worker.terminate();
			reject(new Error("Layout worker failed"));
		});

		worker.postMessage({
			type: "layout",
			nodes: nodes.map((n) => ({ id: n.id })),
			edges: edges.map((e) => ({ id: e.id, source: e.source, target: e.target })),
			options: options as ElkOptionsPayload,
		});
	});
}

// ============================================================================
// GRID LAYOUT
// ============================================================================

function applyGridLayout<T extends Record<string, unknown>>(
	nodes: Node<T>[],
	options: {
		nodeWidth: number;
		nodeHeight: number;
		padding: number;
		compact?: boolean;
	},
): Node<T>[] {
	const padding = options.compact ? options.padding / 2 : options.padding;
	const cols = Math.ceil(Math.sqrt(nodes.length));

	return nodes.map((node, index) => ({
		...node,
		position: {
			x: (index % cols) * (options.nodeWidth + padding),
			y: Math.floor(index / cols) * (options.nodeHeight + padding),
		},
	}));
}

// ============================================================================
// RADIAL LAYOUT (Mind Map)
// ============================================================================

function applyRadialLayout<T extends Record<string, unknown>>(
	nodes: Node<T>[],
	edges: Edge[],
	options: {
		nodeWidth: number;
		nodeHeight: number;
		centerX: number;
		centerY: number;
	},
): Node<T>[] {
	// Find root nodes (no incoming edges)
	const hasIncoming = new Set(edges.map((e) => e.target));
	const roots = nodes.filter((n) => !hasIncoming.has(n.id));

	// Build adjacency list
	const children = new Map<string, string[]>();
	for (const edge of edges) {
		if (!children.has(edge.source)) {
			children.set(edge.source, []);
		}
		children.get(edge.source)!.push(edge.target);
	}

	// Assign depths via BFS
	const depths = new Map<string, number>();
	const queue: { id: string; depth: number }[] = roots.map((r) => ({
		id: r.id,
		depth: 0,
	}));

	while (queue.length > 0) {
		const { id, depth } = queue.shift()!;
		if (depths.has(id)) continue;
		depths.set(id, depth);

		const nodeChildren = children.get(id) || [];
		for (const childId of nodeChildren) {
			if (!depths.has(childId)) {
				queue.push({ id: childId, depth: depth + 1 });
			}
		}
	}

	// Group by depth
	const byDepth = new Map<number, string[]>();
	for (const [id, depth] of depths) {
		if (!byDepth.has(depth)) byDepth.set(depth, []);
		byDepth.get(depth)!.push(id);
	}

	// Position nodes radially
	const positions = new Map<string, { x: number; y: number }>();
	const baseRadius = Math.max(options.nodeWidth, options.nodeHeight) * 1.5;

	byDepth.forEach((nodeIds, depth) => {
		const radius = (depth + 1) * baseRadius;
		const angleStep = (2 * Math.PI) / nodeIds.length;

		nodeIds.forEach((id, index) => {
			const angle = index * angleStep - Math.PI / 2;
			positions.set(id, {
				x: options.centerX + radius * Math.cos(angle) - options.nodeWidth / 2,
				y: options.centerY + radius * Math.sin(angle) - options.nodeHeight / 2,
			});
		});
	});

	// Handle nodes not connected to roots
	let orphanIndex = 0;
	const orphanRadius = (byDepth.size + 1) * baseRadius;

	return nodes.map((node) => {
		let pos = positions.get(node.id);
		if (!pos) {
			// Orphan node - place on outer ring
			const angle = (orphanIndex++ * 2 * Math.PI) / 8 - Math.PI / 2;
			pos = {
				x:
					options.centerX +
					orphanRadius * Math.cos(angle) -
					options.nodeWidth / 2,
				y:
					options.centerY +
					orphanRadius * Math.sin(angle) -
					options.nodeHeight / 2,
			};
		}
		return { ...node, position: pos };
	});
}

// ============================================================================
// CIRCULAR LAYOUT (Wheel)
// ============================================================================

function applyCircularLayout<T extends Record<string, unknown>>(
	nodes: Node<T>[],
	options: {
		nodeWidth: number;
		nodeHeight: number;
		centerX: number;
		centerY: number;
	},
): Node<T>[] {
	const count = nodes.length;
	const radius = Math.max(300, count * 20);
	const angleStep = (2 * Math.PI) / count;

	return nodes.map((node, index) => {
		const angle = index * angleStep - Math.PI / 2;
		return {
			...node,
			position: {
				x: options.centerX + radius * Math.cos(angle) - options.nodeWidth / 2,
				y: options.centerY + radius * Math.sin(angle) - options.nodeHeight / 2,
			},
		};
	});
}

// ============================================================================
// FORCE-DIRECTED LAYOUT (Organic Network)
// ============================================================================

function applyForceLayout<T extends Record<string, unknown>>(
	nodes: Node<T>[],
	edges: Edge[],
	options: { nodeWidth: number; nodeHeight: number; padding: number },
): Node<T>[] {
	// Simple force simulation (basic spring layout)
	const positions = new Map<
		string,
		{ x: number; y: number; vx: number; vy: number }
	>();
	const cols = Math.ceil(Math.sqrt(nodes.length));

	// Initial positions in grid with jitter
	nodes.forEach((node, index) => {
		const baseX = (index % cols) * (options.nodeWidth + options.padding * 2);
		const baseY =
			Math.floor(index / cols) * (options.nodeHeight + options.padding * 2);
		positions.set(node.id, {
			x: baseX + (Math.random() - 0.5) * 50,
			y: baseY + (Math.random() - 0.5) * 50,
			vx: 0,
			vy: 0,
		});
	});

	// Build edge map
	const adjacency = new Map<string, Set<string>>();
	for (const edge of edges) {
		if (!adjacency.has(edge.source)) adjacency.set(edge.source, new Set());
		if (!adjacency.has(edge.target)) adjacency.set(edge.target, new Set());
		adjacency.get(edge.source)!.add(edge.target);
		adjacency.get(edge.target)!.add(edge.source);
	}

	// Run simulation iterations
	const iterations = 50;
	const repulsionStrength = 5000;
	const attractionStrength = 0.1;
	const damping = 0.9;

	for (let iter = 0; iter < iterations; iter++) {
		// Repulsion between all nodes
		for (const node1 of nodes) {
			const p1 = positions.get(node1.id)!;
			for (const node2 of nodes) {
				if (node1.id === node2.id) continue;
				const p2 = positions.get(node2.id)!;

				const dx = p1.x - p2.x;
				const dy = p1.y - p2.y;
				const dist = Math.sqrt(dx * dx + dy * dy) || 1;
				const force = repulsionStrength / (dist * dist);

				p1.vx += (dx / dist) * force;
				p1.vy += (dy / dist) * force;
			}
		}

		// Attraction along edges
		for (const edge of edges) {
			const p1 = positions.get(edge.source);
			const p2 = positions.get(edge.target);
			if (!p1 || !p2) continue;

			const dx = p2.x - p1.x;
			const dy = p2.y - p1.y;

			p1.vx += dx * attractionStrength;
			p1.vy += dy * attractionStrength;
			p2.vx -= dx * attractionStrength;
			p2.vy -= dy * attractionStrength;
		}

		// Apply velocities and damping
		for (const node of nodes) {
			const p = positions.get(node.id)!;
			p.x += p.vx;
			p.y += p.vy;
			p.vx *= damping;
			p.vy *= damping;
		}
	}

	// Normalize positions (move to positive quadrant)
	let minX = Infinity;
	let minY = Infinity;
	for (const p of positions.values()) {
		minX = Math.min(minX, p.x);
		minY = Math.min(minY, p.y);
	}

	return nodes.map((node) => {
		const p = positions.get(node.id)!;
		return {
			...node,
			position: {
				x: p.x - minX + 50,
				y: p.y - minY + 50,
			},
		};
	});
}

// ============================================================================
// MAIN HOOK
// ============================================================================

interface UseDAGLayoutOptions {
	nodeWidth?: number;
	nodeHeight?: number;
	rankSep?: number;
	nodeSep?: number;
	marginX?: number;
	marginY?: number;
	centerX?: number;
	centerY?: number;
}

export function useDAGLayout<T extends Record<string, unknown>>(
	nodes: Node<T>[],
	edges: Edge[],
	layout: LayoutType,
	options: UseDAGLayoutOptions = {},
) {
	const {
		nodeWidth = 200,
		nodeHeight = 80,
		rankSep = 100,
		nodeSep = 60,
		marginX = 40,
		marginY = 40,
		centerX = 500,
		centerY = 400,
	} = options;

	const [layoutedNodes, setLayoutedNodes] = useState<Node<T>[]>(nodes);
	const [isLayouting, setIsLayouting] = useState(false);
	const prevSignatureRef = useRef<string>("");

	const layoutConfig = useMemo(
		() => LAYOUT_CONFIGS.find((c) => c.id === layout) || LAYOUT_CONFIGS[0],
		[layout],
	);

	// Synchronous layouts (grid, radial, force, circular)
	const applySyncLayout = useCallback(
		(inputNodes: Node<T>[], inputEdges: Edge[]): Node<T>[] | null => {
			if (inputNodes.length === 0) return [];

			switch (layout) {
				case "organic-network":
					return applyForceLayout(inputNodes, inputEdges, {
						nodeWidth,
						nodeHeight,
						padding: nodeSep,
					});

				case "mind-map":
					return applyRadialLayout(inputNodes, inputEdges, {
						nodeWidth,
						nodeHeight,
						centerX,
						centerY,
					});

				case "gallery":
					return applyGridLayout(inputNodes, {
						nodeWidth,
						nodeHeight,
						padding: nodeSep,
						compact: false,
					});

				case "wheel":
					return applyCircularLayout(inputNodes, {
						nodeWidth,
						nodeHeight,
						centerX,
						centerY,
					});

				case "compact":
					return applyGridLayout(inputNodes, {
						nodeWidth,
						nodeHeight,
						padding: nodeSep / 2,
						compact: true,
					});

				default:
					return null; // Signal that async ELK layout is needed
			}
		},
		[layout, nodeWidth, nodeHeight, nodeSep, centerX, centerY],
	);

	// Async ELK layout options
	const elkOptions = useMemo((): ElkOptions | null => {
		switch (layout) {
			case "flow-chart":
				return {
					direction: "TB",
					nodeWidth,
					nodeHeight,
					rankSep,
					nodeSep,
					marginX,
					marginY,
				};

			case "timeline":
				return {
					direction: "LR",
					nodeWidth,
					nodeHeight,
					rankSep,
					nodeSep,
					marginX,
					marginY,
				};

			case "tree":
				return {
					direction: "TB",
					nodeWidth,
					nodeHeight,
					rankSep: rankSep * 1.5,
					nodeSep: nodeSep * 0.8,
					marginX,
					marginY,
				};

			default:
				return null;
		}
	}, [layout, nodeWidth, nodeHeight, rankSep, nodeSep, marginX, marginY]);

	// Effect to apply layout when inputs change
	useEffect(() => {
		const signature = `${layout}|${nodes.map((n) => n.id).join("|")}|${edges
			.map((e) => `${e.id}:${e.source}->${e.target}`)
			.join("|")}`;
		if (signature === prevSignatureRef.current) {
			return;
		}
		prevSignatureRef.current = signature;

		if (nodes.length === 0) {
			setLayoutedNodes([]);
			return;
		}

		// Try synchronous layout first
		const syncResult = applySyncLayout(nodes, edges);
		if (syncResult !== null) {
			setLayoutedNodes(syncResult);
			return;
		}

		// Use async ELK layout (D2: in worker when node count is high)
		if (elkOptions) {
			setIsLayouting(true);
			const layoutPromise =
				nodes.length > LAYOUT_WORKER_THRESHOLD
					? runElkLayoutInWorker(nodes, edges, elkOptions)
					: applyElkLayout(nodes, edges, elkOptions);
			layoutPromise
				.then((result) => {
					setLayoutedNodes(result);
				})
				.catch((err) => {
					logger.error("ELK layout failed:", err);
					// Fallback to grid layout
					setLayoutedNodes(
						applyGridLayout(nodes, {
							nodeWidth,
							nodeHeight,
							padding: nodeSep,
							compact: false,
						}),
					);
				})
				.finally(() => {
					setIsLayouting(false);
				});
		}
	}, [
		nodes,
		edges,
		applySyncLayout,
		elkOptions,
		nodeWidth,
		nodeHeight,
		nodeSep,
		layout,
	]);

	// Calculate layout function for external use
	const calculateLayout = useCallback(
		async (inputNodes: Node<T>[], inputEdges: Edge[]): Promise<Node<T>[]> => {
			if (inputNodes.length === 0) return [];

			// Try synchronous layout first
			const syncResult = applySyncLayout(inputNodes, inputEdges);
			if (syncResult !== null) {
				return syncResult;
			}

			// Use async ELK layout (D2: in worker when node count is high)
			if (elkOptions) {
				try {
					return inputNodes.length > LAYOUT_WORKER_THRESHOLD
						? await runElkLayoutInWorker(inputNodes, inputEdges, elkOptions)
						: await applyElkLayout(inputNodes, inputEdges, elkOptions);
				} catch (err) {
					logger.error("ELK layout failed:", err);
					// Fallback to grid layout
					return applyGridLayout(inputNodes, {
						nodeWidth,
						nodeHeight,
						padding: nodeSep,
						compact: false,
					});
				}
			}

			// Final fallback
			return applyGridLayout(inputNodes, {
				nodeWidth,
				nodeHeight,
				padding: nodeSep,
				compact: false,
			});
		},
		[applySyncLayout, elkOptions, nodeWidth, nodeHeight, nodeSep],
	);

	return {
		nodes: layoutedNodes,
		layoutConfig,
		calculateLayout,
		isLayouting,
	};
}

export default useDAGLayout;
