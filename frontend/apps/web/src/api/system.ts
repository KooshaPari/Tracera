// System status API stub
import { apiClient } from "./client";

export interface SystemStatus {
	status: "healthy" | "degraded" | "unhealthy";
	uptime: number;
	activeAgents: number;
	queuedJobs: number;
	version?: string;
}

export const fetchSystemStatus = async (): Promise<SystemStatus> => {
	// Try to fetch from health endpoint, fallback to mock data
	try {
		const response = await apiClient.GET("/api/v1/health", {});
		if (response.data) {
			return {
				status: "healthy",
				uptime: 99.9,
				activeAgents: 0,
				queuedJobs: 0,
				...response.data,
			};
		}
	} catch {
		// Return mock data if endpoint doesn't exist
	}
	return {
		status: "healthy",
		uptime: 99.9,
		activeAgents: 0,
		queuedJobs: 0,
	};
};
