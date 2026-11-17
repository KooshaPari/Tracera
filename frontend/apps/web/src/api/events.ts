// Events API stub
import { client } from "./client";
import { requireAvailable, invalidResponse } from "./availability";

interface Event {
  id: string;
  type: string;
  payload: Record<string, unknown>;
  timestamp: string;
  userId?: string;
  projectId?: string;
}

type ApiClient = typeof client.apiClient;
const { apiClient } = client;
const get: ApiClient["GET"] = apiClient.GET.bind(apiClient);

const isRecordObject = (value: unknown): value is Record<string, unknown> =>
  Object.prototype.toString.call(value) === "[object Object]";

const isEvent = (value: unknown): value is Event => {
  if (!isRecordObject(value)) {
    return false;
  }

  const { payload } = value;
  if (!isRecordObject(payload)) {
    return false;
  }

  return (
    typeof value["id"] === "string" &&
    typeof value["type"] === "string" &&
    typeof value["timestamp"] === "string"
  );
};

const fetchEvents = async (params?: { limit?: number; offset?: number }): Promise<Event[]> => {
  const data = await requireAvailable(get("/api/v1/events", { params: { query: params } }));
  if (!Array.isArray(data) || !data.every(isEvent)) return invalidResponse();
  return data;
};

const fetchEvent = async (id: string): Promise<Event | undefined> => {
  const data = await requireAvailable(get("/api/v1/events/{id}", { params: { path: { id } } }));
  if (!isEvent(data)) return invalidResponse();
  return data;
};

export { fetchEvent, fetchEvents };
export type { Event };
