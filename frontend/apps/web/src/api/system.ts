// System status API stub
import { getMcpConfig } from "./mcp-config";
import client from "./client";

const { apiClient } = client;

export interface SystemStatus {
	status: "healthy" | "degraded" | "unhealthy";
	uptime: number;
	queuedJobs: number;
	version?: string;
	mcp?: {
		baseUrl?: string | null;
		authMode?: string | null;
		requiresAuth?: boolean;
	} | null;
}

export const fetchSystemStatus = async (): Promise<SystemStatus> => {
	// Try to fetch from health endpoint, fallback to mock data
	try {
		const [response, mcpConfig] = await Promise.all([
			apiClient.GET("/api/v1/health", {}),
			getMcpConfig().catch(() => null),
		]);
		if (response.data) {
			const baseStatus: SystemStatus = {
				status: "healthy",
				uptime: 99.9,
				queuedJobs: 0,
			};
			const merged = Object.assign({}, baseStatus, response.data);
			if (mcpConfig) {
				merged.mcp = {
					baseUrl: mcpConfig.mcp_base_url ?? null,
					authMode: mcpConfig.auth_mode ?? null,
					requiresAuth: mcpConfig.requires_auth ?? false,
				};
			} else {
				merged.mcp = null;
			}
			return merged;
		}
	} catch {
		// Return mock data if endpoint doesn't exist
	}
	return {
		status: "healthy",
		uptime: 99.9,
		queuedJobs: 0,
	};
};
