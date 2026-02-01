/**
 * Example usage of useViewportGraph hook
 *
 * This demonstrates progressive graph loading for large datasets.
 */

import { useCallback, useState } from "react";
import ReactFlow, {
	ReactFlowProvider,
	useReactFlow,
	type OnViewportChange,
} from "@xyflow/react";
import { useViewportGraph } from "./useViewportGraph";

/**
 * Example 1: Basic viewport-based loading
 */
export function BasicViewportGraphExample({ projectId }: { projectId: string }) {
	// Initialize the viewport graph hook
	const { nodes, edges, loadViewport, isLoading, totalCount, hasMore } =
		useViewportGraph(projectId);

	// Get React Flow instance for viewport tracking
	const reactFlowInstance = useReactFlow();

	// Handle viewport changes (pan/zoom)
	const handleViewportChange = useCallback<OnViewportChange>(
		(viewport) => {
			// Extract viewport bounds from React Flow
			const { x, y, zoom } = viewport;
			const { width, height } = reactFlowInstance.getSize();

			// Calculate visible area in graph coordinates
			const minX = -x / zoom;
			const minY = -y / zoom;
			const maxX = minX + width / zoom;
			const maxY = minY + height / zoom;

			// Load data for this viewport
			loadViewport({ minX, minY, maxX, maxY, zoom });
		},
		[reactFlowInstance, loadViewport],
	);

	return (
		<div style={{ width: "100%", height: "600px" }}>
			<ReactFlow
				nodes={nodes}
				edges={edges}
				onMove={handleViewportChange}
				fitView
			>
				{isLoading && (
					<div
						style={{
							position: "absolute",
							top: 16,
							right: 16,
							padding: "8px 16px",
							background: "rgba(0,0,0,0.8)",
							color: "white",
							borderRadius: 4,
						}}
					>
						Loading region...
					</div>
				)}
				<div
					style={{
						position: "absolute",
						top: 16,
						left: 16,
						padding: "8px 16px",
						background: "rgba(0,0,0,0.7)",
						color: "white",
						borderRadius: 4,
					}}
				>
					<div>Loaded: {nodes.length} / {totalCount} nodes</div>
					<div style={{ fontSize: "0.8em", marginTop: 4 }}>
						{hasMore.north && "⬆️ "}
						{hasMore.south && "⬇️ "}
						{hasMore.east && "➡️ "}
						{hasMore.west && "⬅️ "}
						{!hasMore.north && !hasMore.south && !hasMore.east && !hasMore.west && "✓ All loaded"}
					</div>
				</div>
			</ReactFlow>
		</div>
	);
}

/**
 * Example 2: With region loading callback
 */
export function ViewportGraphWithCallbackExample({
	projectId,
}: {
	projectId: string;
}) {
	// Track loading stats
	const [_stats, setStats] = useState({
		regionsLoaded: 0,
		totalNodes: 0,
		totalEdges: 0,
	});

	const { nodes, edges, _loadViewport, loadedRegionCount } = useViewportGraph(
		projectId,
		{
			bufferPx: 1000, // Larger buffer for smoother panning
			onRegionLoaded: (regionKey, nodeCount, edgeCount) => {
				logger.info(
					`Loaded region ${regionKey}: ${nodeCount} nodes, ${edgeCount} edges`,
				);
				setStats((prev) => ({
					regionsLoaded: prev.regionsLoaded + 1,
					totalNodes: prev.totalNodes + nodeCount,
					totalEdges: prev.totalEdges + edgeCount,
				}));
			},
		},
	);

	return (
		<div>
			<div
				style={{
					padding: 16,
					background: "#f5f5f5",
					borderBottom: "1px solid #ddd",
				}}
			>
				<h3>Loading Statistics</h3>
				<p>Regions loaded: {loadedRegionCount}</p>
				<p>Total nodes: {nodes.length}</p>
				<p>Total edges: {edges.length}</p>
			</div>
			<div style={{ width: "100%", height: "600px" }}>
				<ReactFlow nodes={nodes} edges={edges} fitView />
			</div>
		</div>
	);
}

/**
 * Example 3: Manual viewport loading
 */
export function ManualViewportLoadExample({ projectId }: { projectId: string }) {
	const { nodes, edges, loadViewport, isLoading, hasMore } =
		useViewportGraph(projectId);

	const handleLoadMore = (direction: "north" | "south" | "east" | "west") => {
		// Get current viewport bounds
		const reactFlow = useReactFlow();
		const viewport = reactFlow.getViewport();
		const { width, height } = reactFlow.getSize();

		const { x, y, zoom } = viewport;
		let minX = -x / zoom;
		let minY = -y / zoom;
		let maxX = minX + width / zoom;
		let maxY = minY + height / zoom;

		// Shift viewport in the specified direction
		const shift = 2000; // 2000px shift
		switch (direction) {
			case "north":
				minY -= shift;
				maxY -= shift;
				break;
			case "south":
				minY += shift;
				maxY += shift;
				break;
			case "east":
				minX += shift;
				maxX += shift;
				break;
			case "west":
				minX -= shift;
				maxX -= shift;
				break;
		}

		loadViewport({ minX, minY, maxX, maxY, zoom });
	};

	return (
		<div>
			<div style={{ padding: 16, display: "flex", gap: 8 }}>
				<button
					onClick={() => handleLoadMore("north")}
					disabled={!hasMore.north || isLoading}
				>
					Load North ⬆️
				</button>
				<button
					onClick={() => handleLoadMore("south")}
					disabled={!hasMore.south || isLoading}
				>
					Load South ⬇️
				</button>
				<button
					onClick={() => handleLoadMore("east")}
					disabled={!hasMore.east || isLoading}
				>
					Load East ➡️
				</button>
				<button
					onClick={() => handleLoadMore("west")}
					disabled={!hasMore.west || isLoading}
				>
					Load West ⬅️
				</button>
			</div>
			<div style={{ width: "100%", height: "600px" }}>
				<ReactFlow nodes={nodes} edges={edges} fitView />
			</div>
		</div>
	);
}

/**
 * Example 4: Wrapper component with provider
 */
export function ViewportGraphWrapper({ projectId }: { projectId: string }) {
	return (
		<ReactFlowProvider>
			<BasicViewportGraphExample projectId={projectId} />
		</ReactFlowProvider>
	);
}

/**
 * Performance Notes:
 *
 * 1. Buffer Size:
 *    - bufferPx=500 (default): Good for most cases
 *    - bufferPx=1000: Better for rapid panning
 *    - bufferPx=200: Minimal memory usage
 *
 * 2. Region Grid Size:
 *    - Currently fixed at 500px
 *    - Smaller grids = more API calls, finer granularity
 *    - Larger grids = fewer API calls, coarser granularity
 *
 * 3. Auto-loading:
 *    - Initial viewport loads on mount
 *    - Centered at (-1000, -1000) to (1000, 1000)
 *    - No manual intervention needed for first render
 *
 * 4. Network Optimization:
 *    - Duplicate region requests are prevented
 *    - In-flight requests are tracked
 *    - Failed loads can be retried (region not marked as loaded)
 *
 * 5. Directional hasMore:
 *    - north/south/east/west indicators
 *    - Use to show "load more" buttons
 *    - Automatically updated on each load
 */
