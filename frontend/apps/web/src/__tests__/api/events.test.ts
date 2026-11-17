/**
 * Tests for Events API
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

import { fetchEvent, fetchEvents } from "@/api/events";

// Mock the client
vi.mock("@/api/client", () => ({
  client: {
    apiClient: {
      GET: vi.fn(),
    },
  },
}));

vi.mock("@/api/availability", () => ({
  requireAvailable: vi.fn(
    async (promise: Promise<{ data?: unknown; error?: unknown; response: Response }>) => {
      const { data, response } = await promise;
      if (!response.ok)
        throw new Error(response.status === 501 ? "Not implemented yet" : "Service unavailable");
      if (data === undefined) throw new Error("Invalid response from service");
      return data;
    },
  ),
  invalidResponse: vi.fn(() => {
    throw new Error("Invalid response from service");
  }),
}));

import { client } from "@/api/client";

const { apiClient } = client;

describe("Events API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchEvents, () => {
    it("should fetch events without params", async () => {
      const mockEvents = [
        {
          id: "1",
          payload: {},
          projectId: "proj-1",
          timestamp: "2024-01-01",
          type: "item_created",
        },
      ];
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockEvents,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchEvents();
      expect(result).toEqual(mockEvents);
      expect(apiClient.GET).toHaveBeenCalledWith("/api/v1/events", {
        params: { query: undefined },
      });
    });

    it("should fetch events with params", async () => {
      const mockEvents: unknown[] = [];
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockEvents,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchEvents({ limit: 10, offset: 0 });
      expect(result).toEqual(mockEvents);
      expect(apiClient.GET).toHaveBeenCalledWith("/api/v1/events", {
        params: { query: { limit: 10, offset: 0 } },
      });
    });

    it("should propagate error via requireAvailable", async () => {
      vi.mocked(apiClient.GET).mockRejectedValue(new Error("Network error"));

      await expect(fetchEvents()).rejects.toThrow("Network error");
    });
  });

  describe(fetchEvent, () => {
    it("should fetch a single event by id", async () => {
      const mockEvent = {
        id: "1",
        payload: {},
        timestamp: "2024-01-01",
        type: "item_created",
      };
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockEvent,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchEvent("1");
      expect(result).toEqual(mockEvent);
      expect(apiClient.GET).toHaveBeenCalledWith("/api/v1/events/{id}", {
        params: { path: { id: "1" } },
      });
    });

    it("should propagate error via requireAvailable", async () => {
      vi.mocked(apiClient.GET).mockRejectedValue(new Error("Not found"));

      await expect(fetchEvent("non-existent")).rejects.toThrow("Not found");
    });
  });
});
