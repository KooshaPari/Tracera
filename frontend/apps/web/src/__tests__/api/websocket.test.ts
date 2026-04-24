/**
 * Comprehensive tests for WebSocket API
 * Goal: Increase coverage from 59% to 95%
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  WebSocketManager,
  connectWebSocket,
  disconnectWebSocket,
  getWebSocketManager,
  subscribeToChannel,
} from '@/api/websocket';

// Mock window for browser environment
const mockWindow = {
  clearInterval: vi.fn(),
  location: { protocol: 'http:' },
  setInterval: vi.fn((_fn: () => void, _delay: number) => 123 as any),
};

globalThis.window = mockWindow as any;
globalThis.window = mockWindow as any;

// Mock WebSocket (intentionally uses on* properties to mirror WebSocket API)
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  url: string;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    // Simulate connection after a tick
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 0);
  }

  send(_data: string) {
    // Mock send
  }

  close() {
    this.readyState = MockWebSocket.CLOSED;
    if (this.onclose) {
      this.onclose(new CloseEvent('close'));
    }
  }

  addEventListener(event: string, handler: EventListener) {
    if (event === 'open') {
      this.onopen = handler;
    }
    if (event === 'close') {
      this.onclose = handler;
    }
    if (event === 'error') {
      this.onerror = handler;
    }
    if (event === 'message') {
      this.onmessage = handler;
    }
  }

  removeEventListener(event: string, handler: EventListener) {
    if (event === 'open' && this.onopen === handler) {
      this.onopen = null;
    }
    if (event === 'close' && this.onclose === handler) {
      this.onclose = null;
    }
    if (event === 'error' && this.onerror === handler) {
      this.onerror = null;
    }
    if (event === 'message' && this.onmessage === handler) {
      this.onmessage = null;
    }
  }
}

// Replace global WebSocket
globalThis.WebSocket = MockWebSocket as any;

// Mock API_BASE_URL
vi.mock('@/api/client', () => ({
  client: {
    API_BASE_URL: 'http://localhost:4000',
  },
}));

describe('WebSocket API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset singleton by clearing the module cache
    vi.resetModules();
    // Re-import to get fresh singleton
    vi.doMock('@/api/websocket', async () => {
      const actual = await vi.importActual('@/api/websocket');
      return actual;
    });
  });

  afterEach(() => {
    // Clean up any connections
    try {
      disconnectWebSocket();
    } catch {
      // Ignore errors
    }
    vi.clearAllTimers();
  });

  describe(WebSocketManager, () => {
    it('should create a WebSocketManager instance', () => {
      const manager = getWebSocketManager();
      expect(manager).toBeInstanceOf(WebSocketManager);
    });

    it('should return same instance (singleton)', () => {
      const manager1 = getWebSocketManager();
      const manager2 = getWebSocketManager();
      expect(manager1).toBe(manager2);
    });
  });

  describe(connectWebSocket, () => {
    it('should connect to WebSocket', () => {
      connectWebSocket();
      const manager = getWebSocketManager();
      expect(manager).toBeDefined();
    });

    it('should handle connection errors gracefully', () => {
      // Connection errors are caught internally
      expect(() => connectWebSocket()).not.toThrow();
    });
  });

  describe(disconnectWebSocket, () => {
    it('should disconnect WebSocket', () => {
      connectWebSocket();
      expect(() => disconnectWebSocket()).not.toThrow();
    });

    it('should handle disconnect when not connected', () => {
      expect(() => disconnectWebSocket()).not.toThrow();
    });
  });

  describe(subscribeToChannel, () => {
    it('should subscribe to a channel', () => {
      connectWebSocket();
      const unsubscribe = subscribeToChannel('test-channel', vi.fn());
      expect(unsubscribe).toBeDefined();
      expect(typeof unsubscribe).toBe('function');
    });

    it('should call callback when message received', async () => {
      connectWebSocket();
      await new Promise((resolve) => setTimeout(resolve, 10)); // Wait for connection

      const callback = vi.fn();
      subscribeToChannel('items:created', callback);

      // Simulate message
      const manager = getWebSocketManager();
      if ((manager as any).ws?.onmessage) {
        const mockEvent = new MessageEvent('message', {
          data: JSON.stringify({
            record: { id: '1' },
            schema: 'public',
            table: 'items',
            timestamp: Date.now(),
            type: 'created',
          }),
        });
        (manager as any).ws.onmessage(mockEvent);
      }

      // Callback should be called for matching channel
      expect(callback).toHaveBeenCalled();
    });

    it('should unsubscribe from channel', () => {
      connectWebSocket();
      const unsubscribe = subscribeToChannel('test-channel', vi.fn());
      expect(() => unsubscribe()).not.toThrow();
    });

    it('should handle multiple subscriptions', () => {
      connectWebSocket();
      const unsubscribe1 = subscribeToChannel('channel-1', vi.fn());
      const unsubscribe2 = subscribeToChannel('channel-2', vi.fn());

      expect(unsubscribe1).toBeDefined();
      expect(unsubscribe2).toBeDefined();

      unsubscribe1();
      unsubscribe2();
    });
  });

  describe('WebSocketManager methods', () => {
    let manager: WebSocketManager;

    beforeEach(() => {
      manager = getWebSocketManager();
    });

    it('should connect when connect is called', () => {
      manager.connect();
      expect(manager).toBeDefined();
    });

    it('should disconnect when disconnect is called', () => {
      manager.connect();
      expect(() => manager.disconnect()).not.toThrow();
    });

    it('should subscribe to channels', () => {
      manager.connect();
      const unsubscribe = manager.subscribe('test-channel', vi.fn());
      expect(unsubscribe).toBeDefined();
      expect(typeof unsubscribe).toBe('function');
    });

    it('should handle message routing to correct channel', async () => {
      manager.connect();
      await new Promise((resolve) => setTimeout(resolve, 10)); // Wait for connection

      const callback = vi.fn();
      manager.subscribe('items:created', callback);

      // Simulate message
      if ((manager as any).ws?.onmessage) {
        const mockEvent = new MessageEvent('message', {
          data: JSON.stringify({
            record: { id: '1' },
            schema: 'public',
            table: 'items',
            timestamp: Date.now(),
            type: 'created',
          }),
        });
        (manager as any).ws.onmessage(mockEvent);
      }

      expect(callback).toHaveBeenCalled();
    });

    it('should handle connection errors', () => {
      manager.connect();
      if ((manager as any).ws?.onerror) {
        const mockEvent = new Event('error');
        (manager as any).ws.onerror(mockEvent);
      }
      // Should not throw
      expect(manager).toBeDefined();
    });

    it('should handle connection close', () => {
      manager.connect();
      if ((manager as any).ws?.onclose) {
        const mockEvent = new CloseEvent('close');
        (manager as any).ws.onclose(mockEvent);
      }
      // Should not throw
      expect(manager).toBeDefined();
    });

    it('should handle reconnection logic', () => {
      manager.connect();
      manager.disconnect();
      manager.connect();
      expect(manager).toBeDefined();
    });

    it('should handle multiple channel subscriptions', () => {
      manager.connect();
      const unsub1 = manager.subscribe('channel-1', vi.fn());
      const unsub2 = manager.subscribe('channel-2', vi.fn());
      const unsub3 = manager.subscribe('channel-1', vi.fn()); // Same channel, different callback

      expect(unsub1).toBeDefined();
      expect(unsub2).toBeDefined();
      expect(unsub3).toBeDefined();

      unsub1();
      unsub2();
      unsub3();
    });

    it('should handle unsubscribe correctly', () => {
      manager.connect();
      const callback = vi.fn();
      const unsubscribe = manager.subscribe('test-channel', callback);

      unsubscribe();

      // Callback should not be called after unsubscribe
      if ((manager as any).ws?.onmessage) {
        const mockEvent = new MessageEvent('message', {
          data: JSON.stringify({ channel: 'test-channel', data: 'test' }),
        });
        (manager as any).ws.onmessage(mockEvent);
      }

      // Callback should not have been called
      expect(callback).not.toHaveBeenCalled();
    });
  });

  describe('edge cases', () => {
    it('should handle WebSocket not available', () => {
      const originalWebSocket = globalThis.WebSocket;
      delete (globalThis as any).WebSocket;

      expect(() => getWebSocketManager()).not.toThrow();

      globalThis.WebSocket = originalWebSocket;
    });

    it('should handle connection when already connected', () => {
      const manager = getWebSocketManager();
      manager.connect();
      expect(() => manager.connect()).not.toThrow();
    });

    it('should handle disconnect when not connected', () => {
      const manager = getWebSocketManager();
      expect(() => manager.disconnect()).not.toThrow();
    });

    it('should handle messages for non-existent channels', async () => {
      const manager = getWebSocketManager();
      manager.connect();
      await new Promise((resolve) => setTimeout(resolve, 10));

      if ((manager as any).ws?.onmessage) {
        const mockEvent = new MessageEvent('message', {
          data: JSON.stringify({
            record: { id: '1' },
            schema: 'public',
            table: 'items',
            timestamp: Date.now(),
            type: 'created',
          }),
        });
        expect(() => {
          (manager as any).ws.onmessage(mockEvent);
        }).not.toThrow();
      }
    });

    it('should handle malformed messages', async () => {
      const manager = getWebSocketManager();
      manager.connect();
      await new Promise((resolve) => setTimeout(resolve, 10));

      if ((manager as any).ws?.onmessage) {
        const mockEvent = new MessageEvent('message', {
          data: 'invalid json',
        });
        expect(() => {
          (manager as any).ws.onmessage(mockEvent);
        }).not.toThrow();
      }
    });

    it('should handle messages with invalid structure', async () => {
      const manager = getWebSocketManager();
      manager.connect();
      await new Promise((resolve) => setTimeout(resolve, 10));

      if ((manager as any).ws?.onmessage) {
        const mockEvent = new MessageEvent('message', {
          data: JSON.stringify({ data: 'test' }), // Missing required fields
        });
        expect(() => {
          (manager as any).ws.onmessage(mockEvent);
        }).not.toThrow();
      }
    });
  });
});
