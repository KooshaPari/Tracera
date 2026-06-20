import EventSourcePolyfill from 'event-source-polyfill';

import type {
  JsonRpcRequest,
  JsonRpcResponse,
  MCPClientConfig,
  MCPEventSource,
  MCPPrompt,
  MCPResource,
  MCPTool,
  ProgressNotification,
} from './mcp-client-types';
import type { MCPClientState, ProgressCallbacks } from './mcp-client-utils';

import { mcpClientUtils } from './mcp-client-utils';

interface InitializeResponse {
  capabilities: Record<string, unknown>;
  protocolVersion: string;
  serverInfo: { name: string; version: string };
}

interface InitializeParams {
  capabilities?: Record<string, unknown> | undefined;
  clientInfo?: { name: string; version: string } | undefined;
  protocolVersion?: string | undefined;
}

class MCPClient {
  private state: MCPClientState;

  constructor(config: MCPClientConfig) {
    this.state = mcpClientUtils.createMcpState(config);
  }

  setToken(token: string): void {
    this.state.token = token;
  }

  private nextRequestId(): number {
    this.state.requestId += 1;
    return this.state.requestId;
  }

  private buildRequestPayload(method: string, params?: Record<string, unknown>): JsonRpcRequest {
    return mcpClientUtils.createRequestPayload(this.nextRequestId(), method, params);
  }

  private async sendRequest<TResult>(
    method: string,
    params?: Record<string, unknown>,
  ): Promise<TResult> {
    const request = this.buildRequestPayload(method, params);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      controller.abort();
    }, this.state.timeout);

    try {
      const response = await fetch(`${this.state.baseUrl}/mcp/rpc`, {
        body: JSON.stringify(request),
        headers: mcpClientUtils.createHeaders(this.state.token),
        method: 'POST',
        signal: controller.signal,
      });

      return mcpClientUtils.parseResponse<TResult>(response);
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new Error('Request timeout', { cause: error });
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  async initialize(params?: InitializeParams): Promise<InitializeResponse> {
    return this.sendRequest('initialize', params as Record<string, unknown> | undefined);
  }

  async listTools(): Promise<{ tools: MCPTool[] }> {
    return this.sendRequest('tools/list');
  }

  async callTool<TResult = unknown>(
    name: string,
    args?: Record<string, unknown>,
  ): Promise<TResult> {
    return this.sendRequest('tools/call', { arguments: args, name });
  }

  async listResources(): Promise<{ resources: MCPResource[] }> {
    return this.sendRequest('resources/list');
  }

  async readResource(uri: string): Promise<{ contents: unknown }> {
    return this.sendRequest('resources/read', { uri });
  }

  async listPrompts(): Promise<{ prompts: MCPPrompt[] }> {
    return this.sendRequest('prompts/list');
  }

  async getPrompt(name: string, args?: Record<string, unknown>): Promise<{ messages: unknown[] }> {
    return this.sendRequest('prompts/get', { arguments: args, name });
  }

  subscribeToProgress(callbacks: ProgressCallbacks): () => void {
    const headers: Record<string, string> = {};

    if (mcpClientUtils.isNonEmptyString(this.state.token)) {
      headers['Authorization'] = `Bearer ${this.state.token}`;
    }

    const eventSource: MCPEventSource = new EventSourcePolyfill(
      `${this.state.baseUrl}/mcp/progress`,
      { headers },
    );

    eventSource.onmessage = (event: MessageEvent): void => {
      try {
        const parsed = mcpClientUtils.parseJson(event.data);
        const notification = mcpClientUtils.parseProgressNotification(parsed);

        if (!notification) {
          mcpClientUtils.handleProgressError(callbacks, new Error('Invalid progress payload'));
          return;
        }

        callbacks.onProgress(notification);
      } catch (error) {
        mcpClientUtils.handleProgressError(callbacks, error);
      }
    };

    eventSource.onerror = (_error: Event): void => {
      if (callbacks.onError !== undefined) {
        callbacks.onError(new Error('SSE connection error'));
      }
    };

    return () => {
      eventSource.close();
    };
  }

  async close(): Promise<void> {
    try {
      await fetch(`${this.state.baseUrl}/mcp/rpc`, {
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'notifications/cancelled',
          params: {},
        }),
        headers: mcpClientUtils.createHeaders(this.state.token),
        method: 'POST',
      });
    } catch {
      return;
    }
  }
}

const createMCPClient = (config: MCPClientConfig): MCPClient => new MCPClient(config);

export {
  MCPClient,
  createMCPClient,
  type JsonRpcRequest,
  type JsonRpcResponse,
  type MCPClientConfig,
  type MCPPrompt,
  type MCPResource,
  type MCPTool,
  type ProgressNotification,
};
