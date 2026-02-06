/**
 * Agent session API - create and manage per-session sandboxes for chat.
 * Used by chat to run tools in a scoped filesystem per conversation.
 */

import { client } from './client';

const API_URL = client.getBackendURL();

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
  Object.prototype.toString.call(value) === '[object Object]';

const isAgentSessionResponse = (value: unknown): value is AgentSessionResponse => {
  if (!isRecordObject(value)) {
    return false;
  }

  return (
    typeof value['session_id'] === 'string' &&
    typeof value['sandbox_root'] === 'string' &&
    typeof value['created_at'] === 'string' &&
    typeof value['updated_at'] === 'string' &&
    (typeof value['project_id'] === 'string' || value['project_id'] === null)
  );
};

const createAgentSession = async (
  body: AgentSessionCreateRequest,
): Promise<AgentSessionResponse> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...client.getAuthHeaders(),
  };
  const response = await fetch(`${API_URL}/api/v1/agent/sessions`, {
    body: JSON.stringify(body),
    headers,
    method: 'POST',
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Agent session create failed: ${response.status} ${errorText}`);
  }
  const data: unknown = await response.json();
  if (!isAgentSessionResponse(data)) {
    throw new Error('Invalid agent session response');
  }
  return data;
};

const agentApi = {
  createAgentSession,
};

export { agentApi, createAgentSession };
