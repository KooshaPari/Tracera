// System status API stub
import { client } from "./client";
import { getMcpConfig } from "./mcp-config";

const { apiClient } = client;

export interface SystemStatus {
	status: "healthy" | "degraded" | "unhealthy";
	uptime: number;
	queuedJobs: number;
	version?: string;
	mcp?:
		| {
				baseUrl?: string | undefined;
				authMode?: string | undefined;
				requiresAuth?: boolean;
		  }
		| undefined;
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
				queuedJobs: 0,
				status: "healthy",
				uptime: 99.9,
			};
			const merged: SystemStatus = {
				queuedJobs: baseStatus.queuedJobs,
				status: baseStatus.status,
				uptime: baseStatus.uptime,
			};
			const responseData = response.data as Record<string, unknown>;
			for (const [key, value] of Object.entries(responseData)) {
				(merged as unknown as Record<string, unknown>)[key] = value;
			}
			if (mcpConfig) {
				merged.mcp = {
					authMode: mcpConfig.auth_mode ?? undefined,
					baseUrl: mcpConfig.mcp_base_url ?? undefined,
					requiresAuth: mcpConfig.requires_auth ?? false,
				};
			} else {
				merged.mcp = undefined;
			}
			return merged;
		}
	} catch {
		// Return mock data if endpoint doesn't exist
	}
	return {
		queuedJobs: 0,
		status: "healthy",
		uptime: 99.9,
	};
};
