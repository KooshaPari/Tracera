/**
 * Web Worker for off-main-thread graph layout computation
 *
 * This worker handles computationally expensive layout algorithms (Dagre, ELK, D3-Force)
 * without blocking the main UI thread. It uses Comlink for type-safe communication
 * and supports progressive layout streaming for large graphs.
 *
 * Performance targets:
 * - 10k nodes: <2s layout time, zero main thread blocking
 * - 100k nodes: <20s layout time with progressive updates
 *
 * @module graphLayout.worker
 */

import * as Comlink from 'comlink';
import type { ElkExtendedEdge, ElkNode } from 'elkjs';
import * as ELKModule from 'elkjs/lib/elk.bundled.js';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface LayoutNode {
	id: string;
	width: number;
	height: number;
}

export interface LayoutEdge {
	id: string;
	source: string;
	target: string;
}

export interface NodePosition {
	x: number;
	y: number;
}

export type LayoutAlgorithm = 'dagre' | 'elk' | 'd3-force' | 'grid' | 'circular' | 'radial';

export interface LayoutOptions {
	algorithm: LayoutAlgorithm;
	direction?: 'TB' | 'LR' | 'BT' | 'RL';
	nodeSep?: number;
	rankSep?: number;
	marginX?: number;
	marginY?: number;
	nodeWidth?: number;
	nodeHeight?: number;
	centerX?: number;
	centerY?: number;
	// Progressive layout options
	progressive?: boolean;
	batchSize?: number;
}

export interface LayoutResult {
	positions: Record<string, NodePosition>;
	size: { width: number; height: number };
	// For progressive layout
	isPartial?: boolean;
	progress?: number;
}

export interface ProgressCallback {
	(result: LayoutResult): void;
}

// ============================================================================
// ELK SETUP
// ============================================================================

// Direction mapping from dagre convention to ELK
const DIRECTION_MAP: Record<string, string> = {
	TB: 'DOWN',
	BT: 'UP',
	LR: 'RIGHT',
	RL: 'LEFT',
};

// Lazy ELK initialization to avoid test environment issues
let elkInstance: any = null;

function getELK() {
	if (!elkInstance) {
		try {
			const ELK = (ELKModule as any).default || ELKModule;
			elkInstance = new ELK();
		} catch (error) {
			logger.error('[GraphLayoutWorker] Failed to initialize ELK:', error);
			throw error;
		}
	}
	return elkInstance;
}

// ============================================================================
// LAYOUT ALGORITHMS
// ============================================================================

/**
 * ELK Layout Algorithm (Hierarchical DAG)
 * Best for: Flow charts, timelines, tree structures
 * Complexity: O(n log n) where n = nodes
 */
async function layoutWithELK(
	nodes: LayoutNode[],
	edges: LayoutEdge[],
	options: LayoutOptions
): Promise<LayoutResult> {
	if (nodes.length === 0) {
		return { positions: {}, size: { width: 0, height: 0 } };
	}

	const {
		direction = 'TB',
		nodeSep = 60,
		rankSep = 100,
		marginX = 40,
		marginY = 40,
		nodeWidth = 200,
		nodeHeight = 120,
	} = options;

	const graph: ElkNode = {
		id: 'root',
		layoutOptions: {
			'elk.algorithm': 'layered',
			'elk.direction': DIRECTION_MAP[direction] || 'DOWN',
			'elk.spacing.nodeNode': String(nodeSep),
			'elk.layered.spacing.nodeNodeBetweenLayers': String(rankSep),
			'elk.padding': `[left=${marginX}, top=${marginY}, right=${marginX}, bottom=${marginY}]`,
			'elk.layered.nodePlacement.strategy': 'NETWORK_SIMPLEX',
			'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
		},
		children: nodes.map((n) => ({
			id: n.id,
			width: n.width || nodeWidth,
			height: n.height || nodeHeight,
		})),
		edges: edges.map((e) => ({
			id: e.id,
			sources: [e.source],
			targets: [e.target],
		})) as ElkExtendedEdge[],
	};

	const elk = getELK();
	const result = await elk.layout(graph);

	// Extract positions
	const positions: Record<string, NodePosition> = {};
	let maxX = 0;
	let maxY = 0;

	for (const child of result.children || []) {
		if (child.x !== undefined && child.y !== undefined) {
			positions[child.id] = { x: child.x, y: child.y };
			maxX = Math.max(maxX, child.x + (child.width || nodeWidth));
			maxY = Math.max(maxY, child.y + (child.height || nodeHeight));
		}
	}

	return {
		positions,
		size: { width: maxX + marginX, height: maxY + marginY },
	};
}

