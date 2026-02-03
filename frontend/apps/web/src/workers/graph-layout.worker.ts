/**
 * Graph Layout Worker
 *
 * Performs heavy graph layout computations off the main thread:
 * - Dagre layouts
 * - Force-directed layouts
 * - ELK hierarchical layouts
 */

import { expose } from "comlink";

export interface LayoutNode {
	id: string;
	width: number;
	height: number;
	data?: any;
}

export interface LayoutEdge {
	id: string;
	source: string;
	target: string;
	data?: any;
}

export interface LayoutOptions {
	type: "dagre" | "force" | "elk" | "hierarchical";
	direction?: "TB" | "LR" | "BT" | "RL";
	nodeSep?: number;
	rankSep?: number;
	marginX?: number;
	marginY?: number;
	iterations?: number;
}

export interface LayoutResult {
	positions: Record<string, { x: number; y: number }>;
	size: { width: number; height: number };
}

export type ProgressCallback = (progress: number) => void;

/**
 * Dagre-style hierarchical layout
 */
function layoutDagre(
	nodes: LayoutNode[],
	edges: LayoutEdge[],
	options: LayoutOptions,
	onProgress?: ProgressCallback,
): LayoutResult {
	onProgress?.(0);

	const nodeMap = new Map(nodes.map((n) => [n.id, n]));
	const graph = new Map<string, string[]>();

	// Build adjacency list
	for (const node of nodes) {
		graph.set(node.id, []);
	}
	for (const edge of edges) {
		if (graph.has(edge.source)) {
			graph.get(edge.source)!.push(edge.target);
		}
	}

	onProgress?.(20);

	// Topological sort with level assignment
	const levels = new Map<string, number>();
	const visited = new Set<string>();
	const inDegree = new Map<string, number>();

	// Calculate in-degrees
	for (const node of nodes) {
		inDegree.set(node.id, 0);
	}
	for (const [, targets] of graph) {
		for (const target of targets) {
			inDegree.set(target, (inDegree.get(target) ?? 0) + 1);
		}
	}

	onProgress?.(40);

	// Kahn's algorithm for topological sort
	const queue: string[] = [];
	for (const [nodeId, degree] of inDegree) {
		if (degree === 0) {
			queue.push(nodeId);
			levels.set(nodeId, 0);
		}
	}

	let level = 0;
	while (queue.length > 0) {
		const levelSize = queue.length;
		const nextQueue: string[] = [];

		for (let i = 0; i < levelSize; i += 1) {
			const nodeId = queue.shift()!;
			visited.add(nodeId);

			const targets = graph.get(nodeId) ?? [];
			for (const target of targets) {
				const newDegree = (inDegree.get(target) ?? 0) - 1;
				inDegree.set(target, newDegree);

				if (newDegree === 0 && !visited.has(target)) {
					nextQueue.push(target);
					levels.set(target, level + 1);
				}
			}
		}

		queue.push(...nextQueue);
		level += 1;
	}

	onProgress?.(60);

	// Handle remaining nodes (cycles or disconnected)
	for (const node of nodes) {
		if (!levels.has(node.id)) {
			levels.set(node.id, level);
		}
	}

	// Group nodes by level
	const levelGroups = new Map<number, string[]>();
	for (const [nodeId, nodeLevel] of levels) {
		if (!levelGroups.has(nodeLevel)) {
			levelGroups.set(nodeLevel, []);
		}
		levelGroups.get(nodeLevel)!.push(nodeId);
	}

	onProgress?.(80);

	// Calculate positions
	const positions: Record<string, { x: number; y: number }> = {};
	const nodeSep = options.nodeSep ?? 60;
	const rankSep = options.rankSep ?? 100;
	const marginX = options.marginX ?? 40;
	const marginY = options.marginY ?? 40;

	let maxWidth = 0;
	let maxHeight = 0;

	const direction = options.direction ?? "TB";
	const isHorizontal = direction === "LR" || direction === "RL";
	const isReverse = direction === "BT" || direction === "RL";

	for (const [nodeLevel, nodeIds] of levelGroups) {
		const levelNodes = nodeIds.map((id) => nodeMap.get(id)!);
		const totalLevelWidth = levelNodes.reduce((sum, n) => sum + n.width, 0);
		const totalSepWidth = (nodeIds.length - 1) * nodeSep;

		const primaryCoord = marginY + nodeLevel * rankSep;
		let secondaryCoord = marginX;

		// Center nodes in level
		const levelWidth = totalLevelWidth + totalSepWidth;
		const maxLevelWidth = Math.max(
			...[...levelGroups.values()].map((ids) => {
				const lvlNodes = ids.map((id) => nodeMap.get(id)!);
				return (
					lvlNodes.reduce((sum, n) => sum + n.width, 0) +
					(ids.length - 1) * nodeSep
				);
			}),
		);
		const offset = (maxLevelWidth - levelWidth) / 2;

		for (const nodeId of nodeIds) {
			const node = nodeMap.get(nodeId)!;

			if (isHorizontal) {
				const x = isReverse ? maxWidth - primaryCoord : primaryCoord;
				const y = secondaryCoord + offset;
				positions[nodeId] = { x, y };
				maxWidth = Math.max(maxWidth, x + node.width + marginX);
				maxHeight = Math.max(maxHeight, y + node.height + marginY);
			} else {
				const x = secondaryCoord + offset;
				const y = isReverse ? maxHeight - primaryCoord : primaryCoord;
				positions[nodeId] = { x, y };
				maxWidth = Math.max(maxWidth, x + node.width + marginX);
				maxHeight = Math.max(maxHeight, y + node.height + marginY);
			}

			secondaryCoord += node.width + nodeSep;
		}
	}

	onProgress?.(100);

	return {
		positions,
		size: { height: maxHeight || 600, width: maxWidth || 800 },
	};
}

