/**
 * React hook for MCP client integration
 *
 * Provides easy-to-use React hooks for:
 * - MCP client lifecycle management
 * - Tool execution with loading/error states
 * - Progress tracking via SSE
 * - Resource and prompt management
 */

import { useCallback, useEffect, useRef, useState } from 'react';

import { logger } from '@/lib/logger';

import type {
  MCPClient,
  MCPClientConfig,
  MCPPrompt,
  MCPResource,
  MCPTool,
  ProgressNotification,
} from '../api/mcp-client';

import { createMCPClient } from '../api/mcp-client';

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
export const useMCP = (config: MCPClientConfig): UseMCPState => {
  const [state, setState] = useState<UseMCPState>({
    client: null,
    error: null,
    isInitialized: false,
    isInitializing: false,
    serverInfo: null,
  });

  const clientRef = useRef<MCPClient | null>(null);

  useEffect(() => {
    let mounted = true;

    const initializeClient = async () => {
      try {
        setState((prev) => ({ ...prev, isInitializing: true, error: null }));

        const client = createMCPClient(config);
        clientRef.current = client;

        const response = await client.initialize({
          capabilities: {
            prompts: true,
            resources: true,
            tools: true,
          },
          clientInfo: {
            name: 'TraceRTM Web Client',
            version: '1.0.0',
          },
          protocolVersion: '2024-11-05',
        });

        if (mounted) {
          setState({
            client,
            error: null,
            isInitialized: true,
            isInitializing: false,
            serverInfo: {
              name: response['serverInfo'].name,
              protocolVersion: response['protocolVersion'],
              version: response['serverInfo'].version,
            },
          });
        }
      } catch (error) {
        if (mounted) {
          setState((prev) => ({
            ...prev,
            isInitializing: false,
            error: error instanceof Error ? error : new Error('Initialization failed'),
          }));
        }
      }
    };

    initializeClient();

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
};

/**
 * Hook for executing MCP tools
 */
export const useTool = <T = unknown>(
  client: MCPClient | null,
  toolName: string,
): UseToolState<T> => {
  const [state, setState] = useState<{
    data: T | null;
    isLoading: boolean;
    error: Error | null;
  }>({
    data: null,
    error: null,
    isLoading: false,
  });

  const execute = useCallback(
    async (args?: Record<string, unknown>): Promise<T | null> => {
      if (!client) {
        const error = new Error('MCP client not initialized');
        setState({ data: null, error, isLoading: false });
        return null;
      }

      try {
        setState({ data: null, error: null, isLoading: true });
        const result = await client.callTool<T>(toolName, args);
        setState({ data: result, error: null, isLoading: false });
        return result;
      } catch (error) {
        const err = error instanceof Error ? error : new Error('Tool execution failed');
        setState({ data: null, error: err, isLoading: false });
        return null;
      }
    },
    [client, toolName],
  );

  return {
    ...state,
    execute,
  };
};

/**
 * Hook for listing available tools
 */
export const useTools = (
  client: MCPClient | null,
): {
  tools: MCPTool[];
  isLoading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
} => {
  const [tools, setTools] = useState<MCPTool[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    if (!client) {
      setError(new Error('MCP client not initialized'));
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      const response = await client.listTools();
      setTools(response['tools']);
    } catch (error) {
      setError(error instanceof Error ? error : new Error('Failed to list tools'));
    } finally {
      setIsLoading(false);
    }
  }, [client]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { error, isLoading, refresh, tools };
};

/**
 * Hook for listing available resources
 */
export const useResources = (
  client: MCPClient | null,
): {
  resources: MCPResource[];
  isLoading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
} => {
  const [resources, setResources] = useState<MCPResource[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    if (!client) {
      setError(new Error('MCP client not initialized'));
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      const response = await client.listResources();
      setResources(response['resources']);
    } catch (error) {
      setError(error instanceof Error ? error : new Error('Failed to list resources'));
    } finally {
      setIsLoading(false);
    }
  }, [client]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { error, isLoading, refresh, resources };
};

/**
 * Hook for listing available prompts
 */
export const usePrompts = (
  client: MCPClient | null,
): {
  prompts: MCPPrompt[];
  isLoading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
} => {
  const [prompts, setPrompts] = useState<MCPPrompt[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    if (!client) {
      setError(new Error('MCP client not initialized'));
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      const response = await client.listPrompts();
      setPrompts(response['prompts']);
    } catch (error) {
      setError(error instanceof Error ? error : new Error('Failed to list prompts'));
    } finally {
      setIsLoading(false);
    }
  }, [client]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { error, isLoading, prompts, refresh };
};

/**
 * Hook for tracking progress via SSE
 */
export const useProgress = (
  client: MCPClient | null,
): UseProgressState & {
  startTracking: () => void;
  stopTracking: () => void;
} => {
  const [state, setState] = useState<UseProgressState>({
    isTracking: false,
    message: null,
    progress: 0,
    total: null,
  });

  const unsubscribeRef = useRef<(() => void) | null>(null);

  const startTracking = useCallback(() => {
    if (!client || state.isTracking) {
      return;
    }

    const unsubscribe = client.subscribeToProgress({
      onProgress: (notification: ProgressNotification) => {
        setState({
          isTracking: true,
          message: notification.message ?? null,
          progress: notification.progress,
          total: notification.total ?? null,
        });
      },
      onError: (error: Error) => {
        logger.error('Progress tracking error:', error);
        setState((prev) => ({ ...prev, isTracking: false }));
      },
    });

    unsubscribeRef.current = unsubscribe;
    setState((prev) => ({ ...prev, isTracking: true }));
  }, [client, state.isTracking]);

  const stopTracking = useCallback(() => {
    if (unsubscribeRef.current) {
      unsubscribeRef.current();
      unsubscribeRef.current = null;
    }
    setState({
      isTracking: false,
      message: null,
      progress: 0,
      total: null,
    });
  }, []);

  useEffect(
    () => () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }
    },
    [],
  );

  return {
    ...state,
    startTracking,
    stopTracking,
  };
};
