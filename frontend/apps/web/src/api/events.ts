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

export const fetchEvents = async (params?: {
	limit?: number;
	offset?: number;
}): Promise<Event[]> => {
	try {
		const response = await safeApiCall(
			apiClient.GET("/api/v1/events", { params: { query: params } }),
		);
		return (response.data as Event[]) || [];
    } catch {
        return [];
	}
};

export const fetchEvent = async (id: string): Promise<Event | null> => {
	try {
		const response = await safeApiCall(
			apiClient.GET("/api/v1/events/{id}", { params: { path: { id } } }),
		);
		return (response.data as Event) || null;
    } catch {
        return null;
	}
};
