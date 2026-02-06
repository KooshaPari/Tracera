import type EventSourcePolyfill from 'event-source-polyfill';

interface JsonRpcRequest {
  id: string | number;
  jsonrpc: '2.0';
  method: string;
  params?: Record<string, unknown>;
}

interface JsonRpcResponse<TResult = unknown> {
  error?: {
    code: number;
    data?: unknown;
    message: string;
  };
  id: string | number;
  jsonrpc: '2.0';
  result?: TResult;
}

interface MCPToolParam {
  description?: string;
  default?: unknown;
  name: string;
  required?: boolean;
  type: string;
}

interface MCPTool {
  description: string;
  name: string;
  parameters: MCPToolParam[];
}

interface MCPResource {
  description?: string;
  mimeType?: string;
  name: string;
  uri: string;
}

interface MCPPrompt {
  arguments?: MCPToolParam[];
  description?: string;
  name: string;
}

interface ProgressNotification {
  message?: string;
  progress: number;
  total?: number;
}

interface MCPClientConfig {
  baseUrl: string;
  token?: string;
  timeout?: number;
}

type MCPEventSource = InstanceType<typeof EventSourcePolyfill>;

interface MCPClientTypes {
  JsonRpcRequest: JsonRpcRequest;
  JsonRpcResponse: JsonRpcResponse;
  MCPClientConfig: MCPClientConfig;
  MCPEventSource: MCPEventSource;
  MCPPrompt: MCPPrompt;
  MCPResource: MCPResource;
  MCPTool: MCPTool;
  MCPToolParam: MCPToolParam;
  ProgressNotification: ProgressNotification;
}

export type {
  JsonRpcRequest,
  JsonRpcResponse,
  MCPClientConfig,
  MCPClientTypes,
  MCPEventSource,
  MCPPrompt,
  MCPResource,
  MCPTool,
  MCPToolParam,
  ProgressNotification,
};
