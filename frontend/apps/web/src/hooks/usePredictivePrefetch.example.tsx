/**
 * Example integrations for usePredictivePrefetch hook
 *
 * This file demonstrates how to integrate predictive prefetching
 * with existing graph components and caching systems.
 */

import { useCallback, useEffect, useState } from "react";
import { graphCache } from "@/lib/graphCache";
import { logger } from "@/lib/logger";
import {
	usePredictivePrefetch,
	viewportToCacheKey,
} from "./usePredictivePrefetch";
import type { PredictedViewport, Viewport } from "./usePredictivePrefetch";

/**
 * Example 1: Basic Integration with Graph View
 *
 * Simple integration that prefetches nodes for predicted viewport
 */
export function ExampleBasicGraphView() {
	const [viewport, setViewport] = useState<Viewport>({
		height: 900,
		width: 1200,
		x: 0,
		y: 0,
		zoom: 1,
	});

	const loadViewportData = useCallback(async (predicted: PredictedViewport) => {
		// Check cache first
		const cacheKey = viewportToCacheKey(predicted);
		const cached = graphCache.get(cacheKey);

		if (cached) {
			logger.info("Using cached data for predicted viewport");
			return;
		}

		// Fetch data for predicted viewport
		logger.info("Prefetching data for:", predicted);
		const data = await fetchGraphData(predicted);

		// Cache the result
		graphCache.set(cacheKey, data);
	}, []);

	const { isPredicting, speed, predictedViewport } = usePredictivePrefetch({
		enabled: true,
		loadViewport: loadViewportData,
		predictionHorizon: 500,
		velocityThreshold: 15,
		viewport,
	});

	return (
		<div>
			<div className="debug-info">
				<p>Speed: {speed.toFixed(2)} px/frame</p>
				<p>Predicting: {isPredicting ? "Yes" : "No"}</p>
				{predictedViewport && (
					<p>
						Predicted: ({predictedViewport.minX.toFixed(0)},{" "}
						{predictedViewport.minY.toFixed(0)})
					</p>
				)}
			</div>

			{/* Your graph component */}
			<div
				className="graph-container"
				onScroll={(e) => {
					const target = e.target as HTMLDivElement;
					setViewport((prev) => ({
						...prev,
						x: target.scrollLeft,
						y: target.scrollTop,
					}));
				}}
			>
				{/* Graph content */}
			</div>
		</div>
	);
}

/**
 * Example 2: Integration with ReactFlow
 *
 * Shows how to integrate with ReactFlow's viewport system
 */
export function ExampleReactFlowIntegration() {
	const [reactFlowInstance, _setReactFlowInstance] = useState<any>(null);
	const [viewport, _setViewport] = useState<Viewport>({
		height: 0,
		width: 0,
		x: 0,
		y: 0,
		zoom: 1,
	});

	// Update viewport from ReactFlow
	useEffect(() => {
		if (!reactFlowInstance) {
			return;
		}

		const updateViewport = () => {
			const rfViewport = reactFlowInstance.getViewport();
			const bounds = reactFlowInstance.getBounds();

			_setViewport({
				height: bounds.height,
				width: bounds.width,
				x: -rfViewport.x / rfViewport.zoom,
				y: -rfViewport.y / rfViewport.zoom,
				zoom: rfViewport.zoom,
			});
		};

		updateViewport();
		reactFlowInstance.on("move", updateViewport);

		return () => {
			reactFlowInstance.off("move", updateViewport);
		};
	}, [reactFlowInstance]);

	const loadViewportNodes = useCallback(
		async (predicted: PredictedViewport) => {
			// Generate cache key
			const cacheKey = viewportToCacheKey(predicted);

			// Check if already cached
			if (graphCache.has(cacheKey)) {
				return;
			}

			// Fetch nodes that would be visible in predicted viewport
			const nodes = await fetchNodesInBounds(predicted);

			// Cache the nodes
			graphCache.set(cacheKey, nodes);

			// Optionally preload images/assets for those nodes
			await preloadNodeAssets(nodes);
		},
		[],
	);

	usePredictivePrefetch({
		debounceDelay: 150,
		enabled: true,
		loadViewport: loadViewportNodes,
		predictionHorizon: 600,
		velocityThreshold: 20,
		viewport,
	});

	return (
		<div>
			{/* ReactFlow component */}
			{/* <ReactFlow onInit={setReactFlowInstance} ... /> */}
		</div>
	);
}

/**
 * Example 3: Adaptive Prefetching with Performance Monitoring
 *
 * Adjusts prediction horizon based on system performance
 */
