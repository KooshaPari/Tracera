/* oxlint-disable import/no-named-export, promise/prefer-await-to-callbacks, promise/prefer-await-to-then, eslint/max-lines, eslint/no-undefined, oxc/no-async-await */
// WebSocket Real-time Connection Manager
import { logger } from '@/lib/logger';

import { clientCore } from './client-core';

const { API_BASE_URL } = clientCore;

const AUTH_CLOSE_CODE = 1008;
const AUTH_TIMEOUT_MS = 5000;
const DEFAULT_RECONNECT_DELAY_MS = 1000;
const DEFAULT_MAX_RECONNECT_DELAY_MS = 30_000;
const DEFAULT_MAX_RECONNECT_ATTEMPTS = 10;
const DEFAULT_HEARTBEAT_INTERVAL_MS = 30_000;
const DEFAULT_MESSAGE_QUEUE_LIMIT = 100;
const RECONNECT_BACKOFF_BASE = 2;
const RECONNECT_ATTEMPT_INCREMENT = 1;
const RECONNECT_ATTEMPT_OFFSET = 1;
const RECONNECT_JITTER_MS = 1000;
const ZERO = 0;

/**
 * Record data from database table
 */
type DatabaseRecord = Record<string, unknown>;

interface RealtimeEvent {
  type: 'created' | 'updated' | 'deleted';
  table: 'projects' | 'items' | 'links';
  schema: string;
  record: DatabaseRecord;
  timestamp: number;
}

interface AuthMessage {
  token: string;
  type: 'auth';
}

interface AuthResponse {
  type: 'auth_success' | 'auth_failed';
  message?: string;
}

type EventCallback = (event: RealtimeEvent) => void;

type TokenGetter = () => string | undefined | Promise<string | undefined>;

type ParsedMessage = Record<string, unknown>;
type TimeoutHandle = ReturnType<typeof globalThis.setTimeout>;
type IntervalHandle = ReturnType<typeof globalThis.setInterval>;

const isRecordObject = (value: unknown): value is Record<string, unknown> =>
  Object.prototype.toString.call(value) === '[object Object]';

const isRealtimeEvent = (value: unknown): value is RealtimeEvent => {
  if (!isRecordObject(value)) {
    return false;
  }

  const eventType = value['type'];
  const { table } = value;
  const { schema } = value;
  const { record } = value;
  const { timestamp } = value;

  if (eventType !== 'created' && eventType !== 'updated' && eventType !== 'deleted') {
    return false;
  }

  if (table !== 'projects' && table !== 'items' && table !== 'links') {
    return false;
  }

  return typeof schema === 'string' && isRecordObject(record) && typeof timestamp === 'number';
};

class WebSocketManager {
  private ws: WebSocket | undefined;
  private reconnectAttempts = ZERO;
  private readonly maxReconnectAttempts = DEFAULT_MAX_RECONNECT_ATTEMPTS;
  private readonly reconnectDelay = DEFAULT_RECONNECT_DELAY_MS;
  private readonly maxReconnectDelay = DEFAULT_MAX_RECONNECT_DELAY_MS;
  private subscriptions = new Map<string, Set<EventCallback>>();
  private isConnecting = false;
  private isConnected = false;
  private isAuthenticated = false;
  private heartbeatInterval: IntervalHandle | undefined;
  private baseUrl: string;
  private getToken: TokenGetter | undefined;
  private authTimeout: TimeoutHandle | undefined;
  private token: string | undefined;
  private messageQueue: unknown[] = [];

  constructor(getToken?: TokenGetter) {
    if (globalThis.window === undefined) {
      throw new TypeError('WebSocketManager requires a browser environment');
    }
    const wsProtocol = WebSocketManager.getWebSocketProtocol();
    const envWsUrl = import.meta.env?.VITE_WS_URL;
    const rawBaseUrl =
      typeof envWsUrl === 'string' && envWsUrl.trim() !== '' ? envWsUrl.trim() : API_BASE_URL;
    const wsBase = rawBaseUrl.replace(/^https?:/, wsProtocol).replace(/\/$/, '');
    const wsPath = wsBase.includes('/api/v1/ws') ? wsBase : `${wsBase}/api/v1/ws`;
    // Server requires project_id query parameter; use 'global' as default for app-level connections
    this.baseUrl = wsPath.includes('?')
      ? `${wsPath}&project_id=global`
      : `${wsPath}?project_id=global`;
    this.getToken = getToken;
  }

