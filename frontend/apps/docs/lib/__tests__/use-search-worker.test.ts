import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import { useSearchWorker } from '../use-search-worker';

// Mock Worker class
class MockWorker {
  listeners: Record<string, Array<(event: any) => void>> = {};
  postMessage = vi.fn();
  terminate = vi.fn();

  addEventListener(event: string, handler: (event: any) => void) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(handler);
  }

  removeEventListener(event: string, handler: (event: any) => void) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter((h) => h !== handler);
    }
  }

  // Helper to simulate messages from the worker
  simulateMessage(data: any) {
    const messageListeners = this.listeners['message'] || [];
    messageListeners.forEach((handler) => handler({ data }));
  }
}

let mockWorkerInstance: MockWorker;

vi.stubGlobal(
  'Worker',
  class {
    constructor() {
      mockWorkerInstance = new MockWorker();
      return mockWorkerInstance;
    }
  },
);

// Mock fetch for loading search index
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

describe('useSearchWorker', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ options: {}, index: {}, documents: [] }),
    });
    // Suppress console output in tests
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('initializes with default state', () => {
    const { result } = renderHook(() => useSearchWorker());

    expect(result.current.isReady).toBe(false);
    expect(result.current.isSearching).toBe(false);
    expect(result.current.results).toEqual([]);
    expect(result.current.error).toBeNull();
    expect(result.current.performance).toEqual({});
  });

  it('provides a search function', () => {
    const { result } = renderHook(() => useSearchWorker());
    expect(typeof result.current.search).toBe('function');
  });

  it('terminates the worker on unmount', () => {
    const { unmount } = renderHook(() => useSearchWorker());
    unmount();
    expect(mockWorkerInstance.terminate).toHaveBeenCalled();
  });

  it('loads search index when worker sends ready message', async () => {
    renderHook(() => useSearchWorker());

    // Simulate worker ready message
    await act(async () => {
      mockWorkerInstance.simulateMessage({ type: 'ready' });
    });

    expect(mockFetch).toHaveBeenCalledWith('/search-index.json');
  });

  it('sends init message to worker after fetching index', async () => {
    const indexData = { options: {}, index: {}, documents: [{ id: 'test' }] };
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(indexData),
    });

    renderHook(() => useSearchWorker());

    await act(async () => {
      mockWorkerInstance.simulateMessage({ type: 'ready' });
      // Wait for fetch promise to resolve
      await new Promise((r) => setTimeout(r, 0));
    });

    expect(mockWorkerInstance.postMessage).toHaveBeenCalledWith({
      type: 'init',
      indexData,
    });
  });

  it('sets isReady to true on init-complete message', async () => {
    const { result } = renderHook(() => useSearchWorker());

    await act(async () => {
      mockWorkerInstance.simulateMessage({
        type: 'init-complete',
        duration: 15.5,
        documentCount: 42,
      });
    });

    expect(result.current.isReady).toBe(true);
    expect(result.current.performance.initDuration).toBe(15.5);
  });

  it('updates results on search-complete message', async () => {
    const { result } = renderHook(() => useSearchWorker());

    const searchResults = [{ item: { id: '1', title: 'Test', url: '/test' }, score: 0.1 }];

    await act(async () => {
      mockWorkerInstance.simulateMessage({
        type: 'search-complete',
        results: searchResults,
        query: 'test',
        duration: 5.2,
        resultCount: 1,
      });
    });

    expect(result.current.results).toEqual(searchResults);
    expect(result.current.isSearching).toBe(false);
    expect(result.current.performance.searchDuration).toBe(5.2);
    expect(result.current.performance.resultCount).toBe(1);
  });

  it('sets error on error message from worker', async () => {
    const { result } = renderHook(() => useSearchWorker());

    await act(async () => {
      mockWorkerInstance.simulateMessage({
        type: 'error',
        error: 'Something went wrong',
      });
    });

    expect(result.current.error).toBe('Something went wrong');
    expect(result.current.isSearching).toBe(false);
  });

  it('does not search when worker is not ready', async () => {
    const { result } = renderHook(() => useSearchWorker());

    act(() => {
      result.current.search('test query');
    });

    // Worker should NOT receive a search message since it's not ready
    expect(mockWorkerInstance.postMessage).not.toHaveBeenCalledWith(
      expect.objectContaining({ type: 'search' }),
    );
  });

  it('clears results for queries shorter than 2 characters', async () => {
    const { result } = renderHook(() => useSearchWorker());

    // First, set isReady to true
    await act(async () => {
      mockWorkerInstance.simulateMessage({
        type: 'init-complete',
        duration: 10,
        documentCount: 5,
      });
    });

    // Add some existing results
    await act(async () => {
      mockWorkerInstance.simulateMessage({
        type: 'search-complete',
        results: [{ item: { id: '1' }, score: 0.1 }],
        query: 'test',
        duration: 2,
        resultCount: 1,
      });
    });

    expect(result.current.results).toHaveLength(1);

    // Now search with a short query
    act(() => {
      result.current.search('a');
    });

    expect(result.current.results).toEqual([]);
  });

  it('sends search message to worker for valid queries', async () => {
    const { result } = renderHook(() => useSearchWorker());

    // Make worker ready
    await act(async () => {
      mockWorkerInstance.simulateMessage({
        type: 'init-complete',
        duration: 10,
        documentCount: 5,
      });
    });

    act(() => {
      result.current.search('hello world', 30);
    });

    expect(mockWorkerInstance.postMessage).toHaveBeenCalledWith({
      type: 'search',
      query: 'hello world',
      maxResults: 30,
    });
    expect(result.current.isSearching).toBe(true);
  });

  it('sets error when fetch fails for search index', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      statusText: 'Not Found',
    });

    const { result } = renderHook(() => useSearchWorker());

    await act(async () => {
      mockWorkerInstance.simulateMessage({ type: 'ready' });
      await new Promise((r) => setTimeout(r, 0));
    });

    expect(result.current.error).toBe('Failed to load search index: Not Found');
  });

  it('uses default maxResults of 20 when not specified', async () => {
    const { result } = renderHook(() => useSearchWorker());

    await act(async () => {
      mockWorkerInstance.simulateMessage({
        type: 'init-complete',
        duration: 10,
        documentCount: 5,
      });
    });

    act(() => {
      result.current.search('query');
    });

    expect(mockWorkerInstance.postMessage).toHaveBeenCalledWith({
      type: 'search',
      query: 'query',
      maxResults: 20,
    });
  });
});
