import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

/**
 * Tests for the search worker message handling logic.
 * Since the worker runs in a Web Worker context with `self`, we simulate
 * the message event listener behavior by extracting and testing the logic.
 */

// We mock `self` to capture postMessage calls and simulate the worker environment.
const mockPostMessage = vi.fn();
const messageListeners: Array<(event: MessageEvent) => void> = [];

// Mock the global self for the worker context
const mockSelf = {
  postMessage: mockPostMessage,
  addEventListener: vi.fn((event: string, handler: (...args: any[]) => void) => {
    if (event === 'message') {
      messageListeners.push(handler as (event: MessageEvent) => void);
    }
  }),
};

// Mock performance.now
const mockPerformanceNow = vi.fn();
let performanceCounter = 0;

// Mock Fuse.js
const mockFuseSearch = vi.fn().mockReturnValue([]);
const mockFuseParseIndex = vi.fn().mockReturnValue({});

vi.mock('fuse.js', () => {
  return {
    default: class MockFuse {
      constructor() {
        // no-op
      }
      search = mockFuseSearch;
      static parseIndex = mockFuseParseIndex;
    },
  };
});

describe('search.worker message handling', () => {
  beforeEach(() => {
    vi.resetModules();
    mockPostMessage.mockClear();
    mockFuseSearch.mockClear();
    mockFuseParseIndex.mockClear();
    messageListeners.length = 0;
    performanceCounter = 0;
    mockPerformanceNow.mockImplementation(() => {
      performanceCounter += 5;
      return performanceCounter;
    });

    // Set up global mocks before importing the worker
    vi.stubGlobal('self', mockSelf);
    vi.stubGlobal('performance', { now: mockPerformanceNow });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  async function loadWorker() {
    await import('../search.worker');
  }

  it('posts a "ready" message on load', async () => {
    await loadWorker();
    expect(mockPostMessage).toHaveBeenCalledWith({ type: 'ready' });
  });

  it('registers a message event listener', async () => {
    await loadWorker();
    expect(mockSelf.addEventListener).toHaveBeenCalledWith('message', expect.any(Function));
  });

  it('initializes search index on "init" message', async () => {
    await loadWorker();
    const handler = messageListeners[0];

    const indexData = {
      options: { keys: ['title'] },
      index: {},
      documents: [
        {
          id: '1',
          url: '/test',
          title: 'Test',
          description: '',
          content: '',
          headings: [],
          priority: 1,
        },
      ],
    };

    handler({ data: { type: 'init', indexData } } as MessageEvent);

    expect(mockFuseParseIndex).toHaveBeenCalledWith(indexData.index);
    expect(mockPostMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'init-complete',
        documentCount: 1,
      }),
    );
  });

  it('performs search on "search" message after initialization', async () => {
    await loadWorker();
    const handler = messageListeners[0];

    // First initialize
    const indexData = {
      options: { keys: ['title'] },
      index: {},
      documents: [
        {
          id: '1',
          url: '/test',
          title: 'Test Doc',
          description: '',
          content: '',
          headings: [],
          priority: 1,
        },
      ],
    };
    handler({ data: { type: 'init', indexData } } as MessageEvent);
    mockPostMessage.mockClear();

    // Mock search results
    mockFuseSearch.mockReturnValue([{ item: indexData.documents[0], score: 0.1, matches: [] }]);

    // Now search
    handler({ data: { type: 'search', query: 'Test', maxResults: 10 } } as MessageEvent);

    expect(mockFuseSearch).toHaveBeenCalledWith('Test', { limit: 10 });
    expect(mockPostMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'search-complete',
        query: 'Test',
        resultCount: 1,
      }),
    );
  });

  it('returns empty results for queries shorter than 2 characters', async () => {
    await loadWorker();
    const handler = messageListeners[0];

    // Initialize
    const indexData = {
      options: { keys: ['title'] },
      index: {},
      documents: [],
    };
    handler({ data: { type: 'init', indexData } } as MessageEvent);
    mockPostMessage.mockClear();

    // Search with short query - performSearch returns [] for short queries
    // but does NOT postMessage for short queries, it just returns
    handler({ data: { type: 'search', query: 'a' } } as MessageEvent);

    // Should not have triggered a search-complete (performSearch returns early)
    expect(mockFuseSearch).not.toHaveBeenCalled();
  });

  it('posts error for unknown message types', async () => {
    await loadWorker();
    const handler = messageListeners[0];
    mockPostMessage.mockClear();

    handler({ data: { type: 'unknown-type' } } as MessageEvent);

    expect(mockPostMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'error',
        error: 'Unknown message type: unknown-type',
      }),
    );
  });

  it('posts error when searching before initialization', async () => {
    await loadWorker();
    const handler = messageListeners[0];
    mockPostMessage.mockClear();

    // Search without init - fuse is null, should throw
    handler({ data: { type: 'search', query: 'test query' } } as MessageEvent);

    expect(mockPostMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'error',
        error: 'Search not initialized',
      }),
    );
  });

  it('does nothing for init message without indexData', async () => {
    await loadWorker();
    const handler = messageListeners[0];
    mockPostMessage.mockClear();

    handler({ data: { type: 'init' } } as MessageEvent);

    // No init-complete should be posted since indexData is falsy
    expect(mockPostMessage).not.toHaveBeenCalledWith(
      expect.objectContaining({ type: 'init-complete' }),
    );
  });

  it('does nothing for search message without query', async () => {
    await loadWorker();
    const handler = messageListeners[0];

    // Initialize first
    const indexData = { options: {}, index: {}, documents: [] };
    handler({ data: { type: 'init', indexData } } as MessageEvent);
    mockPostMessage.mockClear();

    handler({ data: { type: 'search' } } as MessageEvent);

    // Should not call search at all since query is undefined
    expect(mockFuseSearch).not.toHaveBeenCalled();
  });
});
