import { logger } from "@/lib/logger";
import client from "./client";

const { API_BASE_URL } = client;

interface McpConfig {
	mcp_base_url?: string | null;
	auth_mode?: string | null;
	requires_auth?: boolean;
}

const { env } = import.meta;
const envMcpBaseUrl = env ? (env["VITE_MCP_BASE_URL"] as string | undefined) : "";
const ENV_MCP_BASE_URL = envMcpBaseUrl || "";
const MCP_CONFIG_ENDPOINT = `${API_BASE_URL}/api/v1/mcp/config`;

/**
 * MCP Client configuration and utilities
 *
 * Uses HttpOnly cookie-based authentication (credentials: 'include')
 * No Authorization headers needed - backend validates via cookies
 */

let cachedConfig: McpConfig | null = null;

const createEnvConfig = (baseUrl: string): McpConfig => ({
	mcp_base_url: baseUrl,
	auth_mode: "env",
	requires_auth: true,
});

const createDefaultConfig = (): McpConfig => ({
	mcp_base_url: null,
	auth_mode: "none",
	requires_auth: false,
});

const fetchRemoteConfig = async (): Promise<McpConfig> => {
	// Send HttpOnly cookies for authentication
	const response = await fetch(MCP_CONFIG_ENDPOINT, {
		credentials: "include",
		headers: {
			"Content-Type": "application/json",
		},
	});
	if (!response.ok) {
		throw new Error(`MCP config request failed: ${response.status}`);
	}
	return (await response.json()) as McpConfig;
};

export async function getMcpConfig(): Promise<McpConfig> {
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
		logger.warn("Failed to load MCP config", error);
		cachedConfig = createDefaultConfig();
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
	const url = path.startsWith("http") ? path : `${baseUrl || ""}${path}`;

	const headers = new Headers(init.headers || {});
	// Don't set Authorization header; use credentials: 'include' instead
	headers.set("Content-Type", "application/json");

	const requestInit = Object.assign({}, init, {
		// Send HttpOnly cookies for authentication
		credentials: "include",
		headers,
	});

	return fetch(url, requestInit);
}
