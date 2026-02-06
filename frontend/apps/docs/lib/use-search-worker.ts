/**
 * Search Worker Hook
 *
 * React hook to manage the search web worker lifecycle and perform searches.
 * Provides a simple interface for instant search with performance metrics.
 */

import { useEffect, useRef, useState, useCallback } from 'react';

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

interface SearchResult {
  item: SearchDocument;
  score?: number;
  matches?: readonly {
    indices: readonly [number, number][];
    value?: string;
    key?: string;
  }[];
}

interface SearchPerformance {
  initDuration?: number;
  searchDuration?: number;
  resultCount?: number;
}

interface UseSearchWorkerReturn {
  search: (query: string, maxResults?: number) => void;
  results: SearchResult[];
  isReady: boolean;
  isSearching: boolean;
  error: string | null;
  performance: SearchPerformance;
}

/**
 * Hook to use search web worker
 */
export function useSearchWorker(): UseSearchWorkerReturn {
  const workerRef = useRef<Worker | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [performance, setPerformance] = useState<SearchPerformance>({});

  // Initialize worker
  useEffect(() => {
    // Create worker
    const worker = new Worker(new URL('./search.worker.ts', import.meta.url), {
      type: 'module',
    });

    workerRef.current = worker;

    // Handle messages from worker
    worker.addEventListener('message', (event) => {
      const {
        type,
        duration,
        documentCount,
        results,
        query,
        resultCount,
        error: workerError,
      } = event.data;

      switch (type) {
        case 'ready':
          // Worker is ready, load search index
          loadSearchIndex(worker);
          break;

        case 'init-complete':
          setIsReady(true);
          setPerformance((prev) => ({ ...prev, initDuration: duration }));
          console.log(
            `✅ Search worker initialized in ${duration.toFixed(2)}ms (${documentCount} documents)`,
          );
          break;

        case 'search-complete':
          setResults(results);
          setIsSearching(false);
          setPerformance((prev) => ({
            ...prev,
            searchDuration: duration,
            resultCount,
          }));
          console.log(
            `🔍 Search completed in ${duration.toFixed(2)}ms (${resultCount} results for "${query}")`,
          );
          break;

        case 'error':
          setError(workerError);
          setIsSearching(false);
          console.error('❌ Search worker error:', workerError);
          break;
      }
    });

    // Cleanup
    return () => {
      worker.terminate();
    };
  }, []);

  /**
   * Load search index into worker
   */
  const loadSearchIndex = useCallback(async (worker: Worker) => {
    try {
      const response = await fetch('/search-index.json');
      if (!response.ok) {
        throw new Error(`Failed to load search index: ${response.statusText}`);
      }

      const indexData = await response.json();

      worker.postMessage({
        type: 'init',
        indexData,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load search index';
      setError(errorMessage);
      console.error('❌ Failed to load search index:', error);
    }
  }, []);

  /**
   * Perform search
   */
  const search = useCallback(
    (query: string, maxResults: number = 20) => {
      if (!workerRef.current || !isReady) {
        console.warn('Search worker not ready');
        return;
      }

      if (!query || query.length < 2) {
        setResults([]);
        return;
      }

      setIsSearching(true);
      workerRef.current.postMessage({
        type: 'search',
        query,
        maxResults,
      });
    },
    [isReady],
  );

  return {
    search,
    results,
    isReady,
    isSearching,
    error,
    performance,
  };
}
