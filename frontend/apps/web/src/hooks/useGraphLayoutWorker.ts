/**
 * Hook for using Web Worker-based graph layout computation
 *
 * This hook provides a React interface to the graph layout worker,
 * preventing main thread blocking during expensive layout computations.
 *
 * Features:
 * - Zero main thread blocking during layout
 * - Progressive layout updates for large graphs
 * - Automatic worker lifecycle management
 * - Type-safe communication via Comlink
 * - Fallback to synchronous layout on worker failure
 *
 * @module useGraphLayoutWorker
 */

import * as Comlink from 'comlink';
import { useCallback, useEffect, useRef, useState } from 'react';

import type { GraphLayoutWorkerAPI } from '@/workers/graphLayout.worker';
import type {
  LayoutEdge,
  LayoutNode,
  LayoutOptions,
  LayoutResult,
} from '@/workers/graphLayout.worker';

import { logger } from '@/lib/logger';

// ============================================================================
// TYPES
// ============================================================================

interface UseGraphLayoutWorkerOptions {
  /** Enable worker (default: true) */
  enabled?: boolean;
  /** Enable progressive layout for large graphs (default: true for >500 nodes) */
  progressive?: boolean;
  /** Batch size for progressive layout (default: 100) */
  batchSize?: number;
  /** Timeout for layout computation in ms (default: 30000) */
  timeout?: number;
  /** Callback for progressive layout updates */
  onProgress?: (result: LayoutResult) => void;
}

interface UseGraphLayoutWorkerResult {
  /** Compute layout for given nodes and edges */
  computeLayout: (
    nodes: LayoutNode[],
    edges: LayoutEdge[],
    options: LayoutOptions,
  ) => Promise<LayoutResult>;
  /** Whether worker is ready */
  isReady: boolean;
  /** Current layout computation in progress */
  isComputing: boolean;
  /** Error from worker initialization or computation */
  error: Error | null;
  /** Current progress (0-1) for progressive layout */
  progress: number;
  /** Terminate worker and clean up */
  terminate: () => void;
}

// ============================================================================
// FALLBACK SYNCHRONOUS LAYOUTS
// ============================================================================

/**
 * Simple grid layout fallback when worker is not available
 */
function fallbackGridLayout(nodes: LayoutNode[], options: LayoutOptions): LayoutResult {
  const { nodeWidth = 200, nodeHeight = 120, nodeSep = 60, marginX = 40, marginY = 40 } = options;

  const cols = Math.ceil(Math.sqrt(nodes.length));
  const positions: Record<string, { x: number; y: number }> = {};
  let maxWidth = 0;
  let maxHeight = 0;

  nodes.forEach((node, index) => {
    const x = marginX + (index % cols) * (nodeWidth + nodeSep);
    const y = marginY + Math.floor(index / cols) * (nodeHeight + nodeSep);
    positions[node.id] = { x, y };
    maxWidth = Math.max(maxWidth, x + nodeWidth + marginX);
    maxHeight = Math.max(maxHeight, y + nodeHeight + marginY);
  });

  return {
    positions,
    size: { height: maxHeight, width: maxWidth },
  };
}

// ============================================================================
// MAIN HOOK
// ============================================================================

/**
 * Hook for Web Worker-based graph layout computation
 *
 * @example
 * ```tsx
 * const { computeLayout, isReady, isComputing } = useGraphLayoutWorker({
 *   progressive: true,
 *   onProgress: (result) => {
 *     logger.info(`Layout ${result['progress'] * 100}% complete`);
 *   }
 * });
 *
 * useEffect(() => {
 *   if (isReady && nodes.length > 0) {
 *     computeLayout(nodes, edges, { algorithm: 'elk' })
 *       .then(result => {
 *         // Apply layout positions
 *         applyPositions(result['positions']);
 *       });
 *   }
 * }, [isReady, nodes, edges]);
 * ```
 */