  async connect(): Promise<void> {
    if (this.isSocketOpen() || this.isConnecting) {
      return;
    }

    this.beginConnect();

    try {
      const token = await this.resolveToken();
      this.handleResolvedToken(token);
    } catch (error: unknown) {
      this.handleConnectionFailure(error);
    }
  }

  disconnect(): void {
    this.stopHeartbeat();
    this.clearAuthTimeout();
    this.closeSocket();
    this.isConnected = false;
    this.isAuthenticated = false;
    this.isConnecting = false;
    this.token = undefined;
    this.messageQueue = [];
  }

  subscribe(channel: string, listener: EventCallback): () => void {
    this.addSubscription(channel, listener);
    this.sendSubscription(channel);

    return (): void => {
      this.removeSubscription(channel, listener);
    };
  }

  get connected(): boolean {
    return this.isConnected;
  }

  setTokenGetter(getToken?: TokenGetter): void {
    this.getToken = getToken;
  }

  private static getWebSocketProtocol(): string {
    const windowRef = globalThis.window;
    if (typeof windowRef !== 'undefined') {
      if (windowRef.location.protocol === 'https:') {
        return 'wss:';
      }
    }
    return 'ws:';
  }

  private beginConnect(): void {
    this.isConnecting = true;
    this.isAuthenticated = false;
  }