/**
 * Dagre Layout Algorithm (Simple DAG)
 * Best for: Simple directed graphs
 * Complexity: O(n + e) where n = nodes, e = edges
 */
function layoutWithDagre(
	nodes: LayoutNode[],
	edges: LayoutEdge[],
	options: LayoutOptions
): LayoutResult {
	if (nodes.length === 0) {
		return { positions: {}, size: { width: 0, height: 0 } };
	}

	const {
		nodeWidth = 200,
		nodeHeight = 120,
		nodeSep = 60,
		rankSep = 100,
		marginX = 40,
		marginY = 40,
	} = options;

	// Build adjacency list
	const graph = new Map<string, string[]>();
	for (const node of nodes) {
		graph.set(node.id, []);
	}
	for (const edge of edges) {
		if (graph.has(edge.source)) {
			graph.get(edge.source)!.push(edge.target);
		}
	}

	// Topological sort with level assignment
	const levels = new Map<string, number>();
	const visited = new Set<string>();

	function assignLevel(nodeId: string): number {
		if (visited.has(nodeId)) {
			return levels.get(nodeId) || 0;
		}
		visited.add(nodeId);

		let maxIncomingLevel = -1;
		// Find incoming edges
		for (const [source, targets] of graph) {
			if (targets.includes(nodeId)) {
				const srcLevel = assignLevel(source);
				maxIncomingLevel = Math.max(maxIncomingLevel, srcLevel);
			}
		}

		const nodeLevel = maxIncomingLevel + 1;
		levels.set(nodeId, nodeLevel);
		return nodeLevel;
	}

	// Assign levels to all nodes
	for (const nodeId of graph.keys()) {
		assignLevel(nodeId);
	}

	// Group nodes by level
	const levelGroups = new Map<number, string[]>();
	for (const [nodeId, level] of levels) {
		if (!levelGroups.has(level)) {
			levelGroups.set(level, []);
		}
		levelGroups.get(level)!.push(nodeId);
	}

	// Calculate positions
	const positions: Record<string, NodePosition> = {};
	let maxWidth = 0;
	let maxHeight = 0;

	const maxLevel = Math.max(...Array.from(levelGroups.keys()));
	for (const [level, nodeIds] of levelGroups) {
		const y = marginY + level * (nodeHeight + rankSep);
		const levelWidth = nodeIds.length * (nodeWidth + nodeSep);
		const startX = marginX + (maxLevel > 5 ? -levelWidth / 2 : 0);

		nodeIds.forEach((nodeId, index) => {
			const x = startX + index * (nodeWidth + nodeSep);
			positions[nodeId] = { x: Math.max(marginX, x), y };
			maxWidth = Math.max(maxWidth, x + nodeWidth + marginX);
			maxHeight = Math.max(maxHeight, y + nodeHeight + marginY);
		});
	}

	return {
		positions,
		size: { width: maxWidth, height: maxHeight },
	};
}

/**
 * D3 Force Layout Algorithm (Organic network)
 * Best for: Exploratory analysis, relationship discovery
 * Complexity: O(n² * iterations) - expensive but produces natural layouts
 */
