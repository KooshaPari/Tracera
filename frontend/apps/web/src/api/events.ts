/* oxlint-disable oxc/no-async-await */
// Events API stub
import client from "./client";

const { apiClient, safeApiCall } = client;

export interface Event {
	id: string;
	type: string;
	payload: Record<string, unknown>;
	timestamp: string;
	userId?: string;
	projectId?: string;
}

const fetchEvents = async (params?: {
	limit?: number;
	offset?: number;
}): Promise<Event[]> => {
	try {
		const response = await safeApiCall(
			apiClient.GET("/api/v1/events", { params: { query: params } }),
		);
		const data = response.data;
		if (Array.isArray(data)) {
			return data as Event[];
		}
		return [];
	} catch {
		return [];
	}
};

const fetchEvent = async (id: string): Promise<Event | null> => {
	try {
		const response = await safeApiCall(
			apiClient.GET("/api/v1/events/{id}", { params: { path: { id } } }),
		);
		const data = response.data;
		if (data && typeof data === "object" && "id" in data) {
			return data as Event;
		}
		return null;
	} catch {
		return null;
	}
};

const eventsApi = { fetchEvent, fetchEvents };

// eslint-disable-next-line import/no-default-export
export default eventsApi;
