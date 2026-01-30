/**
 * Tests for System API
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchSystemStatus } from "@/api/system";

// Mock client
vi.mock("@/api/client", () => ({
	apiClient: {
		GET: vi.fn(),
	},
}));
vi.mock("@/api/mcpClient", () => ({
	getMcpConfig: vi.fn(),
}));

import { apiClient } from "@/api/client";
import { getMcpConfig } from "@/api/mcpClient";

describe("System API", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe("fetchSystemStatus", () => {
		it("should fetch system status successfully", async () => {
			const mockStatus = {
				status: "healthy" as const,
				uptime: 99.9,
				queuedJobs: 2,
				version: "1.0.0",
			};
			vi.mocked(apiClient.GET).mockResolvedValue({
				data: mockStatus,
				error: undefined,
				response: new Response(),
			});
			vi.mocked(getMcpConfig).mockResolvedValue({
				mcp_base_url: "http://localhost:9000",
				auth_mode: "authkit",
				requires_auth: true,
			});

			const result = await fetchSystemStatus();
			expect(result).toEqual({
				...mockStatus,
				mcp: {
					baseUrl: "http://localhost:9000",
					authMode: "authkit",
					requiresAuth: true,
				},
			});
			expect(apiClient.GET).toHaveBeenCalledWith("/api/v1/health", {});
		});

		it("should return mock data when endpoint fails", async () => {
			vi.mocked(apiClient.GET).mockRejectedValue(new Error("Network error"));
			vi.mocked(getMcpConfig).mockResolvedValue({
				mcp_base_url: "http://localhost:9000",
			});

			const result = await fetchSystemStatus();
			expect(result).toEqual({
				status: "healthy",
				uptime: 99.9,
				queuedJobs: 0,
			});
		});

		it("should merge response data with defaults", async () => {
			const responseData = {
				status: "degraded" as const,
				version: "2.0.0",
			};
			vi.mocked(apiClient.GET).mockResolvedValue({
				data: responseData,
				error: undefined,
				response: new Response(),
			});
			vi.mocked(getMcpConfig).mockResolvedValue({
				mcp_base_url: "http://localhost:9000",
				auth_mode: "authkit",
				requires_auth: true,
			});

			const result = await fetchSystemStatus();
			expect(result).toEqual({
				status: "healthy", // Overridden by response
				uptime: 99.9,
				queuedJobs: 0,
				mcp: {
					baseUrl: "http://localhost:9000",
					authMode: "authkit",
					requiresAuth: true,
				},
				...responseData,
			});
			expect(result.status).toBe("degraded");
			expect(result.version).toBe("2.0.0");
		});

		it("should handle empty response data", async () => {
			vi.mocked(apiClient.GET).mockResolvedValue({
				data: null,
				error: undefined,
				response: new Response(),
			});
			vi.mocked(getMcpConfig).mockResolvedValue({
				mcp_base_url: "http://localhost:9000",
			});

			const result = await fetchSystemStatus();
			expect(result).toEqual({
				status: "healthy",
				uptime: 99.9,
				queuedJobs: 0,
			});
		});
	});
});