export function useGraphLayoutWorker(
  options: UseGraphLayoutWorkerOptions = {},
): UseGraphLayoutWorkerResult {
  const {
    enabled = true,
    progressive = true,
    batchSize = 100,
    timeout = 30_000,
    onProgress,
  } = options;

  const workerRef = useRef<Worker | null>(null);
  const apiRef = useRef<Comlink.Remote<GraphLayoutWorkerAPI> | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [isComputing, setIsComputing] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [progress, setProgress] = useState(0);

  // Initialize worker
  useEffect(() => {
    if (!enabled || typeof globalThis.window === 'undefined') {
      return;
    }

    let mounted = true;

    async function initWorker() {
      try {
        // Create worker
        const worker = new Worker(new URL('../workers/graphLayout.worker.ts', import.meta.url), {
          type: 'module',
        });

        // Wrap with Comlink
        const api = Comlink.wrap<GraphLayoutWorkerAPI>(worker);

        workerRef.current = worker;
        apiRef.current = api;

        if (mounted) {
          setIsReady(true);
          setError(null);
        }
      } catch (caughtError) {
        const initError =
          caughtError instanceof Error ? caughtError : new Error(String(caughtError));
        logger.error('[useGraphLayoutWorker] Failed to initialize worker:', initError);
        if (mounted) {
          setError(initError);
          setIsReady(false);
        }
      }
    }

    void initWorker();

    return () => {
      mounted = false;
      if (workerRef.current) {
        workerRef.current.terminate();
        workerRef.current = null;
      }
      if (apiRef.current) {
        apiRef.current[Comlink.releaseProxy]();
        apiRef.current = null;
      }
    };
  }, [enabled]);

  // Compute layout
  const computeLayout = useCallback(
    async (
      nodes: LayoutNode[],
      edges: LayoutEdge[],
      layoutOptions: LayoutOptions,
    ): Promise<LayoutResult> => {
      // Guard: No nodes
      if (nodes.length === 0) {
        return { positions: {}, size: { height: 0, width: 0 } };
      }

      // Guard: Worker not available - use fallback
      if (!isReady || !apiRef.current) {
        logger.warn('[useGraphLayoutWorker] Worker not ready, using fallback layout');
        return fallbackGridLayout(nodes, layoutOptions);
      }

      setIsComputing(true);
      setProgress(0);
      setError(null);

      try {
        const api = apiRef.current;

        // Determine if we should use progressive layout
        const shouldUseProgressive =
          progressive &&
          nodes.length > 500 &&
          (layoutOptions.algorithm === 'grid' || layoutOptions.algorithm === 'circular');

        if (shouldUseProgressive) {
          // Progressive layout with streaming results
          const progressiveOptions = {
            ...layoutOptions,
            progressive: true,
            batchSize,
          };

          const generatorPromise = api.computeLayoutProgressive(nodes, edges, progressiveOptions);

          let finalResult: LayoutResult | null = null;

          // Consume async generator (Comlink proxy returns promise of async iterable at runtime)
          const generator = await (generatorPromise as Promise<AsyncIterable<LayoutResult>>);
          for await (const result of generator) {
            finalResult = result;
            setProgress(result['progress'] ?? 0);

            // Notify progress callback
            if (onProgress && result['isPartial']) {
              onProgress(result);
            }
          }

          return finalResult!;
        }
        // Standard single-shot layout
        const timeoutPromise = new Promise<never>((_, reject) => {
          setTimeout(() => {
            reject(new Error('Layout computation timeout'));
          }, timeout);
        });

        const layoutPromise = api.computeLayout(nodes, edges, layoutOptions);

        const result = await Promise.race([layoutPromise, timeoutPromise]);
        setProgress(1);
        return result;
      } catch (caughtError) {
        const layoutError =
          caughtError instanceof Error ? caughtError : new Error(String(caughtError));
        logger.error('[useGraphLayoutWorker] Layout computation failed:', layoutError);
        setError(layoutError);

        // Fallback to synchronous layout
        logger.warn('[useGraphLayoutWorker] Falling back to synchronous layout');
        return fallbackGridLayout(nodes, layoutOptions);
      } finally {
        setIsComputing(false);
      }
    },
    [isReady, progressive, batchSize, timeout, onProgress],
  );

  // Terminate worker manually
  const terminate = useCallback(() => {
    if (workerRef.current) {
      workerRef.current.terminate();
      workerRef.current = null;
    }
    if (apiRef.current) {
      apiRef.current[Comlink.releaseProxy]();
      apiRef.current = null;
    }
    setIsReady(false);
    setIsComputing(false);
  }, []);

  return {
    computeLayout,
    error,
    isComputing,
    isReady,
    progress,
    terminate,
  };
}

// ============================================================================
// BENCHMARK HOOK
// ============================================================================

/**
 * Hook for benchmarking layout performance
 */
export function useGraphLayoutBenchmark() {
  const workerRef = useRef<Worker | null>(null);
  const apiRef = useRef<Comlink.Remote<GraphLayoutWorkerAPI> | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (typeof globalThis.window === 'undefined') {
      return;
    }

    const worker = new Worker(new URL('../workers/graphLayout.worker.ts', import.meta.url), {
      type: 'module',
    });
    const api = Comlink.wrap<GraphLayoutWorkerAPI>(worker);

    workerRef.current = worker;
    apiRef.current = api;
    setIsReady(true);

    return () => {
      worker.terminate();
      api[Comlink.releaseProxy]();
    };
  }, []);

  const benchmark = useCallback(
    async (
      nodes: LayoutNode[],
      edges: LayoutEdge[],
      algorithm: LayoutOptions['algorithm'],
      iterations = 5,
    ) => {
      if (!isReady || !apiRef.current) {
        throw new Error('Worker not ready');
      }

      return apiRef.current.benchmarkLayout(nodes, edges, {
        algorithm,
        iterations,
      });
    },
    [isReady],
  );

  return { benchmark, isReady };
}
