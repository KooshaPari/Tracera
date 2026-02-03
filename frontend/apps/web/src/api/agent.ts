/* oxlint-disable oxc/no-async-await */
/**
 * Agent session API - create and manage per-session sandboxes for chat.
 * Used by chat to run tools in a scoped filesystem per conversation.
 */

import client from "./client";

const { getAuthHeaders } = client;

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

async function createAgentSession(
	body: AgentSessionCreateRequest,
): Promise<AgentSessionResponse> {
	const res = await fetch(`${API_URL}/api/v1/agent/sessions`, {
		body: JSON.stringify(body),
		headers: {
			"Content-Type": "application/json",
			...getAuthHeaders(),
		},
		method: "POST",
	});
	if (!res.ok) {
		const text = await res.text();
		throw new Error(`Agent session create failed: ${res.status} ${text}`);
	}
	return res.json() as Promise<AgentSessionResponse>;
}

const agentApi = {
	createAgentSession,
};

// eslint-disable-next-line import/no-default-export
export default agentApi;
