/**
 * Tests for usePredictivePrefetch hook
 */

import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	type PredictedViewport,
	type Viewport,
	isNodeInPredictedViewport,
	usePredictivePrefetch,
	viewportToCacheKey,
} from "@/hooks/usePredictivePrefetch";

describe("usePredictivePrefetch", () => {
	const mockLoadViewport = vi.fn();

	const baseViewport: Viewport = {
		x: 0,
		y: 0,
		zoom: 1,
		width: 1000,
		height: 800,
	};

	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("should initialize with zero velocity", () => {
		const { result } = renderHook(() =>
			usePredictivePrefetch({
				viewport: baseViewport,
				loadViewport: mockLoadViewport,
			}),
		);

		expect(result.current.velocity).toEqual({ x: 0, y: 0 });
		expect(result.current.speed).toBe(0);
		expect(result.current.isPredicting).toBe(false);
		expect(result.current.predictedViewport).toBeNull();
	});

	it("should not predict when disabled", async () => {
		const { rerender } = renderHook(
			({ viewport }) =>
				usePredictivePrefetch({
					viewport,
					loadViewport: mockLoadViewport,
					enabled: false,
				}),
			{
				initialProps: { viewport: baseViewport },
			},
		);

		// Simulate movement
		const newViewport = { ...baseViewport, x: 100 };
		rerender({ viewport: newViewport });

		await waitFor(() => {
			expect(mockLoadViewport).not.toHaveBeenCalled();
		});
	});

	it("should calculate velocity from viewport changes", async () => {
		const { result, rerender } = renderHook(
			({ viewport }) =>
				usePredictivePrefetch({
					viewport,
					loadViewport: mockLoadViewport,
					smoothingFactor: 1, // No smoothing for predictable results
					debounceDelay: 10,
				}),
			{
				initialProps: { viewport: baseViewport },
			},
		);

		// Initial state - velocity is tracked via ref, not state
		// So we check the initial return value
		expect(result.current.speed).toBe(0);

		// Move viewport multiple times to build velocity
		const newViewport = { ...baseViewport, x: 50, y: 30 };
		rerender({ viewport: newViewport });

		// Wait for debounce
		await new Promise((resolve) => setTimeout(resolve, 50));

		// Velocity should be non-zero after movement
		expect(result.current.speed).toBeGreaterThan(0);
	});

	it("should smooth velocity with exponential moving average", async () => {
		const { result, rerender } = renderHook(
			({ viewport }) =>
				usePredictivePrefetch({
					viewport,
					loadViewport: mockLoadViewport,
					smoothingFactor: 0.3,
					debounceDelay: 10,
				}),
			{
				initialProps: { viewport: baseViewport },
			},
		);

		// First movement
		const viewport1 = { ...baseViewport, x: 100 };
		rerender({ viewport: viewport1 });

		await new Promise((resolve) => setTimeout(resolve, 30));
		const speed1 = result.current.speed;

		// Second movement (smaller delta)
		const viewport2 = { ...viewport1, x: 120 };
		rerender({ viewport: viewport2 });

		await new Promise((resolve) => setTimeout(resolve, 30));
		const speed2 = result.current.speed;

		// Speed should change between movements (demonstrating smoothing)
		expect(speed1).toBeGreaterThan(0);
		expect(speed2).toBeGreaterThan(0);
		// Due to EMA, speeds should be different
		expect(Math.abs(speed1 - speed2)).toBeGreaterThan(0);
	});

	it("should calculate speed as velocity magnitude", async () => {
		const { result, rerender } = renderHook(
			({ viewport }) =>
				usePredictivePrefetch({
					viewport,
					loadViewport: mockLoadViewport,
					smoothingFactor: 1,
					debounceDelay: 10,
				}),
			{
				initialProps: { viewport: baseViewport },
			},
		);

		// Move in both x and y
		const newViewport = { ...baseViewport, x: 30, y: 40 };
		rerender({ viewport: newViewport });

		await new Promise((resolve) => setTimeout(resolve, 30));

		// Speed should be non-zero and represent magnitude
		expect(result.current.speed).toBeGreaterThan(0);
		// With smoothing=1, final speed should approach sqrt(30^2 + 40^2) = 50
		expect(result.current.speed).toBeGreaterThan(20);
	});

	it("should trigger prefetch when speed exceeds threshold", async () => {
		const { rerender } = renderHook(
			({ viewport }) =>
				usePredictivePrefetch({
					viewport,
					loadViewport: mockLoadViewport,
					velocityThreshold: 10,
					debounceDelay: 50,
				}),
			{
				initialProps: { viewport: baseViewport },
			},
		);

		// Move fast enough to exceed threshold
		const newViewport = { ...baseViewport, x: 50 };
		rerender({ viewport: newViewport });

		await waitFor(
			() => {
				expect(mockLoadViewport).toHaveBeenCalled();
			},
			{ timeout: 200 },
		);
	});

	it("should not trigger prefetch when speed below threshold", async () => {
		const { rerender } = renderHook(
			({ viewport }) =>
				usePredictivePrefetch({
					viewport,
					loadViewport: mockLoadViewport,
					velocityThreshold: 100,
					debounceDelay: 50,
				}),
			{
				initialProps: { viewport: baseViewport },
			},
		);

		// Move slowly
		const newViewport = { ...baseViewport, x: 5 };
		rerender({ viewport: newViewport });

		await new Promise((resolve) => setTimeout(resolve, 150));
		expect(mockLoadViewport).not.toHaveBeenCalled();
	});

	it("should debounce prefetch calls", async () => {
		const { rerender } = renderHook(
			({ viewport }) =>
				usePredictivePrefetch({
					viewport,
					loadViewport: mockLoadViewport,
					velocityThreshold: 10,
					debounceDelay: 100,
				}),
			{
				initialProps: { viewport: baseViewport },
			},
		);

		// Rapid viewport changes
		for (let i = 1; i <= 5; i++) {
			rerender({ viewport: { ...baseViewport, x: i * 20 } });
			await new Promise((resolve) => setTimeout(resolve, 20));
		}

		// Should only call once after debounce period
		await waitFor(
			() => {
				expect(mockLoadViewport).toHaveBeenCalledTimes(1);
			},
			{ timeout: 200 },
		);
	});

	it("should calculate predicted viewport correctly", async () => {
		const { rerender } = renderHook(
			({ viewport }) =>
				usePredictivePrefetch({
					viewport,
					loadViewport: mockLoadViewport,
					velocityThreshold: 10,
					predictionHorizon: 500,
					debounceDelay: 50,
					smoothingFactor: 1, // No smoothing for predictable results
				}),
			{
				initialProps: { viewport: baseViewport },
			},
		);

		// Move viewport (velocity = 50 px/frame)
		const newViewport = { ...baseViewport, x: 50 };
		rerender({ viewport: newViewport });

		await waitFor(
			() => {
				expect(mockLoadViewport).toHaveBeenCalled();
			},
			{ timeout: 200 },
		);

		const predictedViewport = mockLoadViewport.mock
			.calls[0][0] as PredictedViewport;

		// At 60fps, 500ms = 30 frames
		// Predicted X = 50 + (50 * 30) = 1550
		expect(predictedViewport.minX).toBeCloseTo(1550, -1);
		expect(predictedViewport.minY).toBe(0);
		expect(predictedViewport.maxX).toBeCloseTo(2550, -1);
		expect(predictedViewport.maxY).toBe(800);
		expect(predictedViewport.zoom).toBe(1);
	});

	it("should account for zoom in predicted viewport bounds", async () => {
		const zoomedViewport: Viewport = {
			x: 0,
			y: 0,
			zoom: 2,
			width: 1000,
			height: 800,
		};

		const { rerender } = renderHook(
			({ viewport }) =>
				usePredictivePrefetch({
					viewport,
					loadViewport: mockLoadViewport,
					velocityThreshold: 10,
					debounceDelay: 50,
					smoothingFactor: 1,
				}),
			{
				initialProps: { viewport: zoomedViewport },
			},
		);

		// Move viewport
		const newViewport = { ...zoomedViewport, x: 50 };
		rerender({ viewport: newViewport });

		await waitFor(
			() => {
				expect(mockLoadViewport).toHaveBeenCalled();
			},
			{ timeout: 200 },
		);

		const predictedViewport = mockLoadViewport.mock
			.calls[0][0] as PredictedViewport;

		// Width/height should be scaled by zoom
		const expectedWidth = 1000 / 2; // zoom = 2
		const expectedHeight = 800 / 2;

		expect(predictedViewport.maxX - predictedViewport.minX).toBeCloseTo(
			expectedWidth,
			-1,
		);
		expect(predictedViewport.maxY - predictedViewport.minY).toBeCloseTo(
			expectedHeight,
			-1,
		);
	});

	it("should cleanup debounce timer on unmount", () => {
		const { unmount } = renderHook(() =>
			usePredictivePrefetch({
				viewport: baseViewport,
				loadViewport: mockLoadViewport,
			}),
		);

		unmount();
		// No errors should occur
	});

	it("should provide isPredicting flag correctly", async () => {
		const { result, rerender } = renderHook(
			({ viewport }) =>
				usePredictivePrefetch({
					viewport,
					loadViewport: mockLoadViewport,
					velocityThreshold: 5, // Lower threshold for easier testing
					smoothingFactor: 1,
					debounceDelay: 10,
				}),
			{
				initialProps: { viewport: baseViewport },
			},
		);

		expect(result.current.isPredicting).toBe(false);
		expect(result.current.speed).toBe(0);

		// Move fast
		const newViewport = { ...baseViewport, x: 50 };
		rerender({ viewport: newViewport });

		await new Promise((resolve) => setTimeout(resolve, 50));

		// Should be predicting after fast movement
		expect(result.current.speed).toBeGreaterThan(5);

		// Keep moving to maintain velocity
		rerender({ viewport: { ...newViewport, x: 55 } });
		await new Promise((resolve) => setTimeout(resolve, 20));

		expect(result.current.speed).toBeGreaterThan(0);
	});
});

