/**
 * React hook for MCP client integration
 *
 * Provides easy-to-use React hooks for:
 * - MCP client lifecycle management
 * - Tool execution with loading/error states
 * - Progress tracking via SSE
 * - Resource and prompt management
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { logger } from '@/lib/logger';
import {
	createMCPClient,
	type MCPClient,
	type MCPClientConfig,
	type MCPPrompt,
	type MCPResource,
	type MCPTool,
	type ProgressNotification,
} from "../api/mcp-client";

/**
 * MCP client hook state
 */
export interface UseMCPState {
	client: MCPClient | null;
	isInitialized: boolean;
	isInitializing: boolean;
	error: Error | null;
	serverInfo: {
		name: string;
		version: string;
		protocolVersion: string;
	} | null;
}

/**
 * Tool execution state
 */
export interface UseToolState<T> {
	data: T | null;
	isLoading: boolean;
	error: Error | null;
	execute: (args?: Record<string, unknown>) => Promise<T | null>;
}

/**
 * Progress tracking state
 */
export interface UseProgressState {
	progress: number;
	total: number | null;
	message: string | null;
	isTracking: boolean;
}

/**
 * Main MCP client hook
 */
export function useMCP(config: MCPClientConfig): UseMCPState {
	const [state, setState] = useState<UseMCPState>({
		client: null,
		isInitialized: false,
		isInitializing: false,
		error: null,
		serverInfo: null,
	});

	const clientRef = useRef<MCPClient | null>(null);

	useEffect(() => {
		let mounted = true;

		async function initializeClient() {
			try {
				setState((prev) => ({ ...prev, isInitializing: true, error: null }));

				const client = createMCPClient(config);
				clientRef.current = client;

				const response = await client.initialize({
					protocolVersion: "2024-11-05",
					capabilities: {
						tools: true,
						resources: true,
						prompts: true,
					},
					clientInfo: {
						name: "TraceRTM Web Client",
						version: "1.0.0",
					},
				});

				if (mounted) {
					setState({
						client,
						isInitialized: true,
						isInitializing: false,
						error: null,
						serverInfo: {
							name: response['serverInfo'].name,
							version: response['serverInfo'].version,
							protocolVersion: response['protocolVersion'],
						},
					});
				}
			} catch (error) {
				if (mounted) {
					setState((prev) => ({
						...prev,
						isInitializing: false,
						error:
							error instanceof Error
								? error
								: new Error("Initialization failed"),
					}));
				}
			}
		}

		void initializeClient();

		return () => {
			mounted = false;
			if (clientRef.current) {
				clientRef.current.close().catch(() => {
					// Ignore errors on cleanup
				});
			}
		};
	}, [config.baseUrl, config.token, config.timeout]);

	return state;
}

/**
 * Hook for executing MCP tools
 */
export function useTool<T = unknown>(
	client: MCPClient | null,
	toolName: string,
): UseToolState<T> {
	const [state, setState] = useState<{
		data: T | null;
		isLoading: boolean;
		error: Error | null;
	}>({
		data: null,
		isLoading: false,
		error: null,
	});

	const execute = useCallback(
		async (args?: Record<string, unknown>): Promise<T | null> => {
			if (!client) {
				const error = new Error("MCP client not initialized");
				setState({ data: null, isLoading: false, error });
				return null;
			}

			try {
				setState({ data: null, isLoading: true, error: null });
				const result = await client.callTool<T>(toolName, args);
				setState({ data: result, isLoading: false, error: null });
				return result;
			} catch (error) {
				const err =
					error instanceof Error ? error : new Error("Tool execution failed");
				setState({ data: null, isLoading: false, error: err });
				return null;
			}
		},
		[client, toolName],
	);

	return {
		...state,
		execute,
	};
}

/**
 * Hook for listing available tools
 */
