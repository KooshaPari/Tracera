/**
 * Tests for System API
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

import { fetchSystemStatus } from "@/api/system";

// Mock client
vi.mock("@/api/client", () => ({
  client: {
    apiClient: {
      GET: vi.fn(),
    },
    ApiError: class ApiError extends Error {
      status: number;
      statusText: string;
      constructor(status: number, statusText: string) {
        super(`API Error ${status}: ${statusText}`);
        this.status = status;
        this.statusText = statusText;
      }
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

vi.mock("@/api/mcp-config", () => ({
  getMcpConfig: vi.fn(),
}));

import { client } from "@/api/client";

const { apiClient } = client;

describe("System API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchSystemStatus, () => {
    it("should fetch system status successfully", async () => {
      const mockApiResponse = {
        queuedJobs: 2,
        status: "healthy",
        uptime_seconds: 99.9,
        version: "1.0.0",
      };
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockApiResponse,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSystemStatus();
      expect(result).toEqual({
        queuedJobs: 2,
        status: "healthy",
        uptime: 99.9,
        version: "1.0.0",
      });
      expect(apiClient.GET).toHaveBeenCalledWith("/api/v1/health", {});
    });

    it("should propagate error via requireAvailable", async () => {
      vi.mocked(apiClient.GET).mockRejectedValue(new Error("Network error"));

      await expect(fetchSystemStatus()).rejects.toThrow("Network error");
    });

    it("should normalize ok status to healthy", async () => {
      const responseData = {
        status: "ok",
        uptime_seconds: 50,
      };
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: responseData,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSystemStatus();
      expect(result.status).toBe("healthy");
      expect(result.uptime).toBe(50);
    });

    it("should normalize ready status to healthy", async () => {
      const responseData = {
        status: "ready",
        uptime_seconds: 100,
      };
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: responseData,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSystemStatus();
      expect(result.status).toBe("healthy");
      expect(result.uptime).toBe(100);
    });

    it("should pass through degraded status", async () => {
      const responseData = {
        status: "degraded",
        uptime_seconds: 50,
      };
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: responseData,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSystemStatus();
      expect(result.status).toBe("degraded");
      expect(result.uptime).toBe(50);
    });

    it("should throw invalidResponse when uptime is missing", async () => {
      const responseData = {
        status: "degraded",
        version: "2.0.0",
      };
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: responseData,
        error: undefined,
        response: new Response(),
      });

      await expect(fetchSystemStatus()).rejects.toThrow("Invalid response from service");
    });

    it("should throw invalidResponse when status is invalid", async () => {
      const responseData = {
        status: "unknown_status",
        uptime_seconds: 50,
      };
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: responseData,
        error: undefined,
        response: new Response(),
      });

      await expect(fetchSystemStatus()).rejects.toThrow("Invalid response from service");
    });
  });
});
