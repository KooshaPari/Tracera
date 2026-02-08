/**
 * Comprehensive tests for helper utilities
 * Tests array, object, string, async utilities and TraceRTM-specific helpers
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import type { Item, Link } from '@tracertm/types';

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

describe(groupBy, () => {
  it('should group array by key', () => {
    const items = [
      { id: '1', type: 'A' },
      { id: '2', type: 'B' },
      { id: '3', type: 'A' },
    ];
    const result = groupBy(items, 'type');
    expect(result['A']).toHaveLength(2);
    expect(result['B']).toHaveLength(1);
  });

  it('should handle empty array', () => {
    const result = groupBy([], 'type');
    expect(result).toEqual({});
  });

  it('should handle single group', () => {
    const items = [
      { id: '1', type: 'A' },
      { id: '2', type: 'A' },
    ];
    const result = groupBy(items, 'type');
    expect(Object.keys(result)).toHaveLength(1);
    expect(result['A']).toHaveLength(2);
  });

  it('should handle numeric keys', () => {
    const items = [
      { count: 1, id: '1' },
      { count: 2, id: '2' },
      { count: 1, id: '3' },
    ];
    const result = groupBy(items, 'count');
    expect(result['1']).toHaveLength(2);
    expect(result['2']).toHaveLength(1);
  });

  it('should preserve all item properties', () => {
    const items = [
      { id: '1', type: 'A', value: 10 },
      { id: '2', type: 'A', value: 20 },
    ];
    const result = groupBy(items, 'type');
    const groupA = result['A'];
    expect(groupA?.[0]?.value).toBe(10);
    expect(groupA?.[1]?.value).toBe(20);
  });
});

describe(sortBy, () => {
  it('should sort ascending by default', () => {
    const items = [
      { id: '1', value: 3 },
      { id: '2', value: 1 },
      { id: '3', value: 2 },
    ];
    const result = sortBy(items, 'value');
    expect(result[0]?.value).toBe(1);
    expect(result[2]?.value).toBe(3);
  });

  it('should sort descending when specified', () => {
    const items = [
      { id: '1', value: 3 },
      { id: '2', value: 1 },
      { id: '3', value: 2 },
    ];
    const result = sortBy(items, 'value', 'desc');
    expect(result[0]?.value).toBe(3);
    expect(result[2]?.value).toBe(1);
  });

  it('should sort strings alphabetically', () => {
    const items = [
      { id: '1', name: 'Charlie' },
      { id: '2', name: 'Alice' },
      { id: '3', name: 'Bob' },
    ];
    const result = sortBy(items, 'name');
    expect(result[0]?.name).toBe('Alice');
    expect(result[2]?.name).toBe('Charlie');
  });

  it('should not mutate original array', () => {
    const items = [
      { id: '1', value: 3 },
      { id: '2', value: 1 },
    ];
    const original = [...items];
    sortBy(items, 'value');
    expect(items).toEqual(original);
  });

  it('should handle empty array', () => {
    const result = sortBy([], 'value');
    expect(result).toEqual([]);
  });

  it('should handle single item', () => {
    const items = [{ id: '1', value: 1 }];
    const result = sortBy(items, 'value');
    expect(result).toEqual(items);
  });

  it('should handle equal values', () => {
    const items = [
      { id: '1', value: 1 },
      { id: '2', value: 1 },
      { id: '3', value: 1 },
    ];
    const result = sortBy(items, 'value');
    expect(result).toHaveLength(3);
  });
});

describe(unique, () => {
  it('should remove duplicates from array', () => {
    const result = unique([1, 2, 2, 3, 3, 3]);
    expect(result).toEqual([1, 2, 3]);
  });

  it('should handle empty array', () => {
    const result = unique([]);
    expect(result).toEqual([]);
  });

  it('should handle array without duplicates', () => {
    const result = unique([1, 2, 3]);
    expect(result).toEqual([1, 2, 3]);
  });

  it('should handle string arrays', () => {
    const result = unique(['a', 'b', 'a', 'c']);
    expect(result).toEqual(['a', 'b', 'c']);
  });

  it('should preserve order of first occurrence', () => {
    const result = unique([3, 1, 2, 3, 1]);
    expect(result).toEqual([3, 1, 2]);
  });

  it('should handle single element', () => {
    const result = unique([1]);
    expect(result).toEqual([1]);
  });
});

describe(chunk, () => {
  it('should chunk array into specified size', () => {
    const result = chunk([1, 2, 3, 4, 5], 2);
    expect(result).toEqual([[1, 2], [3, 4], [5]]);
  });

  it('should handle exact division', () => {
    const result = chunk([1, 2, 3, 4], 2);
    expect(result).toEqual([
      [1, 2],
      [3, 4],
    ]);
  });

  it('should handle size larger than array', () => {
    const result = chunk([1, 2], 5);
    expect(result).toEqual([[1, 2]]);
  });

  it('should handle empty array', () => {
    const result = chunk([], 2);
    expect(result).toEqual([]);
  });

  it('should handle chunk size of 1', () => {
    const result = chunk([1, 2, 3], 1);
    expect(result).toEqual([[1], [2], [3]]);
  });

  it('should preserve element types', () => {
    const result = chunk(['a', 'b', 'c'], 2);
    expect(result).toEqual([['a', 'b'], ['c']]);
  });
});

describe(shuffle, () => {
  it('should return array with same length', () => {
    const arr = [1, 2, 3, 4, 5];
    const result = shuffle(arr);
    expect(result).toHaveLength(arr.length);
  });

  it('should contain all original elements', () => {
    const arr = [1, 2, 3, 4, 5];
    const result = shuffle(arr);
    expect(result.toSorted((a, b) => (a < b ? -1 : a > b ? 1 : 0))).toEqual(
      arr.toSorted((a, b) => (a < b ? -1 : a > b ? 1 : 0)),
    );
  });

  it('should not mutate original array', () => {
    const arr = [1, 2, 3, 4, 5];
    const original = [...arr];
    shuffle(arr);
    expect(arr).toEqual(original);
  });

  it('should handle empty array', () => {
    const result = shuffle([]);
    expect(result).toEqual([]);
  });

  it('should handle single element', () => {
    const result = shuffle([1]);
    expect(result).toEqual([1]);
  });
});

describe(pick, () => {
  it('should pick specified keys', () => {
    const obj = { a: 1, b: 2, c: 3 };
    const result = pick(obj, ['a', 'c']);
    expect(result).toEqual({ a: 1, c: 3 });
  });

  it('should handle empty keys array', () => {
    const obj = { a: 1, b: 2 };
    const result = pick(obj, []);
    expect(result).toEqual({});
  });

  it('should ignore non-existent keys', () => {
    const obj = { a: 1, b: 2 };
    const result = pick(obj, ['a', 'c' as any]);
    expect(result).toEqual({ a: 1 });
  });

  it('should preserve value types', () => {
    const obj = { bool: true, num: 42, str: 'hello' };
    const result = pick(obj, ['str', 'bool']);
    expect(result.str).toBe('hello');
    expect(result.bool).toBeTruthy();
  });
});

describe(omit, () => {
  it('should omit specified keys', () => {
    const obj = { a: 1, b: 2, c: 3 };
    const result = omit(obj, ['b']);
    expect(result).toEqual({ a: 1, c: 3 });
  });

  it('should handle empty keys array', () => {
    const obj = { a: 1, b: 2 };
    const result = omit(obj, []);
    expect(result).toEqual({ a: 1, b: 2 });
  });

  it('should handle non-existent keys', () => {
    const obj = { a: 1, b: 2 };
    const result = omit(obj, ['c' as any]);
    expect(result).toEqual({ a: 1, b: 2 });
  });

  it('should preserve value types', () => {
    const obj = { bool: true, num: 42, str: 'hello' };
    const result = omit(obj, ['num']);
    expect(result.str).toBe('hello');
    expect(result.bool).toBeTruthy();
  });
});

describe(deepClone, () => {
  it('should deep clone object', () => {
    const obj = { a: 1, b: { c: 2 } };
    const clone = deepClone(obj);
    expect(clone).toEqual(obj);
    expect(clone).not.toBe(obj);
    expect(clone.b).not.toBe(obj.b);
  });

  it('should deep clone array', () => {
    const arr = [1, [2, 3], { a: 4 }];
    const clone = deepClone(arr);
    expect(clone).toEqual(arr);
    expect(clone).not.toBe(arr);
  });

  it('should handle null', () => {
    const result = deepClone(null);
    expect(result).toBe(null);
  });

  it('should handle primitives', () => {
    expect(deepClone(42)).toBe(42);
    expect(deepClone('hello')).toBe('hello');
    expect(deepClone(true)).toBeTruthy();
  });

  it('should not preserve functions', () => {
    const obj = { fn: () => {} };
    const clone = deepClone(obj);
    expect(clone.fn).toBeUndefined();
  });
});

describe(isEmpty, () => {
  it('should return true for empty object', () => {
    expect(isEmpty({})).toBeTruthy();
  });

  it('should return false for non-empty object', () => {
    expect(isEmpty({ a: 1 })).toBeFalsy();
  });

  it('should handle object with many keys', () => {
    expect(isEmpty({ a: 1, b: 2, c: 3 })).toBeFalsy();
  });
});

describe(merge, () => {
  it('should merge objects', () => {
    const result = merge(
      { a: 1 } as Record<string, number>,
      { b: 2 } as Record<string, number>,
      { c: 3 } as Record<string, number>,
    );
    expect(result).toEqual({ a: 1, b: 2, c: 3 });
  });

  it('should override properties', () => {
    const result = merge({ a: 1 } as Record<string, number>, { a: 2 } as Record<string, number>);
    expect(result).toEqual({ a: 2 });
  });

  it('should handle empty sources', () => {
    const result = merge({ a: 1 }, {}, {});
    expect(result).toEqual({ a: 1 });
  });

  it('should not mutate target', () => {
    const target = { a: 1 };
    merge(target, { b: 2 });
    expect(target).toEqual({ a: 1 });
  });
});

describe(generateId, () => {
  it('should generate unique IDs', () => {
    const id1 = generateId();
    const id2 = generateId();
    expect(id1).not.toBe(id2);
  });

  it('should generate string ID', () => {
    const id = generateId();
    expect(typeof id).toBe('string');
  });

  it('should contain timestamp and random part', () => {
    const id = generateId();
    expect(id).toContain('-');
  });
});

describe(slugify, () => {
  it('should convert to slug', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('should remove special characters', () => {
    expect(slugify('Hello @ World!')).toBe('hello-world');
  });

  it('should handle multiple spaces', () => {
    expect(slugify('Hello   World')).toBe('hello-world');
  });

  it('should trim leading/trailing hyphens', () => {
    expect(slugify('-Hello World-')).toBe('hello-world');
  });

  it('should handle underscores', () => {
    expect(slugify('hello_world')).toBe('hello-world');
  });

  it('should handle empty string', () => {
    expect(slugify('')).toBe('');
  });
});

describe(randomString, () => {
  it('should generate string of specified length', () => {
    const result = randomString(10);
    expect(result).toHaveLength(10);
  });

  it('should generate alphanumeric string', () => {
    const result = randomString(100);
    expect(result).toMatch(/^[A-Za-z0-9]+$/);
  });

  it('should generate different strings', () => {
    const str1 = randomString(20);
    const str2 = randomString(20);
    expect(str1).not.toBe(str2);
  });

  it('should handle length of 0', () => {
    const result = randomString(0);
    expect(result).toBe('');
  });
});

describe(isNotNull, () => {
  it('should return true for non-null values', () => {
    expect(isNotNull(0)).toBeTruthy();
    expect(isNotNull('')).toBeTruthy();
    expect(isNotNull(false)).toBeTruthy();
    expect(isNotNull({})).toBeTruthy();
  });

  it('should return false for null', () => {
    expect(isNotNull(null)).toBeFalsy();
  });

  it('should return false for undefined', () => {
    expect(isNotNull()).toBeFalsy();
  });
});

describe(isDefined, () => {
  it('should return true for defined values', () => {
    expect(isDefined(0)).toBeTruthy();
    expect(isDefined('')).toBeTruthy();
    expect(isDefined(null)).toBeTruthy();
  });

  it('should return false for undefined', () => {
    expect(isDefined()).toBeFalsy();
  });
});

describe(sleep, () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should resolve after specified time', async () => {
    const promise = sleep(1000);
    vi.advanceTimersByTime(1000);
    await expect(promise).resolves.toBeUndefined();
  });

  it('should not resolve before time elapses', async () => {
    const promise = sleep(1000);
    vi.advanceTimersByTime(500);
    // Promise should still be pending
    let resolved = false;
    void promise.then(() => {
      resolved = true;
    });
    await Promise.resolve(); // Flush microtasks
    expect(resolved).toBeFalsy();
  });
});

describe(debounce, () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should delay function execution', () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 100);

    debounced();
    expect(fn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(100);
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it('should reset timer on multiple calls', () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 100);

    debounced();
    vi.advanceTimersByTime(50);
    debounced();
    vi.advanceTimersByTime(50);
    expect(fn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(50);
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it('should pass arguments to function', () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 100);

    debounced('arg1', 'arg2');
    vi.advanceTimersByTime(100);
    expect(fn).toHaveBeenCalledWith('arg1', 'arg2');
  });
});

describe(throttle, () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should execute immediately on first call', () => {
    const fn = vi.fn();
    const throttled = throttle(fn, 100);

    throttled();
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it('should ignore calls within throttle period', () => {
    const fn = vi.fn();
    const throttled = throttle(fn, 100);

    throttled();
    throttled();
    throttled();
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it('should allow calls after throttle period', () => {
    const fn = vi.fn();
    const throttled = throttle(fn, 100);

    throttled();
    vi.advanceTimersByTime(100);
    throttled();
    expect(fn).toHaveBeenCalledTimes(2);
  });

  it('should pass arguments to function', () => {
    const fn = vi.fn();
    const throttled = throttle(fn, 100);

    throttled('arg1', 'arg2');
    expect(fn).toHaveBeenCalledWith('arg1', 'arg2');
  });
});

describe('TraceRTM utilities', () => {
  const mockItems: Item[] = [
    {
      createdAt: '2024-01-01T00:00:00Z',
      id: '1',
      priority: 'high',
      projectId: 'proj-1',
      status: 'todo',
      title: 'Feature 1',
      type: 'feature',
      updatedAt: '2024-01-01T00:00:00Z',
      version: 1,
      view: 'feature',
    },
    {
      createdAt: '2024-01-01T00:00:00Z',
      id: '2',
      parentId: '1',
      priority: 'medium',
      projectId: 'proj-1',
      status: 'done',
      title: 'Feature 2',
      type: 'feature',
      updatedAt: '2024-01-01T00:00:00Z',
      version: 1,
      view: 'code',
    },
    {
      createdAt: '2024-01-01T00:00:00Z',
      id: '3',
      priority: 'low',
      projectId: 'proj-1',
      status: 'in_progress',
      title: 'Feature 3',
      type: 'feature',
      updatedAt: '2024-01-01T00:00:00Z',
      version: 1,
      view: 'feature',
    },
  ];

  describe(getItemsByView, () => {
    it('should filter items by view', () => {
      const result = getItemsByView(mockItems, 'feature');
      expect(result).toHaveLength(2);
      expect(result.every((item) => item.view === 'feature')).toBeTruthy();
    });

    it('should return empty array for non-existent view', () => {
      const result = getItemsByView(mockItems, 'nonexistent');
      expect(result).toEqual([]);
    });

    it('should handle empty items array', () => {
      const result = getItemsByView([], 'feature');
      expect(result).toEqual([]);
    });
  });

  describe(getItemChildren, () => {
    it('should find children of parent', () => {
      const result = getItemChildren(mockItems, '1');
      expect(result).toHaveLength(1);
      expect(result[0]?.id).toBe('2');
    });

    it('should return empty array for item without children', () => {
      const result = getItemChildren(mockItems, '3');
      expect(result).toEqual([]);
    });

    it('should handle non-existent parent', () => {
      const result = getItemChildren(mockItems, 'nonexistent');
      expect(result).toEqual([]);
    });
  });

  describe(getItemAncestors, () => {
    const hierarchyItems: Item[] = [
      {
        createdAt: '2024-01-01T00:00:00Z',
        id: '1',
        priority: 'high',
        projectId: 'proj-1',
        status: 'todo',
        title: 'Root',
        type: 'feature',
        updatedAt: '2024-01-01T00:00:00Z',
        version: 1,
        view: 'feature',
      },
      {
        createdAt: '2024-01-01T00:00:00Z',
        id: '2',
        parentId: '1',
        priority: 'high',
        projectId: 'proj-1',
        status: 'todo',
        title: 'Child',
        type: 'feature',
        updatedAt: '2024-01-01T00:00:00Z',
        version: 1,
        view: 'feature',
      },
      {
        createdAt: '2024-01-01T00:00:00Z',
        id: '3',
        parentId: '2',
        priority: 'high',
        projectId: 'proj-1',
        status: 'todo',
        title: 'Grandchild',
        type: 'feature',
        updatedAt: '2024-01-01T00:00:00Z',
        version: 1,
        view: 'feature',
      },
    ];

    it('should find all ancestors in order', () => {
      const result = getItemAncestors(hierarchyItems, '3');
      expect(result).toHaveLength(2);
      expect(result[0]?.id).toBe('1');
      expect(result[1]?.id).toBe('2');
    });

    it('should return empty array for root item', () => {
      const result = getItemAncestors(hierarchyItems, '1');
      expect(result).toEqual([]);
    });

    it('should handle orphaned items', () => {
      const result = getItemAncestors(mockItems, '1');
      expect(result).toEqual([]);
    });
  });

  describe(getLinkedItems, () => {
    const mockLinks: Link[] = [
      {
        createdAt: '2024-01-01T00:00:00Z',
        id: 'link-1',
        projectId: 'proj-1',
        sourceId: '1',
        targetId: '2',
        type: 'depends_on',
        updatedAt: '2024-01-01T00:00:00Z',
        version: 1,
      },
      {
        createdAt: '2024-01-01T00:00:00Z',
        id: 'link-2',
        projectId: 'proj-1',
        sourceId: '2',
        targetId: '3',
        type: 'implements',
        updatedAt: '2024-01-01T00:00:00Z',
        version: 1,
      },
    ];

    it('should find source and target items', () => {
      const result = getLinkedItems(mockItems, mockLinks, '2');
      expect(result.sources).toHaveLength(1);
      expect(result.targets).toHaveLength(1);
      expect(result.sources[0]?.id).toBe('1');
      expect(result.targets[0]?.id).toBe('3');
    });

    it('should return empty arrays for unlinked item', () => {
      const result = getLinkedItems(mockItems, [], '1');
      expect(result.sources).toEqual([]);
      expect(result.targets).toEqual([]);
    });

    it('should filter out non-existent items', () => {
      const linksWithMissing: Link[] = [
        {
          created_at: '2024-01-01T00:00:00Z',
          id: 'link-1',
          project_id: 'proj-1',
          sourceId: 'nonexistent',
          targetId: '2',
          type: 'depends_on',
        },
      ];
      const result = getLinkedItems(mockItems, linksWithMissing, '2');
      expect(result.sources).toEqual([]);
    });
  });

  describe(calculateProgress, () => {
    it('should calculate progress percentage', () => {
      const result = calculateProgress(mockItems);
      expect(result).toBeCloseTo(33.333, 1);
    });

    it('should return 0 for empty array', () => {
      const result = calculateProgress([]);
      expect(result).toBe(0);
    });

    it('should return 100 when all done', () => {
      const allDone = mockItems.map((item) => ({
        ...item,
        status: 'done' as const,
      }));
      const result = calculateProgress(allDone);
      expect(result).toBe(100);
    });

    it('should return 0 when none done', () => {
      const noneDone = mockItems.map((item) => Object.assign(item, { status: `todo` as const }));
      const result = calculateProgress(noneDone);
      expect(result).toBe(0);
    });
  });
});

describe('localStorage utilities', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe(getFromStorage, () => {
    it('should retrieve stored value', () => {
      localStorage.setItem('test', JSON.stringify({ value: 42 }));
      const result = getFromStorage('test', { value: 0 });
      expect(result).toEqual({ value: 42 });
    });

    it('should return default for missing key', () => {
      const result = getFromStorage('missing', { value: 0 });
      expect(result).toEqual({ value: 0 });
    });

    it('should return default for invalid JSON', () => {
      localStorage.setItem('test', 'invalid json');
      const result = getFromStorage('test', { value: 0 });
      expect(result).toEqual({ value: 0 });
    });

    it('should handle different data types', () => {
      localStorage.setItem('str', JSON.stringify('hello'));
      localStorage.setItem('num', JSON.stringify(42));
      localStorage.setItem('bool', JSON.stringify(true));

      expect(getFromStorage('str', '')).toBe('hello');
      expect(getFromStorage('num', 0)).toBe(42);
      expect(getFromStorage('bool', false)).toBeTruthy();
    });
  });

  describe(setToStorage, () => {
    it('should store value', () => {
      setToStorage('test', { value: 42 });
      const stored = localStorage.getItem('test');
      expect(JSON.parse(stored!)).toEqual({ value: 42 });
    });

    it('should handle different data types', () => {
      setToStorage('str', 'hello');
      setToStorage('num', 42);
      setToStorage('bool', true);

      expect(JSON.parse(localStorage.getItem('str')!)).toBe('hello');
      expect(JSON.parse(localStorage.getItem('num')!)).toBe(42);
      expect(JSON.parse(localStorage.getItem('bool')!)).toBeTruthy();
    });

    it('should overwrite existing value', () => {
      setToStorage('test', 'old');
      setToStorage('test', 'new');
      expect(getFromStorage('test', '')).toBe('new');
    });
  });

  describe(removeFromStorage, () => {
    it('should remove value', () => {
      localStorage.setItem('test', 'value');
      removeFromStorage('test');
      expect(localStorage.getItem('test')).toBeNull();
    });

    it('should handle non-existent key', () => {
      expect(() => {
        removeFromStorage('missing');
      }).not.toThrow();
    });
  });
});

describe(copyToClipboard, () => {
  it('should use clipboard API when available', async () => {
    const mockWriteText = vi.fn().mockResolvedValue();
    Object.assign(navigator, {
      clipboard: { writeText: mockWriteText },
    });

    const result = await copyToClipboard('test text');
    expect(result).toBeTruthy();
    expect(mockWriteText).toHaveBeenCalledWith('test text');
  });

  it('should handle clipboard API errors', async () => {
    const mockWriteText = vi.fn().mockRejectedValue(new Error('Denied'));
    Object.assign(navigator, {
      clipboard: { writeText: mockWriteText },
    });

    // Should fall back to execCommand
    const result = await copyToClipboard('test text');
    expect(typeof result).toBe('boolean');
  });
});

describe(downloadFile, () => {
  it('should create download link', () => {
    const createElementSpy = vi.spyOn(document, 'createElement');
    const appendChildSpy = vi
      .spyOn(document.body, 'appendChild')
      .mockImplementation((): Node => null as unknown as Node);
    const removeChildSpy = vi
      .spyOn(document.body, 'removeChild')
      .mockImplementation((): Node => null as unknown as Node);

    downloadFile('test content', 'test.txt', 'text/plain');

    expect(createElementSpy).toHaveBeenCalledWith('a');
    expect(appendChildSpy).toHaveBeenCalled();
    expect(removeChildSpy).toHaveBeenCalled();

    createElementSpy.mockRestore();
    appendChildSpy.mockRestore();
    removeChildSpy.mockRestore();
  });

  it('should handle different file types', () => {
    const appendChildSpy = vi
      .spyOn(document.body, 'appendChild')
      .mockImplementation((): Node => null as unknown as Node);
    const removeChildSpy = vi
      .spyOn(document.body, 'removeChild')
      .mockImplementation((): Node => null as unknown as Node);

    downloadFile('{"test": true}', 'data.json', 'application/json');
    expect(appendChildSpy).toHaveBeenCalled();

    appendChildSpy.mockRestore();
    removeChildSpy.mockRestore();
  });
});
