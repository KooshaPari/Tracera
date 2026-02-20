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

  // Return results with performance metrics
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

  return results;
}

/**
 * Message handler
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
