import type EventSourcePolyfill from 'event-source-polyfill';

interface JsonRpcRequest {
  id: string | number;
  jsonrpc: '2.0';
  method: string;
  params?: Record<string, unknown> | undefined;
}

interface JsonRpcResponse<TResult = unknown> {
  error?:
    | {
        code: number;
        data?: unknown | undefined;
        message: string;
      }
    | undefined;
  id: string | number;
  jsonrpc: '2.0';
  result?: TResult | undefined;
}

interface MCPToolParam {
  description?: string | undefined;
  default?: unknown | undefined;
  name: string;
  required?: boolean | undefined;
  type: string;
}

interface MCPTool {
  description: string;
  name: string;
  parameters: MCPToolParam[];
}

interface MCPResource {
  description?: string | undefined;
  mimeType?: string | undefined;
  name: string;
  uri: string;
}

interface MCPPrompt {
  arguments?: MCPToolParam[] | undefined;
  description?: string | undefined;
  name: string;
}

interface ProgressNotification {
  message?: string | undefined;
  progress: number;
  total?: number | undefined;
}

interface MCPClientConfig {
  baseUrl: string;
  token?: string | undefined;
  timeout?: number | undefined;
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
