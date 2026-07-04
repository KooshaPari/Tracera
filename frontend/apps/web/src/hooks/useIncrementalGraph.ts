/**
 * UseIncrementalGraph - React hook for incremental graph loading
 *
 * Features:
 * - Streaming graph data loading
 * - Progress tracking
 * - Predictive prefetch
 * - Viewport-based loading
 * - Automatic state management
 */

import { useCallback, useEffect, useRef, useState } from 'react';

import type {
  GraphEdge,
  GraphNode,
  ProgressInfo,
  StreamMetadata,
  ViewportBounds,
} from '../lib/graph/IncrementalGraphBuilder';

import { IncrementalGraphBuilder } from '../lib/graph/IncrementalGraphBuilder';

export interface UseIncrementalGraphOptions {
  projectId: string;
  viewport: ViewportBounds;
  zoom?: number | undefined;
  bufferPx?: number | undefined;
  chunkSize?: number | undefined;
  enablePrefetch?: boolean | undefined;
  prefetchDirection?: PanDirection | undefined;
  prefetchVelocity?: number | undefined;
  apiBaseUrl?: string | undefined;
}

export type PanDirection =
  | 'north'
  | 'south'
  | 'east'
  | 'west'
  | 'northeast'
  | 'northwest'
  | 'southeast'
  | 'southwest';

export interface GraphState {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: StreamMetadata | undefined;
  isLoading: boolean;
  progress?: ProgressInfo | undefined;
  error?: Error | undefined;
}

export interface UseIncrementalGraphReturn {
  // Current graph state
  state: GraphState;

  // Actions
  loadGraph: () => Promise<void>;
  loadViewport: (viewport: ViewportBounds) => Promise<void>;
  prefetchDirection: (direction: PanDirection, velocity?: number) => Promise<void>;
  abort: () => void;
  reset: () => void;

  // Utilities
  hasNode: (id: string) => boolean;
  hasEdge: (id: string) => boolean;
  getNode: (id: string) => GraphNode | undefined;
  getEdge: (id: string) => GraphEdge | undefined;
}

