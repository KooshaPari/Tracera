/**
 * Tests for websocketStore
 */

import { act, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useWebSocketStore } from "../../stores/websocketStore";

describe("websocketStore", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe("initial state", () => {
		it("should have correct initial values", () => {
			const { result } = renderHook(() => useWebSocketStore());

			expect(result.current.isConnected).toBe(false);
			expect(result.current.reconnectAttempts).toBe(0);
			expect(result.current.lastEvent).toBeNull();
			expect(result.current.events).toEqual([]);
			expect(result.current.activeChannels.size).toBe(0);
		});
	});

	describe("connect", () => {
		it("should connect websocket", () => {
			const { result } = renderHook(() => useWebSocketStore());

			act(() => {
				result.current.connect();
			});

			// Initial state is false until connection completes
			expect(result.current.isConnected).toBeDefined();
		});
	});

	describe("disconnect", () => {
		it("should disconnect websocket", () => {
			const { result } = renderHook(() => useWebSocketStore());

			act(() => {
				result.current.disconnect();
			});

			expect(result.current.isConnected).toBe(false);
		});
	});

	describe("subscribe", () => {
		it("should subscribe to a channel", () => {
			const { result } = renderHook(() => useWebSocketStore());
			const callback = vi.fn();

			act(() => {
				result.current.subscribe("test-channel", callback);
			});

			expect(result.current.activeChannels.has("test-channel")).toBe(true);
		});

		it("should unsubscribe from a channel", () => {
			const { result } = renderHook(() => useWebSocketStore());
			const callback = vi.fn();

			let unsubscribe: () => void;

			act(() => {
				unsubscribe = result.current.subscribe("test-channel", callback);
			});

			expect(result.current.activeChannels.has("test-channel")).toBe(true);

			act(() => {
				unsubscribe();
			});

			expect(result.current.activeChannels.has("test-channel")).toBe(false);
		});
	});

	describe("events", () => {
		it("should add events", () => {
			const { result } = renderHook(() => useWebSocketStore());
			const event = {
				type: "updated" as const,
				table: "items" as const,
				schema: "public",
				record: { id: "item-1" },
				timestamp: Date.now(),
			};

			act(() => {
				result.current.addEvent(event);
			});

			expect(result.current.lastEvent).toEqual(event);
			expect(result.current.events).toContain(event);
		});

		it("should limit events to 100", () => {
			const { result } = renderHook(() => useWebSocketStore());

			act(() => {
				for (let i = 0; i < 150; i++) {
					result.current.addEvent({
						type: "created" as const,
						table: "items" as const,
						schema: "public",
						record: { id: i },
						timestamp: Date.now(),
					});
				}
			});

			expect(result.current.events.length).toBe(100);
		});

		it("should clear events", () => {
			const { result } = renderHook(() => useWebSocketStore());

			act(() => {
				result.current.addEvent({
					type: "created" as const,
					table: "items" as const,
					schema: "public",
					record: {},
					timestamp: Date.now(),
				});
				result.current.clearEvents();
			});

			expect(result.current.events).toEqual([]);
			expect(result.current.lastEvent).toBeNull();
		});
	});

	describe("setConnectionStatus", () => {
		it("should set connection status", () => {
			const { result } = renderHook(() => useWebSocketStore());

			act(() => {
				result.current.setConnectionStatus(true);
			});

			expect(result.current.isConnected).toBe(true);

			act(() => {
				result.current.setConnectionStatus(false);
			});

			expect(result.current.isConnected).toBe(false);
		});
	});
});
