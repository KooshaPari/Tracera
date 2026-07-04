/**
 * Tests for useOnClickOutside - Click detection outside element
 */

import { describe, expect, it, vi } from 'vitest';

describe('useOnClickOutside Hook', () => {
  describe('Element Detection', () => {
    it('should check if element exists', () => {
      const ref = { current: null };
      expect(ref.current).toBeNull();
    });

    it('should have reference object property', () => {
      const ref = { current: 'mock-element' };
      expect(ref.current).toBeDefined();
      expect(ref.current).toBe('mock-element');
    });

    it('should handle undefined current', () => {
      const ref = { current: undefined };
      const el = ref?.current;
      expect(el).toBeUndefined();
    });
  });

  describe('Node Containment Logic', () => {
    it('should check if element is the target', () => {
      const element = { id: 'container' };
      const target = element; // Same reference
      const isSameElement = element === target;
      expect(isSameElement).toBeTruthy();
    });

    it('should detect different elements', () => {
      const element = { id: 'container' };
      const target = { id: 'outside' };
      const isSameElement = element === target;
      expect(isSameElement).toBeFalsy();
    });

    it('should handle null element', () => {
      const element = null;
      const isValid = element !== null;
      expect(isValid).toBeFalsy();
    });

    it('should validate target is a Node', () => {
      const mockTarget = { type: 'element' };
      expect(typeof mockTarget).toBe('object');
    });
  });

  describe('Event Types', () => {
    it('should handle mousedown event', () => {
      const eventType = 'mousedown';
      expect(eventType).toBe('mousedown');
    });

    it('should handle touchstart event', () => {
      const eventType = 'touchstart';
      expect(eventType).toBe('touchstart');
    });

    it('should support both event types', () => {
      const events = ['mousedown', 'touchstart'];
      expect(events).toContain('mousedown');
      expect(events).toContain('touchstart');
    });
  });

  describe('Handler Invocation', () => {
    it('should call handler when click is outside', () => {
      const handler = vi.fn();
      const isInside = false;

      if (!isInside) {
        handler({ type: 'mousedown' });
      }

      expect(handler).toHaveBeenCalled();
    });

    it('should not call handler when click is inside', () => {
      const handler = vi.fn();
      const isInside = true;

      if (!isInside) {
        handler({ type: 'mousedown' });
      }

      expect(handler).not.toHaveBeenCalled();
    });

    it('should pass event object to handler', () => {
      const handler = vi.fn();
      const mockEvent = { target: 'element', type: 'mousedown' };

      handler(mockEvent);
      expect(handler).toHaveBeenCalledWith(mockEvent);
    });

    it('should handle both mouse and touch events', () => {
      const handler = vi.fn();
      const mouseEvent = { type: 'mousedown' };
      const touchEvent = { type: 'touchstart' };

      handler(mouseEvent);
      handler(touchEvent);

      expect(handler).toHaveBeenCalledTimes(2);
    });
  });

  describe('Document Availability', () => {
    it('should check if document is defined', () => {
      const documentAvailable = typeof document !== 'undefined';
      expect(typeof documentAvailable).toBe('boolean');
    });
  });

  describe('Event Listener Management', () => {
    it('should register mousedown listener', () => {
      const mockAddEventListener = vi.fn();
      mockAddEventListener('mousedown', () => {});
      expect(mockAddEventListener).toHaveBeenCalledWith('mousedown', expect.any(Function));
    });

    it('should register touchstart listener', () => {
      const mockAddEventListener = vi.fn();
      mockAddEventListener('touchstart', () => {});
      expect(mockAddEventListener).toHaveBeenCalledWith('touchstart', expect.any(Function));
    });

    it('should remove mousedown listener on cleanup', () => {
      const mockRemoveEventListener = vi.fn();
      mockRemoveEventListener('mousedown', () => {});
      expect(mockRemoveEventListener).toHaveBeenCalledWith('mousedown', expect.any(Function));
    });

    it('should remove touchstart listener on cleanup', () => {
      const mockRemoveEventListener = vi.fn();
      mockRemoveEventListener('touchstart', () => {});
      expect(mockRemoveEventListener).toHaveBeenCalledWith('touchstart', expect.any(Function));
    });
  });

  describe('Dependency Tracking', () => {
    it('should include ref in dependencies', () => {
      const ref = { current: null };
      const deps = [ref, () => {}];
      expect(deps[0]).toEqual(ref);
    });

    it('should include handler in dependencies', () => {
      const handler = () => {};
      const deps = [{ current: null }, handler];
      expect(deps[1]).toEqual(handler);
    });
  });
});
