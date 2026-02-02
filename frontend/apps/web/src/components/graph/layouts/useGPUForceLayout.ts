/**
 * React Hook for GPU-Accelerated Force-Directed Layout
 *
 * Features:
 * - Automatic Web Worker execution for >1000 nodes
 * - Smooth spring animations for layout transitions
 * - Progress tracking
 * - Performance metrics
 */

import type { Edge, Node } from "@xyflow/react";
import { useCallback, useEffect, useRef, useState } from "react";
import type {
	ForceLayoutRequest,
	ForceLayoutResponse,
	ForceLayoutProgress,
	ForceLayoutError,
} from "./gpuForceLayout.worker";
import type { ForceSimulationConfig } from "./gpuForceLayout";
import { getGPUForceLayout } from "./gpuForceLayout";

// ============================================================================
// CONFIGURATION
// ============================================================================

const WORKER_THRESHOLD = 1000; // Use worker for graphs with >1000 nodes
const ANIMATION_DURATION = 800; // ms for layout transition animation

// ============================================================================
// TYPES
// ============================================================================

export interface UseGPUForceLayoutOptions {
	enabled?: boolean;
	animateTransitions?: boolean;
	animationDuration?: number;
	config?: ForceSimulationConfig;
}

export interface GPUForceLayoutState {
	isComputing: boolean;
	progress: number;
	duration: number | null;
	error: string | null;
}

// ============================================================================
// HOOK IMPLEMENTATION
// ============================================================================

