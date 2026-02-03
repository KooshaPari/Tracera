/* oxlint-disable oxc/no-async-await */
/**
 * Agent session API - create and manage per-session sandboxes for chat.
 * Used by chat to run tools in a scoped filesystem per conversation.
 */

import client from "./client";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

interface AgentSessionCreateRequest {
	project_id?: string | null;
	session_id?: string | null;
}

interface AgentSessionResponse {
	session_id: string;
	sandbox_root: string;
	project_id: string | null;
	created_at: string;
	updated_at: string;
}

const isRecordObject = (value: unknown): value is Record<string, unknown> =>
	Object.prototype.toString.call(value) === "[object Object]";

const isAgentSessionResponse = (
	value: unknown,
): value is AgentSessionResponse => {
	if (!isRecordObject(value)) {
		return false;
	}

	return (
		typeof value["session_id"] === "string" &&
		typeof value["sandbox_root"] === "string" &&
		typeof value["created_at"] === "string" &&
		typeof value["updated_at"] === "string" &&
		(typeof value["project_id"] === "string" || value["project_id"] === null)
	);
};

const createAgentSession = async (
	body: AgentSessionCreateRequest,
): Promise<AgentSessionResponse> => {
	const headers = Object.assign(
		{ "Content-Type": "application/json" },
		client.getAuthHeaders(),
	);
	const res = await fetch(`${API_URL}/api/v1/agent/sessions`, {
		body: JSON.stringify(body),
		headers,
		method: "POST",
	});
	if (!res.ok) {
		const text = await res.text();
		throw new Error(`Agent session create failed: ${res.status} ${text}`);
	}
	const data = await res.json();
	if (!isAgentSessionResponse(data)) {
		throw new Error("Invalid agent session response");
	}
	return data;
};

const agentApi = {
	createAgentSession,
};

// eslint-disable-next-line import/no-default-export
export default agentApi;
