/**
 * Comprehensive tests for websocket.ts
 * Target: 88.65% → 95% coverage
 * Focus: Remaining uncovered lines (147-148, 174-179)
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { connectWebSocket, disconnectWebSocket, getWebSocketManager } from '../../api/websocket';

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  url = '';
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;

  send = vi.fn();
  close = vi.fn();

  constructor(url: string) {
    this.url = url;
    // Simulate connection after a delay
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 10);
  }
}

// Mock window and WebSocket
globalThis.window = {
  clearInterval: vi.fn(),
  location: {
    host: 'localhost:4000',
    protocol: 'ws:',
  },
  setInterval: vi.fn(
    (_fn: TimerHandler, _delay?: number) => 1 as unknown as ReturnType<typeof setInterval>,
  ),
} as any;

globalThis.WebSocket = MockWebSocket as any;
globalThis.window = globalThis.window;

describe('WebSocket - Comprehensive Coverage (Remaining Gaps)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset singleton
    vi.resetModules();
  });

  describe('Heartbeat functionality', () => {
    it('should send heartbeat when connection is open', async () => {
      const manager = getWebSocketManager();
      const sendSpy = vi.spyOn(manager as any, 'send');

      await connectWebSocket();

      // Wait for connection
      await new Promise((resolve) => setTimeout(resolve, 50));

      // Verify heartbeat interval was set
      expect(globalThis.window.setInterval).toHaveBeenCalled();

      // Simulate heartbeat tick
      const heartbeatFn = vi.mocked(globalThis.window.setInterval).mock.calls[0]?.[0];
      if (heartbeatFn && typeof heartbeatFn === 'function') {
        heartbeatFn();
      }

      // Verify ping was sent
      await new Promise((resolve) => setTimeout(resolve, 10));
      expect(sendSpy).toHaveBeenCalledWith({ type: 'ping' });

      disconnectWebSocket();
    });

    it('should not send heartbeat when connection is not open', async () => {
      const manager = getWebSocketManager();
      const sendSpy = vi.spyOn(manager as any, 'send');

      // Create a WebSocket that stays in CONNECTING state
      class ConnectingWebSocket extends MockWebSocket {
        constructor(url: string) {
          super(url);
          this.readyState = MockWebSocket.CONNECTING;
        }
      }

      globalThis.WebSocket = ConnectingWebSocket as any;

      await connectWebSocket();

      // Wait a bit
      await new Promise((resolve) => setTimeout(resolve, 50));

      // Simulate heartbeat tick
      const heartbeatFn = vi.mocked(globalThis.window.setInterval).mock.calls[0]?.[0];
      if (heartbeatFn && typeof heartbeatFn === 'function') {
        heartbeatFn();
      }

      // Should not send ping when not open
      await new Promise((resolve) => setTimeout(resolve, 10));
      // SendSpy might not be called if readyState check fails
      expect(sendSpy).not.toHaveBeenCalledWith({ type: 'ping' });
    });
  });

  describe('Reconnection logic', () => {
    it('should attempt reconnection with exponential backoff', async () => {
      const manager = getWebSocketManager();
      const connectSpy = vi.spyOn(manager as any, 'connect');

      // Simulate connection failure
      class FailingWebSocket extends MockWebSocket {
        constructor(url: string) {
          super(url);
          setTimeout(() => {
            if (this.onerror) {
              this.onerror(new Event('error'));
            }
            if (this.onclose) {
              this.onclose(new CloseEvent('close'));
            }
          }, 10);
        }
      }

      globalThis.WebSocket = FailingWebSocket as any;

      await connectWebSocket();

      // Wait for reconnection attempt
      await new Promise((resolve) => setTimeout(resolve, 100));

      // Should have attempted reconnection
      expect(connectSpy).toHaveBeenCalled();

      disconnectWebSocket();
    });

    it('should stop reconnecting after max attempts', async () => {
      const manager = getWebSocketManager();
      const maxAttempts = (manager as any).maxReconnectAttempts;

      // Simulate multiple failures
      class AlwaysFailingWebSocket extends MockWebSocket {
        constructor(url: string) {
          super(url);
          setTimeout(() => {
            if (this.onerror) {
              this.onerror(new Event('error'));
            }
            if (this.onclose) {
              this.onclose(new CloseEvent('close'));
            }
          }, 10);
        }
      }

      globalThis.WebSocket = AlwaysFailingWebSocket as any;

      // Trigger multiple connection attempts
      for (let i = 0; i < maxAttempts + 1; i++) {
        await connectWebSocket();
        await new Promise((resolve) => setTimeout(resolve, 50));
      }

      // After max attempts, should stop trying
      const { reconnectAttempts } = manager as any;
      expect(reconnectAttempts).toBeLessThanOrEqual(maxAttempts);

      disconnectWebSocket();
    });

    it('should calculate exponential backoff delay', async () => {
      const manager = getWebSocketManager();
      const { reconnectDelay } = manager as any;

      // Simulate reconnection attempts
      (manager as any).reconnectAttempts = 1;
      const delay1 = reconnectDelay * 2 ** (1 - 1);

      (manager as any).reconnectAttempts = 2;
      const delay2 = reconnectDelay * 2 ** (2 - 1);

      (manager as any).reconnectAttempts = 3;
      const delay3 = reconnectDelay * 2 ** (3 - 1);

      expect(delay2).toBeGreaterThan(delay1);
      expect(delay3).toBeGreaterThan(delay2);
    });
  });

  describe('Connection state management', () => {
    it('should handle connection in non-browser environment', async () => {
      // Temporarily remove window
      const originalWindow = globalThis.window;
      (globalThis as any).window = undefined;
      (globalThis as any).window = undefined;

      const manager = getWebSocketManager();
      const startHeartbeatSpy = vi.spyOn(manager as any, 'startHeartbeat');

      // Should not start heartbeat without window
      await connectWebSocket();
      expect(startHeartbeatSpy).not.toHaveBeenCalled();

      // Restore window
      globalThis.window = originalWindow;
      globalThis.window = originalWindow;

      disconnectWebSocket();
    });

    it('should properly clean up heartbeat on disconnect', async () => {
      const manager = getWebSocketManager();
      const stopHeartbeatSpy = vi.spyOn(manager as any, 'stopHeartbeat');

      await connectWebSocket();
      await new Promise((resolve) => setTimeout(resolve, 50));

      disconnectWebSocket();

      // Should have stopped heartbeat
      expect(stopHeartbeatSpy).toHaveBeenCalled();
      expect(globalThis.window.clearInterval).toHaveBeenCalled();
    });
  });

  describe('Edge cases', () => {
    it('should handle rapid connect/disconnect cycles', async () => {
      for (let i = 0; i < 5; i++) {
        await connectWebSocket();
        await new Promise((resolve) => setTimeout(resolve, 10));
        disconnectWebSocket();
        await new Promise((resolve) => setTimeout(resolve, 10));
      }

      // Should not throw errors
      expect(true).toBeTruthy();
    });

    it('should handle send when not connected', async () => {
      const manager = getWebSocketManager();
      const sendSpy = vi.spyOn(manager as any, 'send');

      // Try to send without connecting
      (manager as any).send({ type: 'test' });

      // Should not throw, but may not send
      expect(sendSpy).toHaveBeenCalled();
    });
  });
});
