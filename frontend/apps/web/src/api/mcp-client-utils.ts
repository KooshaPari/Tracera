import type {
  JsonRpcRequest,
  JsonRpcResponse,
  MCPClientConfig,
  ProgressNotification,
} from './mcp-client-types';

type JsonRecord = Record<string, unknown>;

interface ProgressCallbacks {
  onError?: (error: Error) => void;
  onProgress: (notification: ProgressNotification) => void;
}

interface MCPClientState {
  baseUrl: string;
  requestId: number;
  timeout: number;
  token?: string;
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

  return {
    message: messageVal as string | undefined,
    progress: progressVal,
    total: totalVal as number | undefined,
  };
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

  return {
    error: error as JsonRpcResponse<TResult>['error'],
    id,
    jsonrpc: '2.0',
    result: result as TResult,
  };
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
): JsonRpcRequest => ({
  id: requestId,
  jsonrpc: '2.0',
  method,
  params,
});

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