export function ExampleAdaptivePrefetching() {
	const [viewport, _setViewport] = useState<Viewport>({
		height: 900,
		width: 1200,
		x: 0,
		y: 0,
		zoom: 1,
	});

	const [predictionHorizon, setPredictionHorizon] = useState(500);
	const [fps, setFps] = useState(60);

	// Monitor FPS
	useEffect(() => {
		let lastTime = performance.now();
		let frames = 0;

		const measureFps = () => {
			frames += 1;
			const now = performance.now();
			const elapsed = now - lastTime;

			if (elapsed >= 1000) {
				const currentFps = (frames * 1000) / elapsed;
				setFps(currentFps);
				frames = 0;
				lastTime = now;

				// Adapt prediction horizon based on FPS
				if (currentFps < 30) {
					// Low FPS: reduce prediction horizon to save resources
					setPredictionHorizon(300);
				} else if (currentFps > 50) {
					// High FPS: increase prediction horizon for smoother experience
					setPredictionHorizon(700);
				} else {
					setPredictionHorizon(500);
				}
			}

			requestAnimationFrame(measureFps);
		};

		const rafId = requestAnimationFrame(measureFps);
		return () => cancelAnimationFrame(rafId);
	}, []);

	const loadViewportData = useCallback(async (predicted: PredictedViewport) => {
		const cacheKey = viewportToCacheKey(predicted);

		if (!graphCache.has(cacheKey)) {
			const data = await fetchGraphData(predicted);
			graphCache.set(cacheKey, data);
		}
	}, []);

	const { isPredicting } = usePredictivePrefetch({
		enabled: true,
		loadViewport: loadViewportData,
		predictionHorizon,
		velocityThreshold: 15,
		viewport,
	});

	return (
		<div>
			<div className="performance-info">
				<p>FPS: {fps.toFixed(1)}</p>
				<p>Prediction Horizon: {predictionHorizon}ms</p>
				<p>Prefetching: {isPredicting ? "Active" : "Idle"}</p>
			</div>
		</div>
	);
}

/**
 * Example 4: Multi-layer Prefetching
 *
 * Prefetches different data types at different horizons
 */
export function ExampleMultiLayerPrefetching() {
	const [viewport, _setViewport] = useState<Viewport>({
		height: 900,
		width: 1200,
		x: 0,
		y: 0,
		zoom: 1,
	});

	// Near-horizon: Prefetch node details
	const loadNearData = useCallback(async (predicted: PredictedViewport) => {
		const cacheKey = `near:${viewportToCacheKey(predicted)}`;

		if (!graphCache.has(cacheKey)) {
			const nodeDetails = await fetchDetailedNodeData(predicted);
			graphCache.set(cacheKey, nodeDetails);
		}
	}, []);

	// Far-horizon: Prefetch basic node data only
	const loadFarData = useCallback(async (predicted: PredictedViewport) => {
		const cacheKey = `far:${viewportToCacheKey(predicted)}`;

		if (!graphCache.has(cacheKey)) {
			const basicNodes = await fetchBasicNodeData(predicted);
			graphCache.set(cacheKey, basicNodes);
		}
	}, []);

	// Near prefetch (300ms ahead)
	usePredictivePrefetch({
		loadViewport: loadNearData,
		predictionHorizon: 300,
		velocityThreshold: 15,
		viewport,
	});

	// Far prefetch (800ms ahead)
	usePredictivePrefetch({
		loadViewport: loadFarData,
		predictionHorizon: 800,
		velocityThreshold: 20,
		viewport, // Higher threshold for far prefetch
	});

	return <div>{/* Graph content */}</div>;
}

/**
 * Example 5: Directional Prefetching
 *
 * Prefetches more aggressively in the direction of movement
 */
export function ExampleDirectionalPrefetching() {
	const [viewport, _setViewport] = useState<Viewport>({
		height: 900,
		width: 1200,
		x: 0,
		y: 0,
		zoom: 1,
	});

	const loadDirectionalData = useCallback(
		async (predicted: PredictedViewport) => {
			// Expand bounds in direction of movement
			const deltaX = predicted.minX - viewport.x;
			const deltaY = predicted.minY - viewport.y;

			const expandedBounds: PredictedViewport = {
				maxX: deltaX > 0 ? predicted.maxX + 200 : predicted.maxX,
				maxY: deltaY > 0 ? predicted.maxY + 200 : predicted.maxY,
				minX: deltaX > 0 ? predicted.minX : predicted.minX - 200,
				minY: deltaY > 0 ? predicted.minY : predicted.minY - 200,
				zoom: predicted.zoom,
			};

			const cacheKey = viewportToCacheKey(expandedBounds);

			if (!graphCache.has(cacheKey)) {
				const data = await fetchGraphData(expandedBounds);
				graphCache.set(cacheKey, data);
			}
		},
		[viewport],
	);

	usePredictivePrefetch({
		loadViewport: loadDirectionalData,
		predictionHorizon: 500,
		velocityThreshold: 15,
		viewport,
	});

	return <div>{/* Graph content */}</div>;
}

// Mock API functions (replace with actual implementations)
async function fetchGraphData(_predicted: PredictedViewport): Promise<any> {
	// Simulate API call
	await new Promise((resolve) => setTimeout(resolve, 100));
	return { edges: [], nodes: [] };
}

async function fetchNodesInBounds(_bounds: PredictedViewport): Promise<any[]> {
	await new Promise((resolve) => setTimeout(resolve, 50));
	return [];
}

async function preloadNodeAssets(_nodes: any[]): Promise<void> {
	await new Promise((resolve) => setTimeout(resolve, 50));
}

async function fetchDetailedNodeData(
	_predicted: PredictedViewport,
): Promise<any> {
	await new Promise((resolve) => setTimeout(resolve, 80));
	return { detailedNodes: [] };
}

async function fetchBasicNodeData(_predicted: PredictedViewport): Promise<any> {
	await new Promise((resolve) => setTimeout(resolve, 30));
	return { basicNodes: [] };
}