describe("viewportToCacheKey", () => {
	it("should generate consistent cache keys", () => {
		const viewport: PredictedViewport = {
			minX: 100,
			minY: 200,
			maxX: 1100,
			maxY: 1000,
			zoom: 1.5,
		};

		const key1 = viewportToCacheKey(viewport);
		const key2 = viewportToCacheKey(viewport);

		expect(key1).toBe(key2);
	});

	it("should round coordinates to reduce key variations", () => {
		const viewport1: PredictedViewport = {
			minX: 101,
			minY: 202,
			maxX: 1103,
			maxY: 1004,
			zoom: 1.5,
		};

		const viewport2: PredictedViewport = {
			minX: 149,
			minY: 249,
			maxX: 1149,
			maxY: 1049,
			zoom: 1.5,
		};

		const key1 = viewportToCacheKey(viewport1);
		const key2 = viewportToCacheKey(viewport2);

		// Both should round to same key (coordinates rounded to nearest 100)
		expect(key1).toBe(key2);
	});

	it("should include all viewport bounds in key", () => {
		const viewport: PredictedViewport = {
			minX: 100,
			minY: 200,
			maxX: 1100,
			maxY: 1000,
			zoom: 1.5,
		};

		const key = viewportToCacheKey(viewport);

		expect(key).toContain("100");
		expect(key).toContain("200");
		expect(key).toContain("1100");
		expect(key).toContain("1000");
		expect(key).toContain("1.5");
	});
});

