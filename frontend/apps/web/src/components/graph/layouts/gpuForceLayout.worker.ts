/**
 * Web Worker for GPU Force-Directed Layout
 *
 * Runs force simulation off the main thread to keep UI responsive.
 * Uses Barnes-Hut optimization for O(n log n) complexity.
 */

import type { Edge, Node } from "@xyflow/react";
import {
	type ForceSimulationConfig,
	GPUForceLayout,
} from "./gpuForceLayout";

// ============================================================================
// MESSAGE TYPES
// ============================================================================

export interface ForceLayoutRequest {
	type: "simulate";
	nodes: Array<{ id: string }>;
	edges: Array<{ id: string; source: string; target: string }>;
	config: ForceSimulationConfig;
}

export interface ForceLayoutResponse {
	type: "result";
	positions: Array<{ id: string; x: number; y: number }>;
	duration: number;
}

export interface ForceLayoutProgress {
	type: "progress";
	iteration: number;
	totalIterations: number;
	progress: number;
}

export interface ForceLayoutError {
	type: "error";
	error: string;
}

// ============================================================================
// WORKER IMPLEMENTATION
// ============================================================================

const layoutEngine = new GPUForceLayout();

self.addEventListener("message", async (ev: MessageEvent<ForceLayoutRequest>) => {
	const msg = ev.data;

	if (msg.type !== "simulate") {
		return;
	}

	const startTime = performance.now();

	try {
		// Convert minimal node data back to full Node objects
		const nodes: Node[] = msg.nodes.map((n) => ({
			id: n.id,
			type: "default",
			position: { x: 0, y: 0 },
			data: {},
		}));

		const edges: Edge[] = msg.edges.map((e) => ({
			id: e.id,
			source: e.source,
			target: e.target,
		}));

		// Run simulation
		const result = await layoutEngine.simulate(nodes, edges, msg.config);

		// Extract positions
		const positions = result.map((node) => ({
			id: node.id,
			x: node.position.x,
			y: node.position.y,
		}));

		const duration = performance.now() - startTime;

		// Send result back to main thread
		const response: ForceLayoutResponse = {
			type: "result",
			positions,
			duration,
		};

		(self as unknown as Worker).postMessage(response, self.location.origin);
	} catch (err) {
		const errorResponse: ForceLayoutError = {
			type: "error",
			error: err instanceof Error ? err.message : String(err),
		};

		(self as unknown as Worker).postMessage(errorResponse, self.location.origin);
	}
});

// Handle cleanup
self.addEventListener("error", (err) => {
	const errorResponse: ForceLayoutError = {
		type: "error",
		error: err.message || "Worker error occurred",
	};

	(self as unknown as Worker).postMessage(errorResponse, self.location.origin);
});