function layoutWithForce(
	nodes: LayoutNode[],
	edges: LayoutEdge[],
	options: LayoutOptions
): LayoutResult {
	if (nodes.length === 0) {
		return { positions: {}, size: { width: 0, height: 0 } };
	}

	const {
		nodeWidth = 200,
		nodeHeight = 120,
		nodeSep = 60,
	} = options;

	// Initialize positions with jitter
	const positions = new Map<
		string,
		{ x: number; y: number; vx: number; vy: number }
	>();
	const cols = Math.ceil(Math.sqrt(nodes.length));

	nodes.forEach((node, index) => {
		const baseX = (index % cols) * (nodeWidth + nodeSep * 2);
		const baseY = Math.floor(index / cols) * (nodeHeight + nodeSep * 2);
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

	// Run simulation
	const iterations = Math.min(50, Math.max(20, 100 - Math.floor(nodes.length / 100)));
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

	// Normalize positions to positive quadrant
	let minX = Infinity;
	let minY = Infinity;
	let maxX = -Infinity;
	let maxY = -Infinity;

	for (const p of positions.values()) {
		minX = Math.min(minX, p.x);
		minY = Math.min(minY, p.y);
		maxX = Math.max(maxX, p.x);
		maxY = Math.max(maxY, p.y);
	}

	const result: Record<string, NodePosition> = {};
	for (const [id, p] of positions) {
		result[id] = {
			x: p.x - minX + 50,
			y: p.y - minY + 50,
		};
	}

	return {
		positions: result,
		size: {
			width: maxX - minX + nodeWidth + 100,
			height: maxY - minY + nodeHeight + 100,
		},
	};
}

/**
 * Grid Layout Algorithm
 * Best for: Quick overview, many items
 * Complexity: O(n)
 */
function layoutWithGrid(
	nodes: LayoutNode[],
	_edges: LayoutEdge[],
	options: LayoutOptions
): LayoutResult {
	if (nodes.length === 0) {
		return { positions: {}, size: { width: 0, height: 0 } };
	}

	const {
		nodeWidth = 200,
		nodeHeight = 120,
		nodeSep = 60,
		marginX = 40,
		marginY = 40,
	} = options;

	const cols = Math.ceil(Math.sqrt(nodes.length));
	const positions: Record<string, NodePosition> = {};
	let maxWidth = 0;
	let maxHeight = 0;

	nodes.forEach((node, index) => {
		const x = marginX + (index % cols) * (nodeWidth + nodeSep);
		const y = marginY + Math.floor(index / cols) * (nodeHeight + nodeSep);
		positions[node.id] = { x, y };
		maxWidth = Math.max(maxWidth, x + nodeWidth + marginX);
		maxHeight = Math.max(maxHeight, y + nodeHeight + marginY);
	});

	return {
		positions,
		size: { width: maxWidth, height: maxHeight },
	};
}

/**
 * Circular Layout Algorithm
 * Best for: Cyclic processes, peer relationships
 * Complexity: O(n)
 */
function layoutWithCircular(
	nodes: LayoutNode[],
	_edges: LayoutEdge[],
	options: LayoutOptions
): LayoutResult {
	if (nodes.length === 0) {
		return { positions: {}, size: { width: 0, height: 0 } };
	}

	const {
		nodeWidth = 200,
		nodeHeight = 120,
		centerX = 500,
		centerY = 400,
	} = options;

	const count = nodes.length;
	const radius = Math.max(300, count * 20);
	const angleStep = (2 * Math.PI) / count;

	const positions: Record<string, NodePosition> = {};

	nodes.forEach((node, index) => {
		const angle = index * angleStep - Math.PI / 2;
		positions[node.id] = {
			x: centerX + radius * Math.cos(angle) - nodeWidth / 2,
			y: centerY + radius * Math.sin(angle) - nodeHeight / 2,
		};
	});

	const size = {
		width: centerX * 2 + radius + nodeWidth,
		height: centerY * 2 + radius + nodeHeight,
	};

	return { positions, size };
}

/**
 * Radial Layout Algorithm (Mind Map)
 * Best for: Brainstorming, centered exploration
 * Complexity: O(n + e)
 */
function layoutWithRadial(
	nodes: LayoutNode[],
	edges: LayoutEdge[],
	options: LayoutOptions
): LayoutResult {
	if (nodes.length === 0) {
		return { positions: {}, size: { width: 0, height: 0 } };
	}

	const {
		nodeWidth = 200,
		nodeHeight = 120,
		centerX = 500,
		centerY = 400,
	} = options;

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
	const positions: Record<string, NodePosition> = {};
	const baseRadius = Math.max(nodeWidth, nodeHeight) * 1.5;

	byDepth.forEach((nodeIds, depth) => {
		const radius = (depth + 1) * baseRadius;
		const angleStep = (2 * Math.PI) / nodeIds.length;

		nodeIds.forEach((id, index) => {
			const angle = index * angleStep - Math.PI / 2;
			positions[id] = {
				x: centerX + radius * Math.cos(angle) - nodeWidth / 2,
				y: centerY + radius * Math.sin(angle) - nodeHeight / 2,
			};
		});
	});

	// Handle orphan nodes
	let orphanIndex = 0;
	const orphanRadius = (byDepth.size + 1) * baseRadius;

	for (const node of nodes) {
		if (!positions[node.id]) {
			const angle = (orphanIndex++ * 2 * Math.PI) / 8 - Math.PI / 2;
			positions[node.id] = {
				x: centerX + orphanRadius * Math.cos(angle) - nodeWidth / 2,
				y: centerY + orphanRadius * Math.sin(angle) - nodeHeight / 2,
			};
		}
	}

	const maxDepth = byDepth.size;
	const size = {
		width: centerX * 2 + maxDepth * baseRadius + nodeWidth,
		height: centerY * 2 + maxDepth * baseRadius + nodeHeight,
	};

	return { positions, size };
}

// ============================================================================
// PROGRESSIVE LAYOUT
// ============================================================================

/**
 * Progressive layout computation with streaming results
 * Allows UI to show partial results while computation continues
 */
async function* layoutProgressive(
	nodes: LayoutNode[],
	edges: LayoutEdge[],
	options: LayoutOptions
): AsyncGenerator<LayoutResult> {
	const batchSize = options.batchSize || 100;
	const totalBatches = Math.ceil(nodes.length / batchSize);

	// For now, we'll implement progressive for grid layout (simplest)
	// Future: Implement for ELK and other algorithms
	if (options.algorithm === 'grid') {
		for (let i = 0; i < totalBatches; i++) {
			const start = i * batchSize;
			const end = Math.min(start + batchSize, nodes.length);
			const batchNodes = nodes.slice(0, end);

			const result = layoutWithGrid(batchNodes, edges, options);
			yield {
				...result,
				isPartial: i < totalBatches - 1,
				progress: (i + 1) / totalBatches,
			};
		}
	} else {
		// For complex algorithms, just compute once
		const result = await computeLayout(nodes, edges, options);
		yield result;
	}
}

// ============================================================================
// MAIN API
// ============================================================================

/**
 * Compute graph layout using specified algorithm
 */
export async function computeLayout(
	nodes: LayoutNode[],
	edges: LayoutEdge[],
	options: LayoutOptions
): Promise<LayoutResult> {
	const startTime = performance.now();

	let result: LayoutResult;

	switch (options.algorithm) {
		case 'elk':
			result = await layoutWithELK(nodes, edges, options);
			break;
		case 'dagre':
			result = layoutWithDagre(nodes, edges, options);
			break;
		case 'd3-force':
			result = layoutWithForce(nodes, edges, options);
			break;
		case 'grid':
			result = layoutWithGrid(nodes, edges, options);
			break;
		case 'circular':
			result = layoutWithCircular(nodes, edges, options);
			break;
		case 'radial':
			result = layoutWithRadial(nodes, edges, options);
			break;
		default:
			result = layoutWithGrid(nodes, edges, options);
	}

	const duration = performance.now() - startTime;
	logger.info(
		`[GraphLayoutWorker] Layout ${options.algorithm} for ${nodes.length} nodes completed in ${duration.toFixed(2)}ms`
	);

	return result;
}

/**
 * Compute layout progressively with streaming results
 */
export async function* computeLayoutProgressive(
	nodes: LayoutNode[],
	edges: LayoutEdge[],
	options: LayoutOptions
): AsyncGenerator<LayoutResult> {
	yield* layoutProgressive(nodes, edges, options);
}

/**
 * Benchmark layout algorithm performance
 */
export async function benchmarkLayout(
	nodes: LayoutNode[],
	edges: LayoutEdge[],
	algorithm: LayoutAlgorithm,
	iterations: number = 5
): Promise<{
	algorithm: LayoutAlgorithm;
	nodeCount: number;
	edgeCount: number;
	iterations: number;
	avgTime: number;
	minTime: number;
	maxTime: number;
	stdDev: number;
}> {
	const times: number[] = [];

	for (let i = 0; i < iterations; i++) {
		const start = performance.now();
		await computeLayout(nodes, edges, { algorithm });
		const duration = performance.now() - start;
		times.push(duration);
	}

	const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
	const minTime = Math.min(...times);
	const maxTime = Math.max(...times);
	const variance =
		times.reduce((sum, time) => sum + Math.pow(time - avgTime, 2), 0) /
		times.length;
	const stdDev = Math.sqrt(variance);

	return {
		algorithm,
		nodeCount: nodes.length,
		edgeCount: edges.length,
		iterations,
		avgTime,
		minTime,
		maxTime,
		stdDev,
	};
}

// ============================================================================
// EXPOSE API VIA COMLINK
// ============================================================================

const api = {
	computeLayout,
	computeLayoutProgressive,
	benchmarkLayout,
};

Comlink.expose(api);

export type GraphLayoutWorkerAPI = typeof api;