  private async resolveToken(): Promise<string | undefined> {
    if (typeof this.getToken === 'undefined') {
      return undefined;
    }

    try {
      const tokenResult = await this.getToken();
      if (typeof tokenResult === 'string' && tokenResult !== '') {
        return tokenResult;
      }
      return undefined;
    } catch (error: unknown) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Failed to resolve token', { cause: error });
    }
  }

  private handleResolvedToken(token: string | undefined): void {
    if (typeof token === 'undefined' || token === '') {
      this.handleMissingToken();
      return;
    }

    this.token = token;
    this.openSocket();
  }

  private handleMissingToken(): void {
    logger.error('[WebSocket] Authentication token required. Please authenticate first.');
    this.isConnecting = false;
  }

  private openSocket(): void {
    try {
      this.ws = new WebSocket(this.baseUrl);
      this.attachSocketHandlers();
    } catch (connectionError: unknown) {
      this.handleConnectionFailure(connectionError);
    }
  }

  private attachSocketHandlers(): void {
    if (!this.ws) {
      return;
    }

    this.ws.onopen = (): void => {
      this.handleOpen();
    };
    this.ws.onmessage = (event: MessageEvent): void => {
      this.handleMessage(event.data);
    };
    this.ws.onerror = (error: Event): void => {
      this.handleError(error);
    };
    this.ws.onclose = (event): void => {
      this.handleClose(event);
    };
  }

  private handleOpen(): void {
    logger.info('[WebSocket] Connection established, waiting for authentication');
    this.isConnecting = false;
    this.reconnectAttempts = ZERO;
    this.sendAuthMessage();
    this.startAuthTimeout();
  }

  private handleMessage(data: unknown): void {
    const message = WebSocketManager.parseMessage(data);
    if (!message) {
      return;
    }

    if (this.handleAuthMessage(message)) {
      return;
    }

    if (this.handleBatchMessage(message)) {
      return;
    }

    this.handleRealtimeMessage(message);
  }

  private static parseMessage(data: unknown): ParsedMessage | undefined {
    if (typeof data !== 'string') {
      return undefined;
    }

    try {
      const parsed = JSON.parse(data);
      if (isRecordObject(parsed)) {
        return parsed;
      }
    } catch (parseError: unknown) {
      logger.error('[WebSocket] Failed to parse message:', parseError);
      return undefined;
    }

    return undefined;
  }

  private handleAuthMessage(message: ParsedMessage): boolean {
    const messageType = message['type'];
    if (messageType === 'auth_success') {
      this.handleAuthSuccess();
      return true;
    }
    if (messageType === 'auth_failed') {
      const authMessage = WebSocketManager.extractAuthFailureMessage(message);
      this.handleAuthFailure(authMessage);
      return true;
    }
    return false;
  }

  private static extractAuthFailureMessage(message: ParsedMessage): string | undefined {
    const msg = message['message'];
    if (typeof msg === 'string') {
      return msg;
    }
    return undefined;
  }

  private handleAuthSuccess(): void {
    logger.info('[WebSocket] Authentication successful');
    this.isAuthenticated = true;
    this.isConnected = true;
    this.clearAuthTimeout();
    this.startHeartbeat();
    this.flushMessageQueue();
  }

  private handleAuthFailure(message: string | undefined): void {
    logger.error('[WebSocket] Authentication failed:', message);
    this.isAuthenticated = false;
    this.isConnected = false;
    this.clearAuthTimeout();
    this.closeSocketWithAuthError('Authentication failed');
  }

  private handleBatchMessage(message: ParsedMessage): boolean {
    const msgType = message['type'];
    const msgList = message['messages'];
    if (msgType !== 'batch' || !Array.isArray(msgList)) {
      return false;
    }

    for (const msg of msgList) {
      if (this.isAuthenticated && isRealtimeEvent(msg)) {
        this.handleEvent(msg);
      }
    }
    return true;
  }

  private handleRealtimeMessage(message: ParsedMessage): void {
    if (!this.isAuthenticated) {
      return;
    }

    const msgType = message['type'];
    if (msgType === 'auth') {
      return;
    }

    if (isRealtimeEvent(message)) {
      this.handleEvent(message);
    }
  }

  private handleError(error: unknown): void {
    logger.error('[WebSocket] Error:', error);
    this.isConnected = false;
    this.isAuthenticated = false;
  }

  private handleClose(event: CloseEvent): void {
    logger.info('[WebSocket] Disconnected', {
      code: event.code,
      reason: event.reason,
    });
    this.isConnected = false;
    this.isAuthenticated = false;
    this.isConnecting = false;
    this.stopHeartbeat();
    this.clearAuthTimeout();

    if (WebSocketManager.isAuthFailureClose(event)) {
      logger.error('[WebSocket] Authentication failed. Please re-authenticate.');
      return;
    }

    this.attemptReconnect();
  }

  private static isAuthFailureClose(event: CloseEvent): boolean {
    if (event.code !== AUTH_CLOSE_CODE) {
      return false;
    }
    if (event.reason === '') {
      return false;
    }
    return event.reason.includes('Authentication');
  }

  private handleConnectionFailure(error: unknown): void {
    logger.error('[WebSocket] Connection failed:', error);
    this.isConnecting = false;
    this.attemptReconnect();
  }

  private sendAuthMessage(): void {
    const socket = this.ws;
    if (
      !socket ||
      socket.readyState !== WebSocket.OPEN ||
      typeof this.token === 'undefined' ||
      this.token === ''
    ) {
      logger.error('[WebSocket] Cannot send auth message: connection not ready');
      return;
    }

    const authMessage: AuthMessage = {
      token: this.token,
      type: 'auth',
    };

    try {
      socket.send(JSON.stringify(authMessage));
      logger.info('[WebSocket] Auth message sent');
    } catch (sendError: unknown) {
      logger.error('[WebSocket] Failed to send auth message:', sendError);
    }
  }

  private closeSocketWithAuthError(reason: string): void {
    const socket = this.ws;
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return;
    }
    socket.close(AUTH_CLOSE_CODE, reason);
  }

  private closeSocket(): void {
    if (!this.ws) {
      return;
    }
    this.ws.close();
    this.ws = undefined;
  }

  private startAuthTimeout(): void {
    this.clearAuthTimeout();
    this.authTimeout = globalThis.setTimeout((): void => {
      logger.error('[WebSocket] Authentication timeout');
      this.closeSocketWithAuthError('Authentication timeout');
    }, AUTH_TIMEOUT_MS);
  }

  private clearAuthTimeout(): void {
    if (this.authTimeout === undefined) {
      return;
    }
    globalThis.clearTimeout(this.authTimeout);
    this.authTimeout = undefined;
  }

  private addSubscription(channel: string, listener: EventCallback): void {
    if (!this.subscriptions.has(channel)) {
      this.subscriptions.set(channel, new Set());
    }
    const callbacks = this.subscriptions.get(channel);
    if (typeof callbacks !== 'undefined') {
      callbacks.add(listener);
    }
  }

  private sendSubscription(channel: string): void {
    if (!this.isAuthenticated || typeof this.ws === 'undefined') {
      return;
    }
    this.send({ channel, type: 'subscribe' });
  }

  private removeSubscription(channel: string, listener: EventCallback): void {
    const callbacks = this.subscriptions.get(channel);
    if (typeof callbacks === 'undefined') {
      return;
    }

    callbacks.delete(listener);
    if (callbacks.size !== ZERO) {
      return;
    }

    this.subscriptions.delete(channel);
    if (this.isAuthenticated && typeof this.ws !== 'undefined') {
      this.send({ channel, type: 'unsubscribe' });
    }
  }

  private handleEvent(event: RealtimeEvent): void {
    const channel = `${event.table}:${event.type}`;
    const allChannel = `${event.table}:*`;
    const globalChannel = '*';
    const channels = [channel, allChannel, globalChannel];

    for (const channelName of channels) {
      const callbacks = this.subscriptions.get(channelName);
      if (callbacks) {
        for (const listener of callbacks) {
          WebSocketManager.runCallback(channelName, listener, event);
        }
      }
    }
  }

  private static runCallback(channel: string, listener: EventCallback, event: RealtimeEvent): void {
    try {
      listener(event);
    } catch (callbackError: unknown) {
      logger.error(`[WebSocket] Error in callback for ${channel}:`, callbackError);
    }
  }

  private send(data: unknown): void {
    if (this.isSocketOpen() && this.isAuthenticated) {
      this.sendImmediate(data);
      return;
    }

    this.queueMessage(data);
  }

  private sendImmediate(data: unknown): void {
    if (!this.ws) {
      return;
    }

    try {
      this.ws.send(JSON.stringify(data));
    } catch (error: unknown) {
      logger.error('[WebSocket] Failed to send message:', error);
      this.queueMessage(data);
    }
  }

  private queueMessage(data: unknown): void {
    this.messageQueue.push(data);
    if (this.messageQueue.length <= DEFAULT_MESSAGE_QUEUE_LIMIT) {
      return;
    }

    this.messageQueue.shift();
    logger.warn('[WebSocket] Message queue overflow, dropping oldest message');
  }

  private flushMessageQueue(): void {
    if (this.messageQueue.length === ZERO) {
      return;
    }

    logger.info(`[WebSocket] Flushing ${this.messageQueue.length} queued messages`);

    const messages = [...this.messageQueue];
    this.messageQueue = [];

    for (const message of messages) {
      this.send(message);
    }
  }

  private startHeartbeat(): void {
    if (globalThis.window === undefined) {
      return;
    }

    this.heartbeatInterval = globalThis.setInterval((): void => {
      if (this.isSocketOpen()) {
        this.send({ type: 'ping' });
      }
    }, DEFAULT_HEARTBEAT_INTERVAL_MS);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval === undefined) {
      return;
    }
    globalThis.clearInterval(this.heartbeatInterval);
    this.heartbeatInterval = undefined;
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      logger.error('[WebSocket] Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts += RECONNECT_ATTEMPT_INCREMENT;
    const delay = this.getReconnectDelay();

    logger.info(
      `[WebSocket] Reconnecting in ${Math.round(delay)}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`,
    );

    globalThis.setTimeout((): void => {
      this.connect().catch((error: unknown) => {
        logger.error('[WebSocket] Reconnection failed:', error);
      });
    }, delay);
  }

  private getReconnectDelay(): number {
    const exponent = this.reconnectAttempts - RECONNECT_ATTEMPT_OFFSET;
    const exponentialDelay = this.reconnectDelay * RECONNECT_BACKOFF_BASE ** exponent;
    const jitter = Math.random() * RECONNECT_JITTER_MS;
    return Math.min(exponentialDelay + jitter, this.maxReconnectDelay);
  }

  private isSocketOpen(): boolean {
    return typeof this.ws !== 'undefined' && this.ws.readyState === WebSocket.OPEN;
  }
}

// Singleton instance
// oxlint-disable-next-line eslint/init-declarations
let wsManager: WebSocketManager | undefined;

const getWebSocketManager = (getToken?: TokenGetter): WebSocketManager => {
  if (!wsManager) {
    wsManager = new WebSocketManager(getToken);
    return wsManager;
  }

  if (getToken) {
    wsManager.setTokenGetter(getToken);
  }

  return wsManager;
};

const connectWebSocket = async (getToken?: TokenGetter): Promise<void> => {
  await getWebSocketManager(getToken).connect();
};

const disconnectWebSocket = (): void => {
  getWebSocketManager().disconnect();
};

const subscribeToChannel = (channel: string, listener: EventCallback): (() => void) =>
  getWebSocketManager().subscribe(channel, listener);

export {
  connectWebSocket,
  disconnectWebSocket,
  getWebSocketManager,
  subscribeToChannel,
  WebSocketManager,
  type AuthMessage,
  type AuthResponse,
  type DatabaseRecord,
  type EventCallback,
  type RealtimeEvent,
};
