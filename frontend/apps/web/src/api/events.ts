/* oxlint-disable oxc/no-async-await */
// Events API stub
import client from "./client";

interface Event {
	id: string;
	type: string;
	payload: Record<string, unknown>;
	timestamp: string;
	userId?: string;
	projectId?: string;
}

const apiClient = client.apiClient;
const safeApiCall = client.safeApiCall;
const get = apiClient.GET.bind(apiClient);

const isRecordObject = (value: unknown): value is Record<string, unknown> =>
	Object.prototype.toString.call(value) === "[object Object]";

const isEvent = (value: unknown): value is Event => {
	if (!isRecordObject(value)) {
		return false;
	}

	const payload = value["payload"];
	if (!isRecordObject(payload)) {
		return false;
	}

	return (
		typeof value["id"] === "string" &&
		typeof value["type"] === "string" &&
		typeof value["timestamp"] === "string"
	);
};

const fetchEvents = async (params?: {
	limit?: number;
	offset?: number;
}): Promise<Event[]> => {
	try {
		const response = await safeApiCall(
			get("/api/v1/events", { params: { query: params } }),
		);
		const { data } = response;
		if (Array.isArray(data)) {
			return data.filter(isEvent);
		}
		return [];
	} catch {
		return [];
	}
};

const fetchEvent = async (id: string): Promise<Event | undefined> => {
	try {
		const response = await safeApiCall(
			get("/api/v1/events/{id}", { params: { path: { id } } }),
		);
		const { data } = response;
		if (isEvent(data)) {
			return data;
		}
		return undefined;
	} catch {
		return undefined;
	}
};

const eventsApi = { fetchEvent, fetchEvents };

// eslint-disable-next-line import/no-default-export
export default eventsApi;

export { fetchEvent, fetchEvents };
export type { Event };