/**
 * Force-directed layout (simple spring model)
 */
function layoutForce(
	nodes: LayoutNode[],
	edges: LayoutEdge[],
	options: LayoutOptions,
	onProgress?: ProgressCallback,
): LayoutResult {
	const iterations = options.iterations ?? 100;
	const width = 1000;
	const height = 800;

	// Initialize random positions
	const positions = new Map<
		string,
		{ x: number; y: number; vx: number; vy: number }
	>();
	for (const node of nodes) {
		positions.set(node.id, {
			vx: 0,
			vy: 0,
			x: Math.random() * width,
			y: Math.random() * height,
		});
	}

	const k = Math.sqrt((width * height) / nodes.length);
	const c = 0.1; // Damping factor

	for (let iteration = 0; iteration < iterations; iteration += 1) {
		// Repulsive forces between all nodes
		for (let i = 0; i < nodes.length; i += 1) {
			const node1 = nodes[i];
			const pos1 = positions.get(node1.id)!;

			for (let j = i + 1; j < nodes.length; j += 1) {
				const node2 = nodes[j];
				const pos2 = positions.get(node2.id)!;

				const dx = pos2.x - pos1.x;
				const dy = pos2.y - pos1.y;
				const distance = Math.sqrt(dx * dx + dy * dy) || 0.01;

				const force = (k * k) / distance;
				const fx = (dx / distance) * force;
				const fy = (dy / distance) * force;

				pos1.vx -= fx;
				pos1.vy -= fy;
				pos2.vx += fx;
				pos2.vy += fy;
			}
		}

		// Attractive forces along edges
		for (const edge of edges) {
			const pos1 = positions.get(edge.source);
			const pos2 = positions.get(edge.target);

			if (!pos1 || !pos2) {
				continue;
			}

			const dx = pos2.x - pos1.x;
			const dy = pos2.y - pos1.y;
			const distance = Math.sqrt(dx * dx + dy * dy) || 0.01;

			const force = distance / k;
			const fx = (dx / distance) * force;
			const fy = (dy / distance) * force;

			pos1.vx += fx;
			pos1.vy += fy;
			pos2.vx -= fx;
			pos2.vy -= fy;
		}

		// Update positions with damping
		for (const [_nodeId, pos] of positions) {
			pos.x += pos.vx * c;
			pos.y += pos.vy * c;
			pos.vx *= 0.9;
			pos.vy *= 0.9;

			// Keep within bounds
			pos.x = Math.max(50, Math.min(width - 50, pos.x));
			pos.y = Math.max(50, Math.min(height - 50, pos.y));
		}

		if (iteration % 10 === 0) {
			onProgress?.((iteration / iterations) * 100);
		}
	}

	onProgress?.(100);

	const result: Record<string, { x: number; y: number }> = {};
	for (const [nodeId, pos] of positions) {
		result[nodeId] = { x: pos.x, y: pos.y };
	}

	return {
		positions: result,
		size: { height, width },
	};
}

/**
 * Grid layout (fallback for unsupported layouts)
 */
function layoutGrid(
	nodes: LayoutNode[],
	_edges: LayoutEdge[],
	options: LayoutOptions,
	onProgress?: ProgressCallback,
): LayoutResult {
	onProgress?.(0);

	const positions: Record<string, { x: number; y: number }> = {};
	const perRow = Math.ceil(Math.sqrt(nodes.length));
	const nodeSep = options.nodeSep ?? 60;
	const marginX = options.marginX ?? 40;
	const marginY = options.marginY ?? 40;

	let maxWidth = 0;
	let maxHeight = 0;

	nodes.forEach((node, i) => {
		const col = i % perRow;
		const row = Math.floor(i / perRow);

		const x = marginX + col * (node.width + nodeSep);
		const y = marginY + row * (node.height + nodeSep);

		positions[node.id] = { x, y };
		maxWidth = Math.max(maxWidth, x + node.width + marginX);
		maxHeight = Math.max(maxHeight, y + node.height + marginY);

		if (i % 10 === 0) {
			onProgress?.((i / nodes.length) * 100);
		}
	});

	onProgress?.(100);

	return {
		positions,
		size: { height: maxHeight, width: maxWidth },
	};
}

/**
 * Main layout function
 */
function computeLayout(
	nodes: LayoutNode[],
	edges: LayoutEdge[],
	options: LayoutOptions,
	onProgress?: ProgressCallback,
): LayoutResult {
	if (nodes.length === 0) {
		return { positions: {}, size: { height: 0, width: 0 } };
	}

	switch (options.type) {
		case "dagre":
		case "hierarchical":
		case "elk": {
			return layoutDagre(nodes, edges, options, onProgress);
		}
		case "force": {
			return layoutForce(nodes, edges, options, onProgress);
		}
		default: {
			return layoutGrid(nodes, edges, options, onProgress);
		}
	}
}

// Worker API
const api = {
	computeLayout,
};

expose(api);

export type GraphLayoutWorkerAPI = typeof api;
