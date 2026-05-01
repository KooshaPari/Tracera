/**
 * Search Web Worker
 *
 * Performs search operations in a background thread to avoid blocking the UI.
 * This ensures smooth, responsive search even with large document sets.
 *
 * Benefits:
 * - Non-blocking UI during search
 * - <100ms search performance
 * - Preloaded search index for instant results
 */

import Fuse, { type FuseIndex, type FuseResultMatch, type IFuseOptions } from 'fuse.js';

interface SearchDocument {
  id: string;
  url: string;
  title: string;
  description: string;
  content: string;
  headings: string[];
  structuredData?: Record<string, unknown>;
  priority: number;
}

interface SearchIndex {
  options: IFuseOptions<SearchDocument>;
  index: ReturnType<FuseIndex<SearchDocument>['toJSON']>;
  documents: SearchDocument[];
}

interface SearchMessage {
  type: 'init' | 'search';
  query?: string;
  maxResults?: number;
  indexData?: SearchIndex;
}

interface SearchResult {
  item: SearchDocument;
  score?: number;
  matches?: readonly FuseResultMatch[];
}

let fuse: Fuse<SearchDocument> | null = null;
let documents: SearchDocument[] = [];

/**
 * Initialize Fuse.js with prebuilt index
 */
function initializeSearch(indexData: SearchIndex) {
  try {
    const startTime = performance.now();

    // Load documents
    documents = indexData.documents;

    // Create Fuse instance with prebuilt index
    const fuseIndex = Fuse.parseIndex<SearchDocument>(indexData.index);
    fuse = new Fuse(documents, indexData.options, fuseIndex);

    const duration = performance.now() - startTime;

    self.postMessage({
      type: 'init-complete',
      duration,
      documentCount: documents.length,
    });
  } catch (error) {
    self.postMessage({
      type: 'error',
      error: error instanceof Error ? error.message : 'Failed to initialize search',
    });
  }
}

/**
 * Perform search with Fuse.js
 *
 * @param query - Search query string
 * @param maxResults - Maximum number of results to return (default: 20)
 * @returns Search results array (for direct invocation)
 *
 * @remarks
 * This function has **dual return semantics** which may be confusing:
 *
 * 1. **Primary**: Posts results via `postMessage` with type `'search-complete'`
 *    - This is the intended communication channel when called from the message handler
 *    - The caller (message handler at line 128) ignores the return value
 *
 * 2. **Secondary**: Returns results directly as the function's return value
 *    - This enables direct invocation without message passing
 *    - However, when called via `postMessage` (the typical flow), the return value is discarded
 *
 * **Important**: The message handler (line 128) does NOT use the return value.
 * Results are communicated exclusively through `postMessage`. The return value
 * exists only for edge cases where the function might be called directly
 * (e.g., in tests or if the worker is imported as a module).
 *
 * @example
 * // Via message handler (typical usage) - return value is ignored:
 * self.postMessage({ type: 'search', query: 'docs' });
 * // Results arrive via 'search-complete' message
 *
 * @example
 * // Direct invocation - return value is used:
 * const results = performSearch('docs', 10);
 * // Results returned directly (but postMessage is still sent!)
 */
function performSearch(query: string, maxResults: number = 20): SearchResult[] {
  if (!fuse) {
    throw new Error('Search not initialized');
  }

  if (!query || query.length < 2) {
    return [];
  }

  const startTime = performance.now();

  // Perform search
  const results = fuse.search(query, { limit: maxResults });

  const duration = performance.now() - startTime;

  // Post results via message (primary communication channel)
  self.postMessage({
    type: 'search-complete',
    results: results.map((result) => ({
      item: result.item,
      score: result.score,
      matches: result.matches,
    })),
    query,
    duration,
    resultCount: results.length,
  });

  // Also return results directly (for direct invocation use cases)
  // Note: When called from message handler, this return value is discarded
  return results;
}

/**
 * Message handler
 *
 * Receives search requests and dispatches to appropriate handlers.
 * Note: The return value from performSearch is intentionally ignored;
 * results are communicated back via postMessage from within performSearch.
 */
self.addEventListener('message', (event: MessageEvent<SearchMessage>) => {
  const { type, query, maxResults, indexData } = event.data;

  try {
    switch (type) {
      case 'init':
        if (indexData) {
          initializeSearch(indexData);
        }
        break;

      case 'search':
        if (query) {
          // Return value ignored - results posted via message from performSearch
          performSearch(query, maxResults);
        }
        break;

      default:
        self.postMessage({
          type: 'error',
          error: `Unknown message type: ${type}`,
        });
    }
  } catch (error) {
    self.postMessage({
      type: 'error',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

// Signal that worker is ready
self.postMessage({ type: 'ready' });
