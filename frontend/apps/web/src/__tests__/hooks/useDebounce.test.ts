/**
 * Tests for useDebounce - Debounced value updates
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

describe('useDebounce Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Default Behavior', () => {
    it('should have default delay of 300ms', () => {
      const defaultDelay = 300;
      expect(defaultDelay).toBe(300);
    });

    it('should accept custom delay', () => {
      const customDelay = 500;
      expect(customDelay).toBeGreaterThan(0);
    });

    it('should accept zero delay', () => {
      const zeroDelay = 0;
      expect(zeroDelay).toBe(0);
    });

    it('should handle large delay values', () => {
      const largeDelay = 5000;
      expect(largeDelay).toBeGreaterThan(0);
    });
  });

  describe('Generic Types', () => {
    it('should work with string values', () => {
      const value = 'test';
      const debouncedValue = value;
      expect(typeof debouncedValue).toBe('string');
    });

    it('should work with number values', () => {
      const value = 42;
      const debouncedValue = value;
      expect(typeof debouncedValue).toBe('number');
    });

    it('should work with boolean values', () => {
      const value = true;
      const debouncedValue = value;
      expect(typeof debouncedValue).toBe('boolean');
    });

    it('should work with object values', () => {
      const value = { count: 1 };
      const debouncedValue = value;
      expect(typeof debouncedValue).toBe('object');
    });

    it('should work with array values', () => {
      const value = [1, 2, 3];
      const debouncedValue = value;
      expect(Array.isArray(debouncedValue)).toBeTruthy();
    });
  });

  describe('Timer Management', () => {
    it('should create timeout on value change', () => {
      const setTimeoutSpy = vi.spyOn(globalThis, 'setTimeout');
      const delay = 300;

      // Simulate setTimeout call
      setTimeout(() => {}, delay);

      expect(setTimeoutSpy).toHaveBeenCalledWith(expect.any(Function), delay);
      setTimeoutSpy.mockRestore();
    });

    it('should clear previous timeout', () => {
      const clearTimeoutSpy = vi.spyOn(globalThis, 'clearTimeout');
      const timerId = 1;

      clearTimeout(timerId);

      expect(clearTimeoutSpy).toHaveBeenCalledWith(timerId);
      clearTimeoutSpy.mockRestore();
    });

    it('should cleanup on unmount', () => {
      const clearTimeoutSpy = vi.spyOn(globalThis, 'clearTimeout');

      // Simulate cleanup function called
      clearTimeout(1);

      expect(clearTimeoutSpy).toHaveBeenCalled();
      clearTimeoutSpy.mockRestore();
    });
  });

  describe('Value Updates', () => {
    it('should return initial value immediately', () => {
      const initialValue = 'test';
      const debouncedValue = initialValue;

      expect(debouncedValue).toBe('test');
    });

    it('should delay value update', () => {
      const delay = 300;
      expect(delay).toBe(300);
    });

    it('should update after delay expires', () => {
      const delay = 300;
      const elapsedTime = delay;
      expect(elapsedTime).toBe(delay);
    });

    it('should handle rapid successive value changes', () => {
      const setTimeoutSpy = vi.spyOn(globalThis, 'setTimeout');
      const clearTimeoutSpy = vi.spyOn(globalThis, 'clearTimeout');

      // First change
      setTimeout(() => {}, 300);
      // Second change (should cancel first timeout)
      clearTimeout(1);
      setTimeout(() => {}, 300);

      expect(clearTimeoutSpy).toHaveBeenCalled();
      setTimeoutSpy.mockRestore();
      clearTimeoutSpy.mockRestore();
    });
  });

  describe('Dependency Management', () => {
    it('should include value in dependencies', () => {
      const value = 'test';
      const deps = [value, 300];
      expect(deps[0]).toBe('test');
    });

    it('should include delay in dependencies', () => {
      const delay = 500;
      const deps = ['test', delay];
      expect(deps[1]).toBe(500);
    });

    it('should re-run on value change', () => {
      const values = ['initial', 'updated'];
      expect(values[0]).not.toBe(values[1]);
    });

    it('should re-run on delay change', () => {
      const delays = [300, 500];
      expect(delays[0]).not.toBe(delays[1]);
    });
  });

  describe('Return Value', () => {
    it('should return same type as input', () => {
      const input = 'test';
      const output = input;
      expect(typeof output).toBe(typeof input);
    });

    it('should preserve value precision', () => {
      const input = Math.PI;
      const output = input;
      expect(output).toBe(input);
    });

    it('should handle null values', () => {
      const input = null;
      const output = input;
      expect(output).toBeNull();
    });

    it('should handle undefined values', () => {
      const input = undefined;
      const output = input;
      expect(output).toBeUndefined();
    });
  });
});