export function useTools(client: MCPClient | null): {
	tools: MCPTool[];
	isLoading: boolean;
	error: Error | null;
	refresh: () => Promise<void>;
} {
	const [tools, setTools] = useState<MCPTool[]>([]);
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<Error | null>(null);

	const refresh = useCallback(async () => {
		if (!client) {
			setError(new Error("MCP client not initialized"));
			return;
		}

		try {
			setIsLoading(true);
			setError(null);
			const response = await client.listTools();
			setTools(response['tools']);
		} catch (error) {
			setError(error instanceof Error ? error : new Error("Failed to list tools"));
		} finally {
			setIsLoading(false);
		}
	}, [client]);

	useEffect(() => {
		void refresh();
	}, [refresh]);

	return { tools, isLoading, error, refresh };
}

/**
 * Hook for listing available resources
 */
export function useResources(client: MCPClient | null): {
	resources: MCPResource[];
	isLoading: boolean;
	error: Error | null;
	refresh: () => Promise<void>;
} {
	const [resources, setResources] = useState<MCPResource[]>([]);
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<Error | null>(null);

	const refresh = useCallback(async () => {
		if (!client) {
			setError(new Error("MCP client not initialized"));
			return;
		}

		try {
			setIsLoading(true);
			setError(null);
			const response = await client.listResources();
			setResources(response['resources']);
		} catch (error) {
			setError(
				error instanceof Error ? error : new Error("Failed to list resources"),
			);
		} finally {
			setIsLoading(false);
		}
	}, [client]);

	useEffect(() => {
		void refresh();
	}, [refresh]);

	return { resources, isLoading, error, refresh };
}

/**
 * Hook for listing available prompts
 */
export function usePrompts(client: MCPClient | null): {
	prompts: MCPPrompt[];
	isLoading: boolean;
	error: Error | null;
	refresh: () => Promise<void>;
} {
	const [prompts, setPrompts] = useState<MCPPrompt[]>([]);
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<Error | null>(null);

	const refresh = useCallback(async () => {
		if (!client) {
			setError(new Error("MCP client not initialized"));
			return;
		}

		try {
			setIsLoading(true);
			setError(null);
			const response = await client.listPrompts();
			setPrompts(response['prompts']);
		} catch (error) {
			setError(
				error instanceof Error ? error : new Error("Failed to list prompts"),
			);
		} finally {
			setIsLoading(false);
		}
	}, [client]);

	useEffect(() => {
		void refresh();
	}, [refresh]);

	return { prompts, isLoading, error, refresh };
}

/**
 * Hook for tracking progress via SSE
 */
export function useProgress(client: MCPClient | null): UseProgressState & {
	startTracking: () => void;
	stopTracking: () => void;
} {
	const [state, setState] = useState<UseProgressState>({
		progress: 0,
		total: null,
		message: null,
		isTracking: false,
	});

	const unsubscribeRef = useRef<(() => void) | null>(null);

	const startTracking = useCallback(() => {
		if (!client || state.isTracking) return;

		const unsubscribe = client.subscribeToProgress(
			(notification: ProgressNotification) => {
				setState({
					progress: notification.progress,
					total: notification.total || null,
					message: notification.message || null,
					isTracking: true,
				});
			},
			(error: Error) => {
				logger.error("Progress tracking error:", error);
				setState((prev) => ({ ...prev, isTracking: false }));
			},
		);

		unsubscribeRef.current = unsubscribe;
		setState((prev) => ({ ...prev, isTracking: true }));
	}, [client, state.isTracking]);

	const stopTracking = useCallback(() => {
		if (unsubscribeRef.current) {
			unsubscribeRef.current();
			unsubscribeRef.current = null;
		}
		setState({
			progress: 0,
			total: null,
			message: null,
			isTracking: false,
		});
	}, []);

	useEffect(() => {
		return () => {
			if (unsubscribeRef.current) {
				unsubscribeRef.current();
			}
		};
	}, []);

	return {
		...state,
		startTracking,
		stopTracking,
	};
}
