import { logger } from '@/lib/logger';
/**
 * Real-time WebSocket Client for NATS Event Propagation
 *
 * Connects to Go backend WebSocket endpoint and receives NATS events
 * for real-time UI updates.
 */

export type NATSEventMessage = {
  type: 'nats_event';
  data: {
    event_type: string;
    project_id: string;
    entity_id: string;
    entity_type: string;
    data: Record<string, unknown>;
    timestamp: string;
    source: string; // "go" or "python"
  };
  timestamp: string;
};

export type WebSocketMessage =
  | NATSEventMessage
  | { type: 'pong'; timestamp: string }
  | { type: 'auth_success'; message?: string }
  | { type: 'auth_failed'; message?: string }
  | {
      type: 'subscription_confirmed';
      data: { project_id: string };
      timestamp: string;
    }
  | { type: 'error'; message: string };

export type EventListener = (data: NATSEventMessage['data']) => void;

export class RealtimeClient {
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private pingInterval: NodeJS.Timeout | null = null;
  private listeners = new Map<string, Set<EventListener>>();
  private currentProjectID: string | null = null;
  private token: string | null = null;
  private isAuthenticated = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 5000; // 5 seconds

  constructor(private url: string = 'ws://localhost:4000/api/v1/ws') {
    // Use gateway host (same as API) so ws connects to :4000, not the frontend origin (:5173)
    if (typeof window !== 'undefined') {
      const base = import.meta.env?.VITE_API_URL || 'http://localhost:4000';
      const wsBase = import.meta.env?.VITE_WS_URL || base.replace(/^http/, 'ws');
      this.url = `${wsBase.replace(/\/$/, '')}/api/v1/ws`;
    }
  }

  /**
   * Connect to WebSocket with authentication token and optional project ID
   * SECURITY: Token is sent in auth message, never in URL
   */
  connect(token: string, projectID?: string) {
    this.token = token;
    this.currentProjectID = projectID || null;
    logger.info(`[WebSocket] connect() called with projectID: ${projectID || 'undefined'}`);

    if (this.ws?.readyState === WebSocket.OPEN) {
      // Already connected, re-authenticate with new token
      if (token !== this.token) {
        logger.info('[WebSocket] Token changed, re-authenticating');
        this.sendAuth();
      }
      // Subscribe to project if needed
      if (projectID && projectID !== this.currentProjectID) {
        this.subscribeToProject(projectID);
      }
      return;
    }

    this.doConnect();
  }

  private doConnect() {
    logger.info(
      `[WebSocket] doConnect() called. token=${!!this.token}, currentProjectID=${this.currentProjectID}`,
    );

    if (!this.token) {
      logger.error('Cannot connect without authentication token');
      return;
    }

    // WebSocket requires project_id query param
    // If no project_id set, use a default "global" project for general notifications
    const projectID = this.currentProjectID || 'global-notifications';
    const url = `${this.url}?project_id=${encodeURIComponent(projectID)}`;

    logger.info(`[WebSocket] Connecting to: ${url.replace(/eyJ[^&]*/g, 'TOKEN...')}`);

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      logger.info('✅ WebSocket connected');
      this.reconnectAttempts = 0;

      // Send authentication message (REQUIRED - token NOT in URL)
      this.sendAuth();
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        logger.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      logger.info('❌ WebSocket disconnected');
      this.isAuthenticated = false;
      this.cleanup();

      // Attempt reconnection with exponential backoff
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * 1.5 ** (this.reconnectAttempts - 1);
        logger.info(
          `🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`,
        );

        this.reconnectTimer = setTimeout(() => {
          this.doConnect();
        }, delay);
      } else {
        logger.error('❌ Max reconnection attempts reached');
      }
    };

    this.ws.onerror = (error) => {
      logger.error('❌ WebSocket error:', error);
    };
  }

  private sendAuth() {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN || !this.token) {
      return;
    }

    this.send({
      type: 'auth',
      token: this.token,
    });
  }

  private handleMessage(message: WebSocketMessage) {
    switch (message.type) {
      case 'auth_success':
        logger.info('✅ WebSocket authenticated');
        this.isAuthenticated = true;

        // Start ping interval
        this.startPingInterval();

        // Subscribe to project if specified
        if (this.currentProjectID) {
          this.subscribeToProject(this.currentProjectID);
        }
        break;

      case 'auth_failed':
        logger.error('❌ WebSocket authentication failed:', message.message);
        this.disconnect();
        break;

      case 'subscription_confirmed':
        logger.info('✅ Subscribed to project:', message.data.project_id);
        this.currentProjectID = message.data.project_id;
        break;

      case 'nats_event':
        this.handleNATSEvent(message);
        break;

      case 'pong':
        // Keepalive response
        break;

      case 'error':
        logger.error('❌ WebSocket error:', message.message);
        break;
    }
  }

  private handleNATSEvent(message: NATSEventMessage) {
    const { event_type, data } = message.data;

    logger.info('📡 Received NATS event:', event_type, data);

    // Trigger listeners for this specific event type
    const eventListeners = this.listeners.get(event_type);
    if (eventListeners) {
      eventListeners.forEach((callback) => callback(message.data));
    }

    // Also trigger wildcard listeners
    const wildcardListeners = this.listeners.get('*');
    if (wildcardListeners) {
      wildcardListeners.forEach((callback) => callback(message.data));
    }
  }

  /**
   * Subscribe to a specific project's events
   */
  subscribeToProject(projectID: string) {
    if (!this.isAuthenticated) {
      logger.warn('Cannot subscribe before authentication');
      return;
    }

    this.currentProjectID = projectID;
    this.send({
      type: 'subscribe_project',
      data: {
        project_id: projectID,
      },
    });
  }

  /**
   * Unsubscribe from current project
   */
  unsubscribeFromProject() {
    if (!this.isAuthenticated) {
      return;
    }

    this.send({
      type: 'unsubscribe_project',
    });
    this.currentProjectID = null;
  }

  /**
   * Listen for specific event types
   * @param eventType - Event type to listen for (e.g., "item.created", "*" for all)
   * @param callback - Callback function to handle the event
   * @returns Unsubscribe function
   */
  on(eventType: string, callback: EventListener): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.get(eventType)?.delete(callback);
      if (this.listeners.get(eventType)?.size === 0) {
        this.listeners.delete(eventType);
      }
    };
  }

  /**
   * Remove all event listeners for a specific event type
   */
  off(eventType: string) {
    this.listeners.delete(eventType);
  }

  private send(message: Record<string, unknown>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  private startPingInterval(): void {
    this.pingInterval = setInterval(() => {
      this.send({ type: 'ping' });
    }, 30000); // Ping every 30 seconds
  }

  private cleanup() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    this.cleanup();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isAuthenticated = false;
    this.currentProjectID = null;
    this.reconnectAttempts = 0;
  }

  /**
   * Check if WebSocket is connected and authenticated
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN && this.isAuthenticated;
  }

  /**
   * Get current connection status
   */
  getStatus(): 'connected' | 'connecting' | 'disconnected' {
    if (!this.ws) return 'disconnected';

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return this.isAuthenticated ? 'connected' : 'connecting';
      default:
        return 'disconnected';
    }
  }
}

// Singleton instance (can be used globally)
export const realtimeClient = new RealtimeClient();
