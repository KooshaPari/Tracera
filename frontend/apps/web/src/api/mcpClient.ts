import { API_BASE_URL } from "./client";
import { logger } from '@/lib/logger';

type McpConfig = {
	mcp_base_url?: string | null;
	auth_mode?: string | null;
	requires_auth?: boolean;
};

const ENV_MCP_BASE_URL = import.meta.env?.VITE_MCP_BASE_URL as
	| string
	| undefined;
const MCP_CONFIG_ENDPOINT = `${API_BASE_URL}/api/v1/mcp/config`;

/**
 * MCP Client configuration and utilities
 *
 * Uses HttpOnly cookie-based authentication (credentials: 'include')
 * No Authorization headers needed - backend validates via cookies
 */

let cachedConfig: McpConfig | null = null;

export async function getMcpConfig(): Promise<McpConfig> {
	if (cachedConfig) return cachedConfig;

	if (ENV_MCP_BASE_URL) {
		cachedConfig = {
			mcp_base_url: ENV_MCP_BASE_URL,
			auth_mode: "env",
			requires_auth: true,
		};
		return cachedConfig;
	}

	try {
		const response = await fetch(MCP_CONFIG_ENDPOINT, {
			credentials: "include", // Send HttpOnly cookies for authentication
			headers: {
				"Content-Type": "application/json",
			},
		});
		if (!response.ok) {
			throw new Error(`MCP config request failed: ${response.status}`);
		}
		const data = (await response.json()) as McpConfig;
		cachedConfig = data;
		return data;
	} catch (error) {
		logger.warn("Failed to load MCP config", error);
		cachedConfig = {
			mcp_base_url: null,
			auth_mode: "none",
			requires_auth: false,
		};
		return cachedConfig;
	}
}

export async function getMcpBaseUrl(): Promise<string | null> {
	const config = await getMcpConfig();
	return config.mcp_base_url ?? null;
}

/**
 * Fetch from MCP server with cookie-based authentication
 * Automatically includes credentials for HttpOnly cookie support
 */
export async function mcpFetch(
	path: string,
	init: RequestInit = {},
): Promise<Response> {
	const baseUrl = await getMcpBaseUrl();
	const url = path.startsWith("http") ? path : `${baseUrl ?? ""}${path}`;

	const headers = new Headers(init.headers || {});
	// Don't set Authorization header - use credentials: 'include' instead
	headers.set("Content-Type", "application/json");

	return fetch(url, {
		...init,
		credentials: "include", // Send HttpOnly cookies for authentication
		headers,
	});
}
