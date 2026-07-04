import type {
  JsonRpcRequest,
  JsonRpcResponse,
  MCPClientConfig,
  ProgressNotification,
} from './mcp-client-types';

type JsonRecord = Record<string, unknown>;

interface ProgressCallbacks {
  onError?: ((error: Error) => void) | undefined;
  onProgress: (notification: ProgressNotification) => void;
}

interface MCPClientState {
  baseUrl: string;
  requestId: number;
  timeout: number;
  token?: string | undefined;
}

const DEFAULT_TIMEOUT_MS = 30_000;
const INITIAL_REQUEST_ID = 0;

const isRecord = (value: unknown): value is JsonRecord =>
  typeof value === 'object' && value !== null;

const isNonEmptyString = (value: string | undefined): value is string =>
  typeof value === 'string' && value.trim().length > 0;

const parseJson = (raw: string): unknown => JSON.parse(raw);

const parseProgressNotification = (data: unknown): ProgressNotification | undefined => {
  if (!isRecord(data)) {
    return undefined;
  }

  const messageVal = data['message'];
  const progressVal = data['progress'];
  const totalVal = data['total'];

  if (typeof progressVal !== 'number') {
    return undefined;
  }

  if (messageVal !== undefined && typeof messageVal !== 'string') {
    return undefined;
  }

  if (totalVal !== undefined && typeof totalVal !== 'number') {
    return undefined;
  }

  const notification: ProgressNotification = {
    progress: progressVal,
  };
  if (messageVal !== undefined) {
    notification.message = messageVal;
  }
  if (totalVal !== undefined) {
    notification.total = totalVal;
  }
  return notification;
};

const parseJsonRpcResponse = <TResult>(data: unknown): JsonRpcResponse<TResult> => {
  if (!isRecord(data)) {
    throw new TypeError('Invalid JSON-RPC response: expected object');
  }

  const { error, id, jsonrpc, result } = data;

  if (jsonrpc !== '2.0') {
    throw new TypeError('Invalid JSON-RPC response: invalid version');
  }

  if (typeof id !== 'string' && typeof id !== 'number') {
    throw new TypeError('Invalid JSON-RPC response: invalid id');
  }

  if (error !== undefined) {
    if (!isRecord(error)) {
      throw new TypeError('Invalid JSON-RPC response: error is invalid');
    }

    const errorCode = error['code'];
    const errorMessage = error['message'];

    if (typeof errorCode !== 'number' || typeof errorMessage !== 'string') {
      throw new TypeError('Invalid JSON-RPC response: error is invalid');
    }
  }

  const response: JsonRpcResponse<TResult> = {
    id,
    jsonrpc: '2.0',
    result: result as TResult,
  };
  if (error !== undefined) {
    response.error = error as NonNullable<JsonRpcResponse<TResult>['error']>;
  }
  return response;
};

const createMcpState = (config: MCPClientConfig): MCPClientState => ({
  baseUrl: config.baseUrl.replace(/\/$/, ''),
  requestId: INITIAL_REQUEST_ID,
  timeout: config.timeout ?? DEFAULT_TIMEOUT_MS,
  token: config.token,
});

const createRequestPayload = (
  requestId: number,
  method: string,
  params?: Record<string, unknown>,
): JsonRpcRequest => {
  const request: JsonRpcRequest = {
    id: requestId,
    jsonrpc: '2.0',
    method,
  };
  if (params !== undefined) {
    request.params = params;
  }
  return request;
};

const createHeaders = (token: string | undefined): Record<string, string> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (isNonEmptyString(token)) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
};

const parseResponse = async <TResult>(response: Response): Promise<TResult> => {
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const rawData = (await response.json()) as unknown;
  const data = parseJsonRpcResponse<TResult>(rawData);

  if (data.error !== undefined) {
    throw new Error(`JSON-RPC Error ${data.error.code}: ${data.error.message}`);
  }

  if (data.result === undefined) {
    throw new TypeError('Invalid JSON-RPC response: missing result');
  }

  return data.result as TResult;
};

const handleProgressError = (callbacks: ProgressCallbacks, error: unknown): void => {
  if (callbacks.onError === undefined) {
    return;
  }

  if (error instanceof Error) {
    callbacks.onError(error);
    return;
  }

  callbacks.onError(new Error('Failed to parse progress'));
};

const mcpClientUtils = {
  createHeaders,
  createMcpState,
  createRequestPayload,
  handleProgressError,
  isNonEmptyString,
  parseJson,
  parseJsonRpcResponse,
  parseProgressNotification,
  parseResponse,
};

export { mcpClientUtils, type MCPClientState, type ProgressCallbacks };
