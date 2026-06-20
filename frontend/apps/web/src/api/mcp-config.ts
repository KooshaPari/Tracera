import { logger } from '@/lib/logger';

import { client } from './client';

const { API_BASE_URL } = client;

interface McpConfig {
  mcp_base_url?: string | null | undefined;
  auth_mode?: string | null | undefined;
  requires_auth?: boolean | undefined;
}

const envMcpBaseUrl = (import.meta.env?.['VITE_MCP_BASE_URL'] as string | undefined) ?? '';
const ENV_MCP_BASE_URL = envMcpBaseUrl ?? '';
const MCP_CONFIG_ENDPOINT = `${API_BASE_URL}/api/v1/mcp/config`;

/**
 * MCP Client configuration and utilities
 *
 * Uses HttpOnly cookie-based authentication (credentials: 'include')
 * No Authorization headers needed - backend validates via cookies
 */

let cachedConfig: McpConfig | undefined;

const createEnvConfig = (baseUrl: string): McpConfig => ({
  auth_mode: 'env',
  mcp_base_url: baseUrl,
  requires_auth: true,
});

const createDefaultConfig = (): McpConfig => ({
  auth_mode: 'none',
  mcp_base_url: undefined,
  requires_auth: false,
});

const fetchRemoteConfig = async (): Promise<McpConfig> => {
  // Send HttpOnly cookies for authentication
  const response = await fetch(MCP_CONFIG_ENDPOINT, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error(`MCP config request failed: ${response.status}`);
  }
  return (await response.json()) as McpConfig;
};

const getMcpConfig = async (): Promise<McpConfig> => {
  if (cachedConfig) {
    return cachedConfig;
  }

  if (ENV_MCP_BASE_URL) {
    cachedConfig = createEnvConfig(ENV_MCP_BASE_URL);
    return cachedConfig;
  }

  try {
    const data = await fetchRemoteConfig();
    cachedConfig = data;
    return data;
  } catch (error) {
    logger.warn('Failed to load MCP config', error);
    cachedConfig = createDefaultConfig();
    return cachedConfig;
  }
};

const getMcpBaseUrl = async (): Promise<string | null> => {
  const config = await getMcpConfig();
  return config.mcp_base_url ?? null;
};

/**
 * Fetch from MCP server with cookie-based authentication
 * Automatically includes credentials for HttpOnly cookie support
 */
const mcpFetch = async (path: string, init: RequestInit = {}): Promise<Response> => {
  const baseUrl = await getMcpBaseUrl();
  const fullUrl = path.startsWith('http') ? path : `${baseUrl ?? ''}${path}`;

  const headers = new Headers(init.headers);
  headers.set('Content-Type', 'application/json');

  const requestInit: RequestInit = {
    credentials: 'include',
    headers,
    method: init.method ?? 'GET',
  };

  if (init.body) {
    requestInit.body = init.body;
  }

  return fetch(fullUrl, requestInit);
};

export { getMcpBaseUrl, getMcpConfig, mcpFetch };
