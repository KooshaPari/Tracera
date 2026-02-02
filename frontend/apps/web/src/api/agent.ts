/**
 * Agent session API - create and manage per-session sandboxes for chat.
 * Used by chat to run tools in a scoped filesystem per conversation.
 */

import client from "./client";

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

export interface AgentSessionCreateRequest {
	project_id?: string | null;
	session_id?: string | null;
}

export interface AgentSessionResponse {
	session_id: string;
	sandbox_root: string;
	project_id: string | null;
	created_at: string;
	updated_at: string;
}

/**
 * Create an agent session (sandbox). Returns session_id for use in chat requests.
 * Call when starting a chat with a project context so tools run in that session's sandbox.
 */
export async function createAgentSession(
	body: AgentSessionCreateRequest,
): Promise<AgentSessionResponse> {
	const res = await fetch(`${API_URL}/api/v1/agent/sessions`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			...getAuthHeaders(),
		},
		body: JSON.stringify(body),
	});
	if (!res.ok) {
		const text = await res.text();
		throw new Error(`Agent session create failed: ${res.status} ${text}`);
	}
	return res.json() as Promise<AgentSessionResponse>;
}
