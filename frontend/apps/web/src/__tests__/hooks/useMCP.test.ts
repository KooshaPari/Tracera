/**
 * Tests for MCP React Hooks
 */

import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { MCPClient } from '../../api/mcp-client';

import { useMCP, useTool, useTools } from '../../hooks/useMcp';

// Mock MCP client
vi.mock('../../api/mcp-client', () => ({
  createMCPClient: vi.fn(() => ({
    callTool: vi.fn().mockResolvedValue({ success: true }),
    close: vi.fn().mockResolvedValue(),
    initialize: vi.fn().mockResolvedValue({
      capabilities: {},
      protocolVersion: '2024-11-05',
      serverInfo: {
        name: 'TraceRTM MCP Server',
        version: '1.0.0',
      },
    }),
    listTools: vi.fn().mockResolvedValue({
      tools: [
        {
          description: 'Manage projects',
          name: 'project_manage',
          parameters: [],
        },
      ],
    }),
  })),
}));

describe(useMCP, () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize MCP client', async () => {
    const { result } = renderHook(() =>
      useMCP({
        baseUrl: 'http://localhost:4000',
        token: 'test-token',
      }),
    );

    // Initially not initialized
    expect(result.current.isInitialized).toBeFalsy();
    expect(result.current.isInitializing).toBeTruthy();
    expect(result.current.client).toBeNull();

    // Wait for initialization
    await waitFor(() => {
      expect(result.current.isInitialized).toBeTruthy();
    });

    expect(result.current.isInitializing).toBeFalsy();
    expect(result.current.client).toBeDefined();
    expect(result.current.serverInfo).toEqual({
      name: 'TraceRTM MCP Server',
      protocolVersion: '2024-11-05',
      version: '1.0.0',
    });
    expect(result.current.error).toBeNull();
  });

  it('should handle initialization errors', async () => {
    const { createMCPClient } = await import('../../api/mcp-client');

    (createMCPClient as any).mockReturnValueOnce({
      close: vi.fn().mockResolvedValue(),
      initialize: vi.fn().mockRejectedValue(new Error('Connection failed')),
    });

    const { result } = renderHook(() =>
      useMCP({
        baseUrl: 'http://localhost:4000',
        token: 'test-token',
      }),
    );

    await waitFor(() => {
      expect(result.current.error).toBeDefined();
      expect(result.current.isInitializing).toBeFalsy();
    });

    expect(result.current.isInitialized).toBeFalsy();
    expect(result.current.error?.message).toBe('Connection failed');
  });

  it('should cleanup on unmount', async () => {
    const closeMock = vi.fn().mockResolvedValue();
    const { createMCPClient } = await import('../../api/mcp-client');

    (createMCPClient as any).mockReturnValueOnce({
      close: closeMock,
      initialize: vi.fn().mockResolvedValue({
        capabilities: {},
        protocolVersion: '2024-11-05',
        serverInfo: { name: 'Test', version: '1.0' },
      }),
    });

    const { unmount } = renderHook(() =>
      useMCP({
        baseUrl: 'http://localhost:4000',
        token: 'test-token',
      }),
    );

    await waitFor(() => {
      expect(closeMock).not.toHaveBeenCalled();
    });

    unmount();

    expect(closeMock).toHaveBeenCalled();
  });
});

describe(useTool, () => {
  let mockClient: Partial<MCPClient>;

  beforeEach(() => {
    mockClient = {
      callTool: vi.fn().mockResolvedValue({ result: 'success' }),
    };
  });

  it('should execute tool successfully', async () => {
    const { result } = renderHook(() => useTool(mockClient as MCPClient, 'project_manage'));

    expect(result.current.isLoading).toBeFalsy();
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();

    let data: unknown;
    await act(async () => {
      data = await result.current.execute({ action: 'list' });
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBeFalsy();
    });

    expect(data).toEqual({ result: 'success' });
    expect(result.current.data).toEqual({ result: 'success' });
    expect(result.current.error).toBeNull();
    expect(mockClient.callTool).toHaveBeenCalledWith('project_manage', {
      action: 'list',
    });
  });

  it('should handle tool execution errors', async () => {
    mockClient.callTool = vi.fn().mockRejectedValue(new Error('Tool execution failed'));

    const { result } = renderHook(() => useTool(mockClient as MCPClient, 'project_manage'));

    await act(async () => {
      await result.current.execute({ action: 'list' });
    });

    await waitFor(() => {
      expect(result.current.error).toBeDefined();
    });

    expect(result.current.isLoading).toBeFalsy();
    expect(result.current.data).toBeNull();
    expect(result.current.error?.message).toBe('Tool execution failed');
  });

  it('should handle null client', async () => {
    const { result } = renderHook(() => useTool(null, 'project_manage'));

    let data: unknown;
    await act(async () => {
      data = await result.current.execute({ action: 'list' });
    });

    await waitFor(() => {
      expect(result.current.error).toBeDefined();
    });

    expect(data).toBeNull();
    expect(result.current.error?.message).toBe('MCP client not initialized');
  });
});

describe(useTools, () => {
  let mockClient: Partial<MCPClient>;

  beforeEach(() => {
    mockClient = {
      listTools: vi.fn().mockResolvedValue({
        tools: [
          { description: 'Tool 1', name: 'tool1', parameters: [] },
          { description: 'Tool 2', name: 'tool2', parameters: [] },
        ],
      }),
    };
  });

  it('should list tools on mount', async () => {
    const { result } = renderHook(() => useTools(mockClient as MCPClient));

    expect(result.current.isLoading).toBeTruthy();

    await waitFor(() => {
      expect(result.current.isLoading).toBeFalsy();
    });

    expect(result.current.tools).toHaveLength(2);
    expect(result.current.tools[0]?.name).toBe('tool1');
    expect(result.current.tools[1]?.name).toBe('tool2');
    expect(result.current.error).toBeNull();
  });

  it('should handle list tools errors', async () => {
    mockClient.listTools = vi.fn().mockRejectedValue(new Error('Failed to list tools'));

    const { result } = renderHook(() => useTools(mockClient as MCPClient));

    await waitFor(() => {
      expect(result.current.error).toBeDefined();
      expect(result.current.isLoading).toBeFalsy();
    });
    expect(result.current.tools).toHaveLength(0);
    expect(result.current.error?.message).toBe('Failed to list tools');
  });

  it('should allow manual refresh', async () => {
    const { result } = renderHook(() => useTools(mockClient as MCPClient));

    await waitFor(() => {
      expect(result.current.tools).toHaveLength(2);
    });

    // Clear tools
    const initialListTools = mockClient.listTools as ReturnType<typeof vi.fn>;
    mockClient.listTools = vi.fn().mockResolvedValue({ tools: [] });

    // Refresh
    await act(async () => {
      await result.current.refresh();
    });

    await waitFor(() => {
      expect(result.current.tools).toHaveLength(0);
    });

    await waitFor(() => {
      expect(initialListTools).toHaveBeenCalledOnce();
      expect(mockClient.listTools).toHaveBeenCalledOnce();
    });
  });

  it('should handle null client', async () => {
    const { result } = renderHook(() => useTools(null));

    await waitFor(() => {
      expect(result.current.error).toBeDefined();
    });

    expect(result.current.error?.message).toBe('MCP client not initialized');
    expect(result.current.tools).toHaveLength(0);
  });
});