export function useGPUForceLayout<T extends Record<string, unknown>>(
	nodes: Node<T>[],
	edges: Edge[],
	options: UseGPUForceLayoutOptions = {},
) {
	const {
		enabled = true,
		animateTransitions = true,
		animationDuration = ANIMATION_DURATION,
		config = {},
	} = options;

	const [layoutedNodes, setLayoutedNodes] = useState<Node<T>[]>(nodes);
	const [state, setState] = useState<GPUForceLayoutState>({
		isComputing: false,
		progress: 0,
		duration: null,
		error: null,
	});

	const workerRef = useRef<Worker | null>(null);
	const animationFrameRef = useRef<number | null>(null);
	const prevSignatureRef = useRef<string>("");

	// Cleanup worker on unmount
	useEffect(() => {
		return () => {
			if (workerRef.current) {
				workerRef.current.terminate();
				workerRef.current = null;
			}
			if (animationFrameRef.current) {
				cancelAnimationFrame(animationFrameRef.current);
			}
		};
	}, []);

	/**
	 * Animate transition from old positions to new positions
	 */
	const animateLayout = useCallback(
		(
			oldNodes: Node<T>[],
			newNodes: Node<T>[],
			duration: number,
		): Promise<void> => {
			return new Promise((resolve) => {
				if (!animateTransitions) {
					setLayoutedNodes(newNodes);
					resolve();
					return;
				}

				const startTime = performance.now();
				const oldPosMap = new Map(
					oldNodes.map((n) => [n.id, n.position]),
				);
				const newPosMap = new Map(
					newNodes.map((n) => [n.id, n.position]),
				);

				const animate = (currentTime: number) => {
					const elapsed = currentTime - startTime;
					const progress = Math.min(elapsed / duration, 1);

					// Ease-out cubic
					const eased = 1 - Math.pow(1 - progress, 3);

					const interpolatedNodes = newNodes.map((node) => {
						const oldPos = oldPosMap.get(node.id) || node.position;
						const newPos = newPosMap.get(node.id) || node.position;

						return {
							...node,
							position: {
								x: oldPos.x + (newPos.x - oldPos.x) * eased,
								y: oldPos.y + (newPos.y - oldPos.y) * eased,
							},
						};
					});

					setLayoutedNodes(interpolatedNodes);

					if (progress < 1) {
						animationFrameRef.current = requestAnimationFrame(animate);
					} else {
						resolve();
					}
				};

				animationFrameRef.current = requestAnimationFrame(animate);
			});
		},
		[animateTransitions],
	);

	/**
	 * Run layout in Web Worker
	 */
	const runInWorker = useCallback(
		(inputNodes: Node<T>[], inputEdges: Edge[]): Promise<Node<T>[]> => {
			return new Promise((resolve, reject) => {
				if (typeof Worker === "undefined") {
					reject(new Error("Web Workers not supported"));
					return;
				}

				// Create worker
				const worker = new Worker(
					new URL("./gpuForceLayout.worker.ts", import.meta.url),
					{ type: "module" },
				);

				workerRef.current = worker;

				// Handle messages
				const onMessage = (
					ev: MessageEvent<
						ForceLayoutResponse | ForceLayoutProgress | ForceLayoutError
					>,
				) => {
					if (ev.data.type === "result") {
						worker.terminate();
						workerRef.current = null;

						const positionMap = new Map(
							ev.data.positions.map((p) => [p.id, { x: p.x, y: p.y }]),
						);

						const result = inputNodes.map((node) => {
							const pos = positionMap.get(node.id);
							if (!pos) return node;
							return { ...node, position: pos };
						});

						setState((prev) => ({
							...prev,
							duration: ev.data.duration,
							isComputing: false,
						}));

						resolve(result);
					} else if (ev.data.type === "progress") {
						setState((prev) => ({
							...prev,
							progress: ev.data.progress,
						}));
					} else if (ev.data.type === "error") {
						worker.terminate();
						workerRef.current = null;

						setState((prev) => ({
							...prev,
							error: ev.data.error,
							isComputing: false,
						}));

						reject(new Error(ev.data.error));
					}
				};

				worker.addEventListener("message", onMessage);

				worker.addEventListener("error", (err) => {
					worker.terminate();
					workerRef.current = null;

					setState((prev) => ({
						...prev,
						error: err.message || "Worker error",
						isComputing: false,
					}));

					reject(new Error(err.message || "Worker error"));
				});

				// Send request
				const request: ForceLayoutRequest = {
					type: "simulate",
					nodes: inputNodes.map((n) => ({ id: n.id })),
					edges: inputEdges.map((e) => ({
						id: e.id,
						source: e.source,
						target: e.target,
					})),
					config,
				};

				worker.postMessage(request, worker.location.origin);
			});
		},
		[config],
	);

	/**
	 * Run layout on main thread
	 */
	const runOnMainThread = useCallback(
		async (inputNodes: Node<T>[], inputEdges: Edge[]): Promise<Node<T>[]> => {
			const startTime = performance.now();
			const layoutEngine = getGPUForceLayout();

			const result = await layoutEngine.simulate(
				inputNodes,
				inputEdges,
				config,
			);

			const duration = performance.now() - startTime;

			setState((prev) => ({
				...prev,
				duration,
				isComputing: false,
			}));

			return result;
		},
		[config],
	);

	/**
	 * Calculate layout (main entry point)
	 */
	const calculateLayout = useCallback(
		async (inputNodes: Node<T>[], inputEdges: Edge[]): Promise<Node<T>[]> => {
			if (!enabled || inputNodes.length === 0) {
				return inputNodes;
			}

			setState({
				isComputing: true,
				progress: 0,
				duration: null,
				error: null,
			});

			try {
				// Use worker for large graphs
				const result =
					inputNodes.length > WORKER_THRESHOLD
						? await runInWorker(inputNodes, inputEdges)
						: await runOnMainThread(inputNodes, inputEdges);

				return result;
			} catch (err) {
				console.error("GPU force layout failed:", err);

				setState((prev) => ({
					...prev,
					error: err instanceof Error ? err.message : String(err),
					isComputing: false,
				}));

				// Return original nodes on error
				return inputNodes;
			}
		},
		[enabled, runInWorker, runOnMainThread],
	);

	/**
	 * Auto-calculate layout when inputs change
	 */
	useEffect(() => {
		if (!enabled) {
			setLayoutedNodes(nodes);
			return;
		}

		// Create signature to detect changes
		const signature = `${nodes.length}|${edges.length}|${nodes
			.map((n) => n.id)
			.join(",")}`;

		if (signature === prevSignatureRef.current) {
			return;
		}

		prevSignatureRef.current = signature;

		if (nodes.length === 0) {
			setLayoutedNodes([]);
			return;
		}

		// Calculate new layout
		const oldNodes = layoutedNodes.length > 0 ? layoutedNodes : nodes;

		void calculateLayout(nodes, edges).then((newNodes) => {
			if (animateTransitions && oldNodes.length === newNodes.length) {
				void animateLayout(oldNodes, newNodes, animationDuration);
			} else {
				setLayoutedNodes(newNodes);
			}
		});
	}, [
		enabled,
		nodes,
		edges,
		calculateLayout,
		animateLayout,
		animationDuration,
		animateTransitions,
	]);

	return {
		nodes: layoutedNodes,
		...state,
		calculateLayout,
	};
}

export default useGPUForceLayout;
