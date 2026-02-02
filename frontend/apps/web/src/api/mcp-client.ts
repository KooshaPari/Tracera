/**
 * MCP HTTP Client for TraceRTM
 *
 * Provides HTTP transport for MCP protocol with:
 * - JSON-RPC 2.0 request/response handling
 * - Bearer token authentication
 * - Server-Sent Events (SSE) for progress streaming
 * - TypeScript type safety
 */

import EventSourcePolyfill from "event-source-polyfill";

/**
 * JSON-RPC 2.0 request structure
 */
export interface JsonRpcRequest {
	jsonrpc: "2.0";
	id: string | number;
	method: string;
	params?: Record<string, unknown> | undefined;
}

/**
 * JSON-RPC 2.0 response structure
 */
export interface JsonRpcResponse<T = unknown> {
	jsonrpc: "2.0";
	id: string | number;
	result?: T;
	error?: {
		code: number;
		message: string;
		data?: unknown;
	};
}

/**
 * MCP tool parameter definition
 */
export interface MCPToolParam {
	name: string;
	type: string;
	description?: string;
	required?: boolean;
	default?: unknown;
}

/**
 * MCP tool definition
 */
export interface MCPTool {
	name: string;
	description: string;
	parameters: MCPToolParam[];
}

/**
 * MCP resource definition
 */
export interface MCPResource {
	uri: string;
	name: string;
	description?: string;
	mimeType?: string;
}

/**
 * MCP prompt definition
 */
export interface MCPPrompt {
	name: string;
	description?: string;
	arguments?: MCPToolParam[];
}

/**
 * Progress notification from SSE stream
 */
export interface ProgressNotification {
	progress: number;
	total?: number;
	message?: string;
}

/**
 * MCP client configuration
 */
export interface MCPClientConfig {
	baseUrl: string;
	token?: string;
	timeout?: number;
}

/**
 * HTTP-based MCP client implementation
 */
export class MCPClient {
	private baseUrl: string;
	private token?: string;
	private timeout: number;
	private requestId = 0;

	constructor(config: MCPClientConfig) {
		this.baseUrl = config.baseUrl.replace(/\/$/, ""); // Remove trailing slash
		this.token = config.token;
		this.timeout = config.timeout || 30000;
	}

	/**
	 * Set or update the authentication token
	 */
	setToken(token: string): void {
		this.token = token;
	}

	/**
	 * Generate a unique request ID
	 */
	private nextRequestId(): number {
		return ++this.requestId;
	}

	/**
	 * Build headers for MCP requests
	 */
	private buildHeaders(): Record<string, string> {
		const headers: Record<string, string> = {
			"Content-Type": "application/json",
		};

		if (this.token) {
			headers['Authorization'] = `Bearer ${this.token}`;
		}

		return headers;
	}

	/**
	 * Send a JSON-RPC request to the MCP server
	 */
	private async sendRequest<T>(
		method: string,
		params?: Record<string, unknown>,
	): Promise<T> {
		const request: JsonRpcRequest = {
			jsonrpc: "2.0",
			id: this.nextRequestId(),
			method,
			params,
		};

		const controller = new AbortController();
		let timeoutId: ReturnType<typeof setTimeout> | null = null;
		const timeoutPromise = new Promise<never>((_, reject) => {
			timeoutId = setTimeout(() => {
				controller.abort();
				reject(new Error("Request timeout"));
			}, this.timeout);
		});

		try {
			const fetchPromise = fetch(`${this.baseUrl}/mcp/rpc`, {
				method: "POST",
				headers: this.buildHeaders(),
				body: JSON.stringify(request),
				signal: controller.signal,
			});
			const response = await Promise.race([fetchPromise, timeoutPromise]);

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			const data: JsonRpcResponse<T> = await response.json();

			if (data.error) {
				throw new Error(
					`JSON-RPC Error ${data.error.code}: ${data.error.message}`,
				);
			}

			if (data.result === undefined) {
				throw new Error("Invalid JSON-RPC response: missing result");
			}

			return data.result;
		} finally {
			if (timeoutId) {
				clearTimeout(timeoutId);
			}
		}
	}

	/**
	 * Initialize the MCP session
	 */
	async initialize(params?: {
		protocolVersion?: string;
		capabilities?: Record<string, unknown>;
		clientInfo?: { name: string; version: string };
	}): Promise<{
		protocolVersion: string;
		capabilities: Record<string, unknown>;
		serverInfo: { name: string; version: string };
	}> {
		return this.sendRequest("initialize", params);
	}

	/**
	 * List available tools
	 */
	async listTools(): Promise<{ tools: MCPTool[] }> {
		return this.sendRequest("tools/list");
	}

	/**
	 * Call a tool with parameters
	 */
	async callTool<T = unknown>(
		name: string,
		args?: Record<string, unknown>,
	): Promise<T> {
		return this.sendRequest("tools/call", { name, arguments: args });
	}

	/**
	 * List available resources
	 */
	async listResources(): Promise<{ resources: MCPResource[] }> {
		return this.sendRequest("resources/list");
	}

	/**
	 * Read a resource by URI
	 */
	async readResource(uri: string): Promise<{ contents: unknown }> {
		return this.sendRequest("resources/read", { uri });
	}

	/**
	 * List available prompts
	 */
	async listPrompts(): Promise<{ prompts: MCPPrompt[] }> {
		return this.sendRequest("prompts/list");
	}

	/**
	 * Get a prompt with arguments
	 */
	async getPrompt(
		name: string,
		args?: Record<string, unknown>,
	): Promise<{ messages: unknown[] }> {
		return this.sendRequest("prompts/get", { name, arguments: args });
	}

	/**
	 * Subscribe to progress notifications via SSE
	 */
	subscribeToProgress(
		onProgress: (notification: ProgressNotification) => void,
		onError?: (error: Error) => void,
	): () => void {
		const headers: Record<string, string> = {};
		if (this.token) {
			headers['Authorization'] = `Bearer ${this.token}`;
		}

		const eventSource = new EventSourcePolyfill(
			`${this.baseUrl}/mcp/progress`,
			{
				headers,
			},
		);

		/* eslint-disable unicorn/prefer-add-event-listener -- EventSource API uses .onmessage/.onerror */
		eventSource.onmessage = (event: MessageEvent) => {
			try {
				const notification = JSON.parse(event.data) as ProgressNotification;
				onProgress(notification);
			} catch (error) {
				if (onError) {
					onError(
						error instanceof Error
							? error
							: new Error("Failed to parse progress"),
					);
				}
			}
		};

		eventSource.onerror = (_error: Event) => {
			if (onError) {
				onError(new Error("SSE connection error"));
			}
		};
		/* eslint-enable unicorn/prefer-add-event-listener */

		// Return cleanup function
		return () => {
			eventSource.close();
		};
	}

	/**
	 * Close the MCP session
	 */
	async close(): Promise<void> {
		// MCP doesn't have a formal close method, but we can send a notification
		// No response expected for notifications
		try {
			await fetch(`${this.baseUrl}/mcp/rpc`, {
				method: "POST",
				headers: this.buildHeaders(),
				body: JSON.stringify({
					jsonrpc: "2.0",
					method: "notifications/cancelled",
					params: {},
				}),
			});
		} catch {
			// Ignore errors on close
		}
	}
}

/**
 * Create an MCP client instance
 */
export function createMCPClient(config: MCPClientConfig): MCPClient {
	return new MCPClient(config);
}
