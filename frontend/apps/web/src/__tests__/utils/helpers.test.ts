/**
 * Tests for helper utilities
 */

import { describe, expect, it, vi } from 'vitest';

import {
  calculateProgress,
  chunk,
  copyToClipboard,
  debounce,
  deepClone,
  downloadFile,
  generateId,
  getFromStorage,
  getItemAncestors,
  getItemChildren,
  getItemsByView,
  getLinkedItems,
  groupBy,
  isDefined,
  isEmpty,
  isNotNull,
  merge,
  omit,
  pick,
  randomString,
  removeFromStorage,
  setToStorage,
  shuffle,
  sleep,
  slugify,
  sortBy,
  throttle,
  unique,
} from '../../utils/helpers';

describe('Helper Utilities', () => {
  describe('Array utilities', () => {
    it('should group array by key', () => {
      const items = [
        { category: 'A', id: 1 },
        { category: 'B', id: 2 },
        { category: 'A', id: 3 },
      ];
      const grouped = groupBy(items, 'category');
      expect(grouped.A).toHaveLength(2);
      expect(grouped.B).toHaveLength(1);
    });

    it('should sort array ascending', () => {
      const items = [{ name: 'C' }, { name: 'A' }, { name: 'B' }];
      const sorted = sortBy(items, 'name', 'asc');
      expect(sorted[0].name).toBe('A');
      expect(sorted[2].name).toBe('C');
    });

    it('should sort array descending', () => {
      const items = [{ name: 'A' }, { name: 'C' }, { name: 'B' }];
      const sorted = sortBy(items, 'name', 'desc');
      expect(sorted[0].name).toBe('C');
      expect(sorted[2].name).toBe('A');
    });

    it('should return unique values', () => {
      const items = [1, 2, 2, 3, 3, 3, 4];
      const result = unique(items);
      expect(result).toHaveLength(4);
      expect(result).toContain(1);
      expect(result).toContain(2);
    });

    it('should chunk array', () => {
      const items = [1, 2, 3, 4, 5, 6, 7];
      const chunks = chunk(items, 3);
      expect(chunks).toHaveLength(3);
      expect(chunks[0]).toEqual([1, 2, 3]);
      expect(chunks[2]).toEqual([7]);
    });

    it('should shuffle array', () => {
      const items = [1, 2, 3, 4, 5];
      const shuffled = shuffle(items);
      expect(shuffled).toHaveLength(5);
      expect(shuffled).toContain(1);
      expect(shuffled).toContain(5);
    });
  });

  describe('Object utilities', () => {
    it('should pick object properties', () => {
      const obj = { a: 1, b: 2, c: 3 };
      const result = pick(obj, ['a', 'c']);
      expect(result).toEqual({ a: 1, c: 3 });
      expect(result).not.toHaveProperty('b');
    });

    it('should omit object properties', () => {
      const obj = { a: 1, b: 2, c: 3 };
      const result = omit(obj, ['b']);
      expect(result).toEqual({ a: 1, c: 3 });
      expect(result).not.toHaveProperty('b');
    });

    it('should deep clone object', () => {
      const obj = { a: 1, b: { c: 2 } };
      const cloned = deepClone(obj);
      cloned.b.c = 3;
      expect(obj.b.c).toBe(2);
      expect(cloned.b.c).toBe(3);
    });

    it('should check if object is empty', () => {
      expect(isEmpty({})).toBeTruthy();
      expect(isEmpty({ a: 1 })).toBeFalsy();
    });

    it('should merge objects', () => {
      const obj1 = { a: 1, b: 2 };
      const obj2 = { b: 3, c: 4 };
      const result = merge(obj1, obj2);
      expect(result).toEqual({ a: 1, b: 3, c: 4 });
    });
  });

  describe('String utilities', () => {
    it('should generate unique ID', () => {
      const id1 = generateId();
      const id2 = generateId();
      expect(id1).not.toBe(id2);
      expect(id1).toMatch(/\d+-[a-z0-9]+/);
    });

    it('should slugify text', () => {
      expect(slugify('Hello World')).toBe('hello-world');
      expect(slugify('  Spaces  ')).toBe('spaces');
      expect(slugify('Special!@#$Chars')).toBe('specialchars');
    });

    it('should generate random string', () => {
      const str = randomString(10);
      expect(str).toHaveLength(10);
      expect(str).toMatch(/^[a-zA-Z0-9]{10}$/);
    });
  });

  describe('Type guards', () => {
    it('should check if value is not null', () => {
      expect(isNotNull(null)).toBeFalsy();
      expect(isNotNull()).toBeFalsy();
      expect(isNotNull(0)).toBeTruthy();
      expect(isNotNull('')).toBeTruthy();
    });

    it('should check if value is defined', () => {
      expect(isDefined()).toBeFalsy();
      expect(isDefined(null)).toBeTruthy();
      expect(isDefined(0)).toBeTruthy();
    });
  });

  describe('Async utilities', () => {
    it('should sleep for specified time', async () => {
      const start = Date.now();
      await sleep(10);
      const elapsed = Date.now() - start;
      expect(elapsed).toBeGreaterThanOrEqual(10);
    });

    it('should debounce function calls', async () => {
      const mockFn = vi.fn();
      const debouncedFn = debounce(mockFn, 50);

      debouncedFn();
      debouncedFn();
      debouncedFn();

      expect(mockFn).not.toHaveBeenCalled();

      await new Promise((resolve) => setTimeout(resolve, 60));
      expect(mockFn).toHaveBeenCalledOnce();
    });

    it('should throttle function calls', async () => {
      const mockFn = vi.fn();
      const throttledFn = throttle(mockFn, 50);

      throttledFn();
      throttledFn();
      throttledFn();

      expect(mockFn).toHaveBeenCalledOnce();

      await new Promise((resolve) => setTimeout(resolve, 60));
      throttledFn();
      expect(mockFn).toHaveBeenCalledTimes(2);
    });
  });

  describe('TraceRTM specific utilities', () => {
    it('should get items by view', () => {
      const items = [
        { id: '1', view: 'table' },
        { id: '2', view: 'graph' },
        { id: '3', view: 'table' },
      ] as any;

      const tableItems = getItemsByView(items, 'table');
      expect(tableItems).toHaveLength(2);
      expect(tableItems[0].id).toBe('1');
    });

    it('should get item children', () => {
      const items = [
        { id: '1', parentId: null },
        { id: '2', parentId: '1' },
        { id: '3', parentId: '1' },
      ] as any;

      const children = getItemChildren(items, '1');
      expect(children).toHaveLength(2);
    });

    it('should get item ancestors', () => {
      const items = [
        { id: '1', parentId: null },
        { id: '2', parentId: '1' },
        { id: '3', parentId: '2' },
      ] as any;

      const ancestors = getItemAncestors(items, '3');
      expect(ancestors).toHaveLength(2);
      expect(ancestors[0].id).toBe('1');
      expect(ancestors[1].id).toBe('2');
    });

    it('should get linked items', () => {
      const items = [{ id: '1' }, { id: '2' }, { id: '3' }] as any;
      const links = [
        { id: '1', sourceId: '1', targetId: '2' },
        { id: '2', sourceId: '3', targetId: '2' },
      ] as any;

      const linked = getLinkedItems(items, links, '2');
      expect(linked.sources).toHaveLength(2);
      expect(linked.targets).toHaveLength(0);
    });

    it('should calculate progress', () => {
      const items = [
        { status: 'done' },
        { status: 'done' },
        { status: 'pending' },
        { status: 'pending' },
      ] as any;

      const progress = calculateProgress(items);
      expect(progress).toBe(50);
    });

    it('should return 0 for empty items', () => {
      expect(calculateProgress([])).toBe(0);
    });
  });

  describe('Local storage utilities', () => {
    beforeEach(() => {
      localStorage.clear();
    });

    it('should get from storage', () => {
      localStorage.setItem('test-key', JSON.stringify({ value: 'test' }));
      const result = getFromStorage('test-key', {});
      expect(result).toEqual({ value: 'test' });
    });

    it('should return default if key not found', () => {
      const result = getFromStorage('missing-key', { default: 'value' });
      expect(result).toEqual({ default: 'value' });
    });

    it('should set to storage', () => {
      setToStorage('test-key', { value: 'test' });
      expect(localStorage.getItem('test-key')).toBe(JSON.stringify({ value: 'test' }));
    });

    it('should remove from storage', () => {
      localStorage.setItem('test-key', 'value');
      removeFromStorage('test-key');
      expect(localStorage.getItem('test-key')).toBeNull();
    });
  });

  describe('Clipboard utilities', () => {
    it('should handle clipboard copy', async () => {
      // Note: This test may not work in all environments without proper Clipboard API mock
      const result = await copyToClipboard('test text');
      expect(typeof result).toBe('boolean');
    });
  });

  describe('File download utilities', () => {
    it('should handle download file', () => {
      // This test verifies the function is callable
      // Actual file download behavior requires browser environment
      expect(() => {
        downloadFile('test content', 'test.txt');
      }).not.toThrow();
    });
  });
});