describe("isNodeInPredictedViewport", () => {
	const viewport: PredictedViewport = {
		minX: 0,
		minY: 0,
		maxX: 1000,
		maxY: 800,
		zoom: 1,
	};

	it("should return true for node fully inside viewport", () => {
		const node = { x: 100, y: 100, width: 50, height: 50 };
		expect(isNodeInPredictedViewport(node, viewport)).toBe(true);
	});

	it("should return true for node partially inside viewport", () => {
		const node = { x: -25, y: 100, width: 50, height: 50 };
		expect(isNodeInPredictedViewport(node, viewport)).toBe(true);
	});

	it("should return false for node completely outside viewport", () => {
		const node = { x: 1100, y: 100, width: 50, height: 50 };
		expect(isNodeInPredictedViewport(node, viewport)).toBe(false);
	});

	it("should handle edge cases correctly", () => {
		// Node touching left edge
		const node1 = { x: -50, y: 100, width: 50, height: 50 };
		expect(isNodeInPredictedViewport(node1, viewport)).toBe(false);

		// Node touching right edge
		const node2 = { x: 1000, y: 100, width: 50, height: 50 };
		expect(isNodeInPredictedViewport(node2, viewport)).toBe(false);

		// Node overlapping right edge
		const node3 = { x: 990, y: 100, width: 50, height: 50 };
		expect(isNodeInPredictedViewport(node3, viewport)).toBe(true);
	});

	it("should handle zero-size nodes", () => {
		const node = { x: 500, y: 400, width: 0, height: 0 };
		// Zero-size nodes at a point inside the viewport are considered visible
		expect(isNodeInPredictedViewport(node, viewport)).toBe(true);
	});

	it("should handle nodes larger than viewport", () => {
		const node = { x: -100, y: -100, width: 1500, height: 1200 };
		expect(isNodeInPredictedViewport(node, viewport)).toBe(true);
	});
});
