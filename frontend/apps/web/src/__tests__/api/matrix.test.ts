/**
 * Tests for Traceability Matrix API
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

import type { TraceabilityMatrix } from "@/api/matrix";

import { exportMatrix, fetchMatrix } from "@/api/matrix";

// Mock the API client
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

import { mockItems, mockLinks } from "../mocks/data";

const { apiClient } = client;

describe("Traceability Matrix API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchMatrix, () => {
    it("should fetch matrix for a project", async () => {
      const mockMatrix: TraceabilityMatrix = {
        coverage: {
          percentage: 66.67,
          total: 3,
          traced: 2,
          untraced: 1,
        },
        items: mockItems,
        links: mockLinks,
      };

      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockMatrix,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchMatrix("proj-1");

      expect(result).toEqual(mockMatrix);
      expect(result.coverage.percentage).toBe(66.67);
      expect(result.items).toHaveLength(mockItems.length);
      expect(result.links).toHaveLength(mockLinks.length);
    });

    it("should propagate error via requireAvailable", async () => {
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: undefined,
        error: undefined,
        response: new Response(null, { status: 503 }),
      });

      await expect(fetchMatrix("proj-1")).rejects.toThrow("Service unavailable");
    });

    it("should throw invalidResponse for malformed data", async () => {
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: { coverage: "invalid" },
        error: undefined,
        response: new Response(),
      });

      await expect(fetchMatrix("proj-1")).rejects.toThrow("Invalid response from service");
    });

    it("should include traced/untraced coverage statistics", async () => {
      const mockMatrix: TraceabilityMatrix = {
        coverage: {
          percentage: 100,
          total: 2,
          traced: 2,
          untraced: 0,
        },
        items: mockItems.slice(0, 2),
        links: mockLinks,
      };

      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockMatrix,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchMatrix("proj-1");

      expect(result.coverage.traced).toBe(2);
      expect(result.coverage.untraced).toBe(0);
      expect(result.coverage.percentage).toBe(100);
    });

    it("should call API with correct project ID", async () => {
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: {
          coverage: { percentage: 0, total: 0, traced: 0, untraced: 0 },
          items: [],
          links: [],
        },
        error: undefined,
        response: new Response(),
      });

      await fetchMatrix("specific-proj-123");

      expect(apiClient.GET).toHaveBeenCalledWith(
        "/api/v1/projects/{id}/matrix",
        expect.objectContaining({
          params: { path: { id: "specific-proj-123" } },
        }),
      );
    });
  });

  describe(exportMatrix, () => {
    it("should export matrix as CSV", async () => {
      const mockBlob = new Blob(["csv-data"], { type: "text/csv" });
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockBlob,
        error: undefined,
        response: new Response(),
      });

      const result = await exportMatrix("proj-1", "csv");

      expect(result).toBeInstanceOf(Blob);
    });

    it("should export matrix as JSON", async () => {
      const mockBlob = new Blob(['{"items":[],"links":[]}'], {
        type: "application/json",
      });
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockBlob,
        error: undefined,
        response: new Response(),
      });

      const result = await exportMatrix("proj-1", "json");

      expect(result).toBeInstanceOf(Blob);
    });

    it("should export matrix as XLSX", async () => {
      const mockBlob = new Blob(["xlsx-data"], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockBlob,
        error: undefined,
        response: new Response(),
      });

      const result = await exportMatrix("proj-1", "xlsx");

      expect(result).toBeInstanceOf(Blob);
    });

    it("should propagate error via requireAvailable", async () => {
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: undefined,
        error: undefined,
        response: new Response(null, { status: 503 }),
      });

      await expect(exportMatrix("proj-1", "csv")).rejects.toThrow("Service unavailable");
    });

    it("should throw invalidResponse for non-blob data", async () => {
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: { items: [] },
        error: undefined,
        response: new Response(),
      });

      await expect(exportMatrix("proj-1", "csv")).rejects.toThrow("Invalid response from service");
    });

    it("should call API with correct export format", async () => {
      const mockBlob = new Blob(["data"]);
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockBlob,
        error: undefined,
        response: new Response(),
      });

      await exportMatrix("proj-1", "xlsx");

      expect(apiClient.GET).toHaveBeenCalledWith(
        "/api/v1/projects/{id}/matrix/export",
        expect.objectContaining({
          params: {
            path: { id: "proj-1" },
            query: { format: "xlsx" },
          },
        }),
      );
    });

    it("should support all export formats", async () => {
      const mockBlob = new Blob(["data"]);
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockBlob,
        error: undefined,
        response: new Response(),
      });

      const formats: ("csv" | "json" | "xlsx")[] = ["csv", "json", "xlsx"];

      for (const format of formats) {
        const result = await exportMatrix("proj-1", format);
        expect(result).toBeInstanceOf(Blob);
      }
    });

    it("should handle large datasets in export", async () => {
      const mockBlob = new Blob(["x".repeat(100000)]);
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockBlob,
        error: undefined,
        response: new Response(),
      });

      const result = await exportMatrix("proj-1", "json");

      expect(result).toBeInstanceOf(Blob);
      expect(result.size).toBeGreaterThan(0);
    });
  });

  describe("Matrix API error handling", () => {
    it("should propagate network errors from requireAvailable", async () => {
      vi.mocked(apiClient.GET).mockRejectedValue(new Error("Network error"));

      await expect(fetchMatrix("proj-1")).rejects.toThrow("Network error");
    });

    it("should throw on null response data", async () => {
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: null,
        error: undefined,
        response: new Response(),
      });

      await expect(fetchMatrix("proj-1")).rejects.toThrow("Invalid response from service");
    });

    it("should throw invalidResponse on partial matrix data", async () => {
      const partialMatrix: Partial<TraceabilityMatrix> = {
        items: mockItems,
        // Links is missing
      };

      vi.mocked(apiClient.GET).mockResolvedValue({
        data: partialMatrix,
        error: undefined,
        response: new Response(),
      });

      await expect(fetchMatrix("proj-1")).rejects.toThrow("Invalid response from service");
    });
  });
});
