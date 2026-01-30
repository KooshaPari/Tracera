// System status API stub
import { apiClient } from "./client";
import { getMcpConfig } from "./mcpClient";

export interface SystemStatus {
	status: "healthy" | "degraded" | "unhealthy";
	uptime: number;
	queuedJobs: number;
	version?: string;
	mcp?: {
		baseUrl?: string | null;
		authMode?: string | null;
		requiresAuth?: boolean;
	};
}

export const fetchSystemStatus = async (): Promise<SystemStatus> => {
	// Try to fetch from health endpoint, fallback to mock data
	try {
		const [response, mcpConfig] = await Promise.all([
			apiClient.GET("/api/v1/health", {}),
			getMcpConfig().catch(() => null),
		]);
		if (response.data) {
			return {
				status: "healthy",
				uptime: 99.9,
				queuedJobs: 0,
				mcp: mcpConfig
					? {
							baseUrl: mcpConfig.mcp_base_url ?? null,
							authMode: mcpConfig.auth_mode ?? null,
							requiresAuth: mcpConfig.requires_auth ?? false,
						}
					: undefined,
				...response.data,
			};
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
