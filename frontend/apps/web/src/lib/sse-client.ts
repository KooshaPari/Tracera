/**
 * Server-Sent Events (SSE) client with automatic reconnection and exponential backoff
 */

export interface SSEClientOptions {
  url: string;
  headers?: Record<string, string>;
  maxReconnectAttempts?: number;
  initialReconnectDelay?: number;
  maxReconnectDelay?: number;
  onMessage?: (event: MessageEvent) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
}

export class SSEClient {
  private eventSource: EventSource | null = null;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private isManualClose = false;
  private currentDelay: number;

  constructor(private options: SSEClientOptions) {
    this.currentDelay = options.initialReconnectDelay || 1000;
  }

  /**
   * Connect to the SSE endpoint
   */
  public connect(): void {
    if (this.eventSource) {
      return; // Already connected
    }

    this.isManualClose = false;

    try {
      // Create EventSource with custom headers (note: EventSource API doesn't support custom headers directly)
      // For authentication, we need to pass the token in the URL or use a proxy approach
      const url = this.buildUrlWithAuth(this.options.url, this.options.headers);
      this.eventSource = new EventSource(url);

      this.eventSource.onopen = () => {
        console.log('SSE connection established');
        this.reconnectAttempts = 0;
        this.currentDelay = this.options.initialReconnectDelay || 1000;
        this.options.onOpen?.();
      };

      this.eventSource.onmessage = (event: MessageEvent) => {
        this.options.onMessage?.(event);
      };

      this.eventSource.onerror = (error: Event) => {
        console.error('SSE connection error:', error);
        this.options.onError?.(error);

        // EventSource will auto-reconnect for network errors, but we handle manual reconnection
        // for auth failures or other issues
        this.handleError();
      };

      // Handle custom event types
      this.eventSource.addEventListener('notification', (event: MessageEvent) => {
        this.handleNotificationEvent(event);
      });

      this.eventSource.addEventListener('read', (event: MessageEvent) => {
        this.handleNotificationEvent(event);
      });

      this.eventSource.addEventListener('read_all', (event: MessageEvent) => {
        this.handleNotificationEvent(event);
      });

      this.eventSource.addEventListener('delete', (event: MessageEvent) => {
        this.handleNotificationEvent(event);
      });

      this.eventSource.addEventListener('connected', (event: MessageEvent) => {
        console.log('SSE connected:', event.data);
      });

      this.eventSource.addEventListener('ping', (_event: MessageEvent) => {
        // Keep-alive ping, no action needed
      });
    } catch (error) {
      console.error('Failed to create EventSource:', error);
      this.scheduleReconnect();
    }
  }

  /**
   * Handle notification events
   */
  private handleNotificationEvent(event: MessageEvent): void {
    this.options.onMessage?.(event);
  }

  /**
   * Build URL with authentication token
   * EventSource doesn't support custom headers, so we need to pass auth in URL or use cookies
   */
  private buildUrlWithAuth(url: string, headers?: Record<string, string>): string {
    if (!headers?.['Authorization']) {
      return url;
    }

    // Extract bearer token from Authorization header
    const token = headers['Authorization'].replace('Bearer ', '');
    const separator = url.includes('?') ? '&' : '?';
    return `${url}${separator}token=${encodeURIComponent(token)}`;
  }

  /**
   * Handle connection errors
   */
  private handleError(): void {
    if (this.isManualClose) {
      return; // Don't reconnect if manually closed
    }

    // Close the current connection
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }

    this.scheduleReconnect();
  }

  /**
   * Schedule reconnection with exponential backoff
   */
  private scheduleReconnect(): void {
    const maxAttempts = this.options.maxReconnectAttempts || Infinity;

    if (this.reconnectAttempts >= maxAttempts) {
      console.error(`Max reconnection attempts (${maxAttempts}) reached. Giving up.`);
      this.options.onClose?.();
      return;
    }

    this.reconnectAttempts++;

    console.log(
      `Scheduling reconnection attempt ${this.reconnectAttempts} in ${this.currentDelay}ms`,
    );

    // Clear any existing timer
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, this.currentDelay);

    // Exponential backoff
    this.currentDelay = Math.min(this.currentDelay * 2, this.options.maxReconnectDelay || 30000);
  }

  /**
   * Manually close the connection
   */
  public close(): void {
    this.isManualClose = true;

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }

    this.options.onClose?.();
  }

  /**
   * Get connection state
   */
  public getState(): number {
    return this.eventSource?.readyState ?? EventSource.CLOSED;
  }

  /**
   * Check if connected
   */
  public isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN;
  }
}

/**
 * Create SSE client for notifications
 */
export function createNotificationSSEClient(
  token: string | null,
  onNotification: (notification: unknown) => void,
  onError?: (error: Event) => void,
): SSEClient | null {
  if (!token) {
    return null;
  }

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

  return new SSEClient({
    url: `${API_URL}/api/v1/notifications/stream`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
    maxReconnectAttempts: 10,
    initialReconnectDelay: 1000,
    maxReconnectDelay: 30000,
    onMessage: (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        onNotification(data);
      } catch (error) {
        console.error('Failed to parse notification data:', error);
      }
    },
    onError: (error: Event) => {
      console.error('Notification SSE error:', error);
      onError?.(error);
    },
    onOpen: () => {
      console.log('Notification SSE connection opened');
    },
    onClose: () => {
      console.log('Notification SSE connection closed');
    },
  });
}
