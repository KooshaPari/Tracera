/**
 * Tests for Events API
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchEvent, fetchEvents } from "@/api/events";

// Mock the client
vi.mock("@/api/client", () => ({
	apiClient: {
		GET: vi.fn(),
	},
	safeApiCall: vi.fn(),
	handleApiResponse: vi.fn(),
}));

import { apiClient, handleApiResponse, safeApiCall } from "@/api/client";

describe("Events API", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe("fetchEvents", () => {
		it("should fetch events without params", async () => {
			const mockEvents = [
				{
					id: "1",
					type: "item_created",
					payload: {},
					timestamp: "2024-01-01",
					projectId: "proj-1",
				},
			];
			vi.mocked(apiClient.GET).mockResolvedValue({
				data: mockEvents,
				error: undefined,
				response: new Response(),
			});
			vi.mocked(safeApiCall).mockResolvedValue({
				data: mockEvents,
				error: undefined,
				response: new Response(),
			});
			vi.mocked(handleApiResponse).mockResolvedValue(mockEvents);

			const result = await fetchEvents();
			expect(result).toEqual(mockEvents);
			expect(apiClient.GET).toHaveBeenCalledWith("/api/v1/events", {
				params: { query: undefined },
			});
		});

		it("should fetch events with params", async () => {
			const mockEvents = [];
			vi.mocked(apiClient.GET).mockResolvedValue({
				data: mockEvents,
				error: undefined,
				response: new Response(),
			});
			vi.mocked(safeApiCall).mockResolvedValue({
				data: mockEvents,
				error: undefined,
				response: new Response(),
			});
			vi.mocked(handleApiResponse).mockResolvedValue(mockEvents);

			const result = await fetchEvents({ limit: 10, offset: 0 });
			expect(result).toEqual(mockEvents);
			expect(apiClient.GET).toHaveBeenCalledWith("/api/v1/events", {
				params: { query: { limit: 10, offset: 0 } },
			});
		});

		it("should return empty array on error", async () => {
			vi.mocked(apiClient.GET).mockRejectedValue(new Error("Network error"));
			vi.mocked(safeApiCall).mockRejectedValue(new Error("Network error"));
			vi.mocked(handleApiResponse).mockRejectedValue(
				new Error("Network error"),
			);

			const result = await fetchEvents();
			expect(result).toEqual([]);
		});
	});

	describe("fetchEvent", () => {
		it("should fetch a single event by id", async () => {
			const mockEvent = {
				id: "1",
				type: "item_created",
				payload: {},
				timestamp: "2024-01-01",
			};
			vi.mocked(apiClient.GET).mockResolvedValue({
				data: mockEvent,
				error: undefined,
				response: new Response(),
			});
			vi.mocked(safeApiCall).mockResolvedValue({
				data: mockEvent,
				error: undefined,
				response: new Response(),
			});
			vi.mocked(handleApiResponse).mockResolvedValue(mockEvent);

			const result = await fetchEvent("1");
			expect(result).toEqual(mockEvent);
			expect(apiClient.GET).toHaveBeenCalledWith("/api/v1/events/{id}", {
				params: { path: { id: "1" } },
			});
		});

		it("should return null on error", async () => {
			vi.mocked(apiClient.GET).mockRejectedValue(new Error("Not found"));
			vi.mocked(safeApiCall).mockRejectedValue(new Error("Not found"));
			vi.mocked(handleApiResponse).mockRejectedValue(new Error("Not found"));

			const result = await fetchEvent("non-existent");
			expect(result).toBeNull();
		});
	});
});