export function useIncrementalGraph(
  options: UseIncrementalGraphOptions,
): UseIncrementalGraphReturn {
  const {
    projectId,
    viewport,
    zoom = 1,
    bufferPx = 500,
    chunkSize = 50,
    enablePrefetch = true,
    prefetchDirection,
    prefetchVelocity = 0,
    apiBaseUrl = '/api/v1',
  } = options;

  const [state, setState] = useState<GraphState>({
    edges: [],
    isLoading: false,
    nodes: [],
  });

  const builderRef = useRef<IncrementalGraphBuilder | null>(null);
  const prefetchBuilderRef = useRef<IncrementalGraphBuilder | null>(null);
  const prefetchCacheRef = useRef<Map<string, { nodes: GraphNode[]; edges: GraphEdge[] }>>(
    new Map(),
  );

  // Initialize builder
  useEffect(() => {
    builderRef.current = new IncrementalGraphBuilder({
      batchDelay: 16,
      batchSize: chunkSize,

      onComplete: (result) => {
        setState((prev) => ({
          ...prev,
          edges: [...result['edges'].values()],
          isLoading: false,
          metadata: result['metadata'],
          nodes: [...result['nodes'].values()],
          progress: undefined,
        }));
      },

      onEdge: (edge) => {
        setState((prev) => ({
          ...prev,
          edges: [...prev.edges, edge],
        }));
      },

      onError: (error) => {
        setState((prev) => ({
          ...prev,
          error,
          isLoading: false,
        }));
      },

      onNode: (node) => {
        setState((prev) => ({
          ...prev,
          nodes: [...prev.nodes, node],
        }));
      },

      onProgress: (progress) => {
        setState((prev) => ({
          ...prev,
          progress,
        }));
      },
    });

    return () => {
      builderRef.current?.abort();
      prefetchBuilderRef.current?.abort();
    };
  }, [chunkSize]);

  // Load graph for current viewport
  const loadGraph = useCallback(async () => {
    if (!builderRef.current) {
      return;
    }

    setState((prev) => ({
      ...prev,
      isLoading: true,
      error: undefined,
      progress: undefined,
    }));

    const url = `${apiBaseUrl}/projects/${projectId}/graph/stream`;
    const viewportRequest = {
      bufferPx,
      viewport,
      zoom,
    };

    try {
      await builderRef.current.loadFromStream(url, viewportRequest);
    } catch (_error) {
      if (_error instanceof Error && _error.name !== 'AbortError') {
        setState((prev) => ({
          ...prev,
          error: _error,
          isLoading: false,
        }));
      }
    }
  }, [projectId, viewport, zoom, bufferPx, apiBaseUrl]);

  // Load specific viewport
  const loadViewport = useCallback(
    async (newViewport: ViewportBounds) => {
      if (!builderRef.current) {
        return;
      }

      // Check prefetch cache first
      const cacheKey = viewportToCacheKey(newViewport);
      const cached = prefetchCacheRef.current.get(cacheKey);

      if (cached) {
        // Use cached data
        setState((prev) => ({
          ...prev,
          edges: cached.edges,
          isLoading: false,
          nodes: cached.nodes,
        }));
        prefetchCacheRef.current.delete(cacheKey);
        return;
      }

      // Load from server
      setState((prev) => ({
        ...prev,
        error: undefined,
        isLoading: true,
      }));

      const url = `${apiBaseUrl}/projects/${projectId}/graph/stream`;
      const viewportRequest = {
        bufferPx,
        viewport: newViewport,
        zoom,
      };

      try {
        await builderRef.current.loadFromStream(url, viewportRequest);
      } catch (error) {
        if (error instanceof Error && error.name !== 'AbortError') {
          setState((prev) => ({
            ...prev,
            error: error,
            isLoading: false,
          }));
        }
      }
    },
    [projectId, zoom, bufferPx, apiBaseUrl],
  );

  // Prefetch data in a specific direction
  const prefetchDirectionData = useCallback(
    async (direction: PanDirection, velocity = 0) => {
      if (!enablePrefetch) {
        return;
      }

      // Create prefetch builder if needed
      prefetchBuilderRef.current ??= new IncrementalGraphBuilder({
        batchDelay: 50,
        batchSize: 25,
      });

      const url = `${apiBaseUrl}/projects/${projectId}/graph/stream/prefetch`;
      const prefetchRequest = {
        currentViewport: viewport,
        direction,
        velocity,
      };

      try {
        const result = await prefetchBuilderRef.current.loadFromStream(url, prefetchRequest);

        // Cache the result
        const cacheKey = `${direction}-${velocity}`;
        prefetchCacheRef.current.set(cacheKey, {
          edges: [...result['edges'].values()],
          nodes: [...result['nodes'].values()],
        });

        // Limit cache size
        if (prefetchCacheRef.current.size > 8) {
          const firstKey = prefetchCacheRef.current.keys().next().value;
          if (firstKey) {
            prefetchCacheRef.current.delete(firstKey);
          }
        }
      } catch {
        // Silent fail for prefetch
      }
    },
    [projectId, viewport, enablePrefetch, apiBaseUrl],
  );

  // Auto-prefetch based on direction
  useEffect(() => {
    if (prefetchDirection && enablePrefetch) {
      const timer = setTimeout(() => {
        prefetchDirectionData(prefetchDirection, prefetchVelocity ?? 0);
      }, 100); // Debounce prefetch

      return () => {
        clearTimeout(timer);
      };
    }
    return;
  }, [prefetchDirection, prefetchVelocity, enablePrefetch, prefetchDirectionData]);

  // Abort loading
  const abort = useCallback(() => {
    builderRef.current?.abort();
    prefetchBuilderRef.current?.abort();
    setState((prev) => ({
      ...prev,
      isLoading: false,
    }));
  }, []);

  // Reset state
  const reset = useCallback(() => {
    builderRef.current?.reset();
    prefetchBuilderRef.current?.reset();
    prefetchCacheRef.current.clear();
    setState({
      edges: [],
      isLoading: false,
      nodes: [],
    });
  }, []);

  // Utility functions
  const hasNode = useCallback((id: string) => builderRef.current?.hasNode(id) ?? false, []);

  const hasEdge = useCallback((id: string) => builderRef.current?.hasEdge(id) ?? false, []);

  const getNode = useCallback((id: string) => builderRef.current?.getNode(id), []);

  const getEdge = useCallback((id: string) => builderRef.current?.getEdge(id), []);

  return {
    abort,
    getEdge,
    getNode,
    hasEdge,
    hasNode,
    loadGraph,
    loadViewport,
    prefetchDirection: prefetchDirectionData,
    reset,
    state,
  };
}

/**
 * Convert viewport to cache key
 */
function viewportToCacheKey(viewport: ViewportBounds): string {
  return `${Math.round(viewport.minX)},${Math.round(viewport.minY)},${Math.round(viewport.maxX)},${Math.round(viewport.maxY)}`;
}

/**
 * Calculate pan direction from viewport changes
 */
export function calculatePanDirection(
  oldViewport: ViewportBounds,
  newViewport: ViewportBounds,
): PanDirection | null {
  const dx = newViewport.minX - oldViewport.minX;
  const dy = newViewport.minY - oldViewport.minY;

  const threshold = 10; // Minimum movement threshold

  if (Math.abs(dx) < threshold && Math.abs(dy) < threshold) {
    return null;
  }

  // Determine primary direction
  if (Math.abs(dx) > Math.abs(dy) * 2) {
    return dx > 0 ? 'east' : 'west';
  } else if (Math.abs(dy) > Math.abs(dx) * 2) {
    return dy > 0 ? 'south' : 'north';
  }
  // Diagonal
  if (dx > 0 && dy < 0) {
    return 'northeast';
  }
  if (dx < 0 && dy < 0) {
    return 'northwest';
  }
  if (dx > 0 && dy > 0) {
    return 'southeast';
  }
  if (dx < 0 && dy > 0) {
    return 'southwest';
  }

  return null;
}

/**
 * Calculate pan velocity
 */
export function calculatePanVelocity(
  oldViewport: ViewportBounds,
  newViewport: ViewportBounds,
  deltaTime: number, // Milliseconds
): number {
  if (deltaTime === 0) {
    return 0;
  }

  const dx = newViewport.minX - oldViewport.minX;
  const dy = newViewport.minY - oldViewport.minY;
  const distance = Math.hypot(dx, dy);

  return (distance / deltaTime) * 1000; // Pixels per second
}
