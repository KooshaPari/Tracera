import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

import { RealtimeClient } from './websocket';

// Mock WebSocket
global.WebSocket = vi.fn() as any;

describe('RealtimeClient', () => {
  let realtimeClient: RealtimeClient;
  let mockWs: any;

  beforeEach(() => {
    mockWs = {
      readyState: WebSocket.CONNECTING,
      send: vi.fn(),
      close: vi.fn(),
      addEventListener: vi.fn(),
    };
    (global.WebSocket as any).mockReturnValue(mockWs);
    realtimeClient = new RealtimeClient('ws://localhost:4000/api/v1/ws');
  });

  afterEach(() => {
    vi.clearAllMocks();
    realtimeClient.disconnect();
  });

  describe('Authentication', () => {
    it('should require token to connect', () => {
      realtimeClient.connect('', 'project-1');

      expect(mockWs.send).not.toHaveBeenCalled();
    });

    it('should send auth message on connect', (done) => {
      const token = 'test-token-123';
      realtimeClient.connect(token, 'project-1');

      // Simulate connection open
      const openEvent = mockWs.addEventListener.mock.calls.find(
        (call: any[]) => call[0] === 'open',
      );

      if (openEvent) {
        openEvent[1]();

        // Give time for async auth send
        setTimeout(() => {
          expect(mockWs.send).toHaveBeenCalled();
          const sentData = JSON.parse(mockWs.send.mock.calls[0][0]);
          expect(sentData.type).toBe('auth');
          expect(sentData.token).toBe(token);
          done();
        }, 50);
      }
    });

    it('should handle successful authentication', (done) => {
      realtimeClient.connect('test-token', 'project-1');

      // Simulate connection open
      const openEvent = mockWs.addEventListener.mock.calls.find(
        (call: any[]) => call[0] === 'open',
      );
      if (openEvent) {
        openEvent[1]();
      }

      // Simulate successful auth response
      const messageEvent = mockWs.addEventListener.mock.calls.find(
        (call: any[]) => call[0] === 'message',
      );
      if (messageEvent) {
        messageEvent[1]({
          data: JSON.stringify({
            type: 'auth_success',
            message: '',
          }),
        });

        setTimeout(() => {
          expect(realtimeClient.isConnected()).toBe(true);
          done();
        }, 50);
      }
    });

    it('should handle failed authentication', (done) => {
      realtimeClient.connect('invalid-token', 'project-1');

      const openEvent = mockWs.addEventListener.mock.calls.find(
        (call: any[]) => call[0] === 'open',
      );
      if (openEvent) {
        openEvent[1]();
      }

      // Simulate failed auth response
      const messageEvent = mockWs.addEventListener.mock.calls.find(
        (call: any[]) => call[0] === 'message',
      );
      if (messageEvent) {
        messageEvent[1]({
          data: JSON.stringify({
            type: 'auth_failed',
            message: 'Invalid token',
          }),
        });

        setTimeout(() => {
          expect(realtimeClient.isConnected()).toBe(false);
          done();
        }, 50);
      }
    });

    it('should not store token in logs', () => {
      const token = 'secret-token-123';
      const originalLog = console.log;
      const logs: string[] = [];

      console.log = vi.fn((msg: string) => {
        logs.push(msg);
      });

      realtimeClient.connect(token, 'project-1');

      console.log = originalLog;

      // Verify token is not in logs
      const logsWithToken = logs.filter((log) => log.includes(token));
      expect(logsWithToken.length).toBe(0);
    });
  });

  describe('Token Refresh', () => {
    it('should support token refresh without reconnection', (done) => {
      realtimeClient.connect('initial-token', 'project-1');

      // Simulate successful auth
      mockWs.readyState = WebSocket.OPEN;
      const messageEvent = mockWs.addEventListener.mock.calls.find(
        (call: any[]) => call[0] === 'message',
      );

      if (messageEvent) {
        messageEvent[1]({
          data: JSON.stringify({ type: 'auth_success' }),
        });

        setTimeout(() => {
          // Connect with new token (should update without closing connection)
          const sendCallsBefore = mockWs.send.mock.calls.length;
          realtimeClient.connect('refreshed-token', 'project-1');
          const sendCallsAfter = mockWs.send.mock.calls.length;

          // Should send new auth without closing
          expect(sendCallsAfter).toBeGreaterThan(sendCallsBefore);
          expect(mockWs.close).not.toHaveBeenCalled();
          done();
        }, 50);
      }
    });
  });

  describe('Message Handling', () => {
    it('should handle NATS events', (done) => {
      const callback = vi.fn();
      realtimeClient.on('item.created', callback);

      realtimeClient.connect('test-token', 'project-1');

      // Simulate auth success
      const messageEvent = mockWs.addEventListener.mock.calls.find(
        (call: any[]) => call[0] === 'message',
      );

      if (messageEvent) {
        // Send auth response
        messageEvent[1]({
          data: JSON.stringify({ type: 'auth_success' }),
        });

        // Send NATS event
        messageEvent[1]({
          data: JSON.stringify({
            type: 'nats_event',
            data: {
              event_type: 'item.created',
              project_id: 'project-1',
              entity_id: 'entity-1',
              entity_type: 'item',
              data: { name: 'test' },
              timestamp: new Date().toISOString(),
              source: 'go',
            },
          }),
        });

        setTimeout(() => {
          expect(callback).toHaveBeenCalledWith(
            expect.objectContaining({
              event_type: 'item.created',
            }),
          );
          done();
        }, 50);
      }
    });

    it('should trigger wildcard listeners', (done) => {
      const callback = vi.fn();
      realtimeClient.on('*', callback);

      realtimeClient.connect('test-token', 'project-1');

      const messageEvent = mockWs.addEventListener.mock.calls.find(
        (call: any[]) => call[0] === 'message',
      );

      if (messageEvent) {
        messageEvent[1]({
          data: JSON.stringify({ type: 'auth_success' }),
        });

        messageEvent[1]({
          data: JSON.stringify({
            type: 'nats_event',
            data: {
              event_type: 'any.event',
              project_id: 'project-1',
              entity_id: 'entity-1',
              entity_type: 'item',
              data: {},
              timestamp: new Date().toISOString(),
              source: 'go',
            },
          }),
        });

        setTimeout(() => {
          expect(callback).toHaveBeenCalled();
          done();
        }, 50);
      }
    });
  });

  describe('Connection Management', () => {
    it('should properly disconnect', () => {
      mockWs.readyState = WebSocket.OPEN;
      realtimeClient.connect('test-token', 'project-1');

      realtimeClient.disconnect();

      expect(mockWs.close).toHaveBeenCalled();
      expect(realtimeClient.isConnected()).toBe(false);
    });

    it('should handle reconnection with exponential backoff', (done) => {
      realtimeClient.connect('test-token', 'project-1');

      const closeEvent = mockWs.addEventListener.mock.calls.find(
        (call: any[]) => call[0] === 'close',
      );

      if (closeEvent) {
        closeEvent[1]();

        // Verify reconnect is attempted
        setTimeout(() => {
          expect(global.WebSocket).toHaveBeenCalledTimes(2);
          done();
        }, 6000); // Wait for reconnect timeout (5 seconds)
      }
    });

    it('should respect max reconnect attempts', (done) => {
      const originalSetTimeout = global.setTimeout;
      let reconnectCount = 0;

      global.setTimeout = vi.fn((cb: any) => {
        reconnectCount++;
        if (reconnectCount <= 10) {
          originalSetTimeout(cb, 0);
        }
        return 0;
      }) as any;

      realtimeClient.connect('test-token', 'project-1');

      const closeEvent = mockWs.addEventListener.mock.calls.find(
        (call: any[]) => call[0] === 'close',
      );

      if (closeEvent) {
        // Trigger close event 15 times
        for (let i = 0; i < 15; i++) {
          (global.WebSocket as any).mockReturnValue({
            readyState: WebSocket.OPEN,
            send: vi.fn(),
            close: vi.fn(),
            addEventListener: vi.fn(),
          });
          closeEvent[1]();
        }

        setTimeout(() => {
          expect(realtimeClient.isConnected()).toBe(false);
          global.setTimeout = originalSetTimeout;
          done();
        }, 100);
      }
    });
  });

  describe('Subscription Management', () => {
    it('should subscribe to project events', (done) => {
      realtimeClient.connect('test-token', 'project-1');

      const openEvent = mockWs.addEventListener.mock.calls.find(
        (call: any[]) => call[0] === 'open',
      );

      if (openEvent) {
        openEvent[1]();

        const messageEvent = mockWs.addEventListener.mock.calls.find(
          (call: any[]) => call[0] === 'message',
        );

        if (messageEvent) {
          messageEvent[1]({
            data: JSON.stringify({ type: 'auth_success' }),
          });

          setTimeout(() => {
            // Clear previous calls
            mockWs.send.mockClear();

            realtimeClient.subscribeToProject('project-2');

            const sentData = JSON.parse(mockWs.send.mock.calls[0][0]);
            expect(sentData.type).toBe('subscribe_project');
            expect(sentData.data.project_id).toBe('project-2');
            done();
          }, 50);
        }
      }
    });

    it('should unsubscribe from project', (done) => {
      realtimeClient.connect('test-token', 'project-1');

      const openEvent = mockWs.addEventListener.mock.calls.find(
        (call: any[]) => call[0] === 'open',
      );

      if (openEvent) {
        openEvent[1]();

        const messageEvent = mockWs.addEventListener.mock.calls.find(
          (call: any[]) => call[0] === 'message',
        );

        if (messageEvent) {
          messageEvent[1]({
            data: JSON.stringify({ type: 'auth_success' }),
          });

          setTimeout(() => {
            mockWs.send.mockClear();

            realtimeClient.unsubscribeFromProject();

            const sentData = JSON.parse(mockWs.send.mock.calls[0][0]);
            expect(sentData.type).toBe('unsubscribe_project');
            done();
          }, 50);
        }
      }
    });
  });
});
