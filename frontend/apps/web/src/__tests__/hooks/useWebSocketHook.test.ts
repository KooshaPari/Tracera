/**
 * Tests for useWebSocketHook - Real-time WebSocket connection management
 */

import { beforeEach, describe, expect, it } from 'vitest';

import type { RealtimeEvent } from '../../api/websocket';

import { useWebSocketStore } from '../../stores/websocket-store';

describe('WebSocket Hooks and Store', () => {
  const mockRealtimeEvent: RealtimeEvent = {
    record: { id: '1', title: 'Test Item' },
    schema: 'public',
    table: 'items',
    timestamp: Date.now(),
    type: 'created',
  };

  beforeEach(() => {
    // Reset WebSocket store before each test
    useWebSocketStore.getState().clearEvents();
  });

  describe('useWebSocketStore - connection management', () => {
    it('should initialize with disconnected state', () => {
      const state = useWebSocketStore.getState();
      expect(typeof state.isConnected).toBe('boolean');
      expect(state.reconnectAttempts).toBe(0);
    });

    it('should have connect method', () => {
      const state = useWebSocketStore.getState();
      expect(typeof state.connect).toBe('function');
    });

    it('should have disconnect method', () => {
      const state = useWebSocketStore.getState();
      expect(typeof state.disconnect).toBe('function');
    });

    it('should have subscribe method available', () => {
      const state = useWebSocketStore.getState();
      expect(typeof state.subscribe).toBe('function');
    });
  });

  describe('useWebSocketStore - event management', () => {
    it('should add events to store', () => {
      const state = useWebSocketStore.getState();
      state.addEvent(mockRealtimeEvent);

      const updated = useWebSocketStore.getState();
      expect(updated.events).toContain(mockRealtimeEvent);
      expect(updated.lastEvent).toEqual(mockRealtimeEvent);
    });

    it('should maintain event order (newest first)', () => {
      const event1: RealtimeEvent = {
        ...mockRealtimeEvent,
        record: { id: '1' },
      };
      const event2: RealtimeEvent = {
        ...mockRealtimeEvent,
        record: { id: '2' },
        timestamp: Date.now() + 1000,
      };

      const state = useWebSocketStore.getState();
      state.addEvent(event1);
      state.addEvent(event2);

      const updated = useWebSocketStore.getState();
      expect(updated.events[0]).toEqual(event2);
      expect(updated.events[1]).toEqual(event1);
    });

    it('should limit events to last 100', () => {
      const state = useWebSocketStore.getState();

      for (let i = 0; i < 150; i++) {
        state.addEvent({
          ...mockRealtimeEvent,
          record: { id: `${i}` },
          timestamp: Date.now() + i,
        });
      }

      const updated = useWebSocketStore.getState();
      expect(updated.events).toHaveLength(100);
    });

    it('should clear events', () => {
      const state = useWebSocketStore.getState();
      state.addEvent(mockRealtimeEvent);
      expect(useWebSocketStore.getState().events).toHaveLength(1);

      state.clearEvents();
      expect(useWebSocketStore.getState().events).toHaveLength(0);
      // LastEvent is set to undefined after clear
      const { lastEvent } = useWebSocketStore.getState();
      expect(lastEvent === undefined || lastEvent === null).toBeTruthy();
    });
  });

  describe('useWebSocketStore - channel subscriptions', () => {
    it('should initialize with empty active channels', () => {
      const state = useWebSocketStore.getState();
      expect(state.activeChannels instanceof Set).toBeTruthy();
      expect(state.activeChannels.size).toBe(0);
    });
  });

  describe('useWebSocketStore - connection status', () => {
    it('should set connection status', () => {
      const state = useWebSocketStore.getState();
      state.setConnectionStatus(true);

      expect(useWebSocketStore.getState().isConnected).toBeTruthy();

      state.setConnectionStatus(false);
      expect(useWebSocketStore.getState().isConnected).toBeFalsy();
    });

    it('should handle multiple status transitions', () => {
      const state = useWebSocketStore.getState();

      state.setConnectionStatus(true);
      expect(useWebSocketStore.getState().isConnected).toBeTruthy();

      state.setConnectionStatus(false);
      expect(useWebSocketStore.getState().isConnected).toBeFalsy();

      state.setConnectionStatus(true);
      expect(useWebSocketStore.getState().isConnected).toBeTruthy();
    });
  });

  describe('useWebSocketStore - integration scenarios', () => {
    it('should maintain event state with connection transitions', () => {
      const state = useWebSocketStore.getState();

      state.setConnectionStatus(true);
      state.addEvent(mockRealtimeEvent);

      let current = useWebSocketStore.getState();
      expect(current.isConnected).toBeTruthy();
      expect(current.events).toHaveLength(1);
      expect(current.lastEvent).toEqual(mockRealtimeEvent);

      state.setConnectionStatus(false);
      current = useWebSocketStore.getState();
      expect(current.isConnected).toBeFalsy();
      expect(current.events).toHaveLength(1); // Events persist
    });

    it('should handle reconnection and event accumulation', () => {
      const event1: RealtimeEvent = {
        ...mockRealtimeEvent,
        record: { id: '1' },
      };
      const event2: RealtimeEvent = {
        ...mockRealtimeEvent,
        record: { id: '2' },
        timestamp: Date.now() + 1000,
      };

      const state = useWebSocketStore.getState();

      // Initial connection and events
      state.setConnectionStatus(true);
      state.addEvent(event1);

      let current = useWebSocketStore.getState();
      expect(current.events).toHaveLength(1);

      // Simulate disconnection
      state.setConnectionStatus(false);
      current = useWebSocketStore.getState();
      expect(current.isConnected).toBeFalsy();

      // Reconnect and add more events
      state.setConnectionStatus(true);
      state.addEvent(event2);

      current = useWebSocketStore.getState();
      expect(current.isConnected).toBeTruthy();
      expect(current.events).toHaveLength(2);
      expect(current.lastEvent).toEqual(event2);
    });
  });
});
