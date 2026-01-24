// Traceability Matrix API stub
import { apiClient, safeApiCall } from "./client";
import type { Item, Link } from "./types";

export interface TraceabilityMatrix {
	items: Item[];
	links: Link[];
	coverage: {
		total: number;
		traced: number;
		untraced: number;
		percentage: number;
	};
}

export const fetchMatrix = async (
	projectId: string,
): Promise<TraceabilityMatrix> => {
	try {
		const response = await safeApiCall(
			apiClient.GET("/api/v1/projects/{id}/matrix", {
				params: { path: { id: projectId } },
			}),
		);
		return (
			(response.data as TraceabilityMatrix) || {
				items: [],
				links: [],
				coverage: { total: 0, traced: 0, untraced: 0, percentage: 0 },
			}
		);
	} catch {
		return {
			items: [],
			links: [],
			coverage: { total: 0, traced: 0, untraced: 0, percentage: 0 },
		};
	}
};

export const exportMatrix = async (
	projectId: string,
	format: "csv" | "json" | "xlsx",
): Promise<Blob> => {
	try {
		const response = await safeApiCall(
			apiClient.GET("/api/v1/projects/{id}/matrix/export", {
				params: { path: { id: projectId }, query: { format } },
			}),
		);
		return new Blob([JSON.stringify(response.data)], {
			type: "application/json",
		});
	} catch {
		return new Blob(["{}"], { type: "application/json" });
	}
};
