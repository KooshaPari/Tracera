// Traceability Matrix API stub
import client from "./client";
import type { Item, Link } from "./types";

const { apiClient, safeApiCall } = client;

export interface TraceabilityMatrix {
	coverage: {
		percentage: number;
		total: number;
		traced: number;
		untraced: number;
	};
	items: Item[];
	links: Link[];
}

const fetchMatrix = (projectId: string): Promise<TraceabilityMatrix> => {
	const response = safeApiCall(
		apiClient.GET("/api/v1/projects/{id}/matrix", {
			params: { path: { id: projectId } },
		}),
	);
	return response
		.then((res) => {
			const data = res.data;
			if (
				data &&
				typeof data === "object" &&
				"coverage" in data &&
				"items" in data &&
				"links" in data
			) {
				return data as TraceabilityMatrix;
			}
			return {
				coverage: {
					percentage: 0,
					total: 0,
					traced: 0,
					untraced: 0,
				},
				items: [],
				links: [],
			} satisfies TraceabilityMatrix;
		})
		.catch(() => {
			return {
				coverage: {
					percentage: 0,
					total: 0,
					traced: 0,
					untraced: 0,
				},
				items: [],
				links: [],
			} satisfies TraceabilityMatrix;
		});
};

const exportMatrix = (
	projectId: string,
	format: "csv" | "json" | "xlsx",
): Promise<Blob> => {
	const response = safeApiCall(
		apiClient.GET("/api/v1/projects/{id}/matrix/export", {
			params: { path: { id: projectId }, query: { format } },
		}),
	);
	return response
		.then((res) => {
			return new Blob([JSON.stringify(res.data)], {
				type: "application/json",
			});
		})
		.catch(() => {
			return new Blob(["{}"], { type: "application/json" });
		});
};

const matrixApi = { exportMatrix, fetchMatrix };

// eslint-disable-next-line import/no-default-export
export default matrixApi;
