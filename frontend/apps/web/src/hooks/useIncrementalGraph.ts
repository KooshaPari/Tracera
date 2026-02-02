/**
 * useIncrementalGraph - React hook for incremental graph loading
 *
 * Features:
 * - Streaming graph data loading
 * - Progress tracking
 * - Predictive prefetch
 * - Viewport-based loading
 * - Automatic state management
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { IncrementalGraphBuilder } from '../lib/graph/IncrementalGraphBuilder';
import type {
  GraphNode,
  GraphEdge,
  ProgressInfo,
  StreamMetadata,
  ViewportBounds,
} from '../lib/graph/IncrementalGraphBuilder';

export interface UseIncrementalGraphOptions {
  projectId: string;
  viewport: ViewportBounds;
  zoom?: number;
  bufferPx?: number;
  chunkSize?: number;
  enablePrefetch?: boolean;
  prefetchDirection?: PanDirection;
  prefetchVelocity?: number;
  apiBaseUrl?: string;
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
  metadata?: StreamMetadata;
  isLoading: boolean;
  progress?: ProgressInfo;
  error?: Error;
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
  options: UseIncrementalGraphOptions
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
    nodes: [],
    edges: [],
    isLoading: false,
  });

  const builderRef = useRef<IncrementalGraphBuilder | null>(null);
  const prefetchBuilderRef = useRef<IncrementalGraphBuilder | null>(null);
  const prefetchCacheRef = useRef<Map<string, { nodes: GraphNode[]; edges: GraphEdge[] }>>(
    new Map()
  );

  // Initialize builder
  useEffect(() => {
    builderRef.current = new IncrementalGraphBuilder({
      batchSize: chunkSize,
      batchDelay: 16,

      onProgress: (progress) => {
        setState((prev) => ({
          ...prev,
          progress,
        }));
      },

      onNode: (node) => {
        setState((prev) => ({
          ...prev,
          nodes: [...prev.nodes, node],
        }));
      },

      onEdge: (edge) => {
        setState((prev) => ({
          ...prev,
          edges: [...prev.edges, edge],
        }));
      },

      onComplete: (result) => {
        setState((prev) => ({
          ...prev,
          nodes: Array.from(result['nodes'].values()),
          edges: Array.from(result['edges'].values()),
          metadata: result['metadata'],
          isLoading: false,
          progress: undefined,
        }));
      },

      onError: (error) => {
        setState((prev) => ({
          ...prev,
          error,
          isLoading: false,
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
    if (!builderRef.current) return;

    setState((prev) => ({
      ...prev,
      isLoading: true,
      error: undefined,
      progress: undefined,
    }));

    const url = `${apiBaseUrl}/projects/${projectId}/graph/stream`;
    const viewportRequest = {
      viewport,
      zoom,
      bufferPx,
    };

    try {
      await builderRef.current.loadFromStream(url, viewportRequest);
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        setState((prev) => ({
          ...prev,
          error: error as Error,
          isLoading: false,
        }));
      }
    }
  }, [projectId, viewport, zoom, bufferPx, apiBaseUrl]);

  // Load specific viewport
  const loadViewport = useCallback(
    async (newViewport: ViewportBounds) => {
      if (!builderRef.current) return;

      // Check prefetch cache first
      const cacheKey = viewportToCacheKey(newViewport);
      const cached = prefetchCacheRef.current.get(cacheKey);

      if (cached) {
        // Use cached data
        setState((prev) => ({
          ...prev,
          nodes: cached.nodes,
          edges: cached.edges,
          isLoading: false,
        }));
        prefetchCacheRef.current.delete(cacheKey);
        return;
      }

      // Load from server
      setState((prev) => ({
        ...prev,
        isLoading: true,
        error: undefined,
      }));

      const url = `${apiBaseUrl}/projects/${projectId}/graph/stream`;
      const viewportRequest = {
        viewport: newViewport,
        zoom,
        bufferPx,
      };

      try {
        await builderRef.current.loadFromStream(url, viewportRequest);
      } catch (error) {
        if (error instanceof Error && error.name !== 'AbortError') {
          setState((prev) => ({
            ...prev,
            error: error as Error,
            isLoading: false,
          }));
        }
      }
    },
    [projectId, zoom, bufferPx, apiBaseUrl]
  );

  // Prefetch data in a specific direction
  const prefetchDirectionData = useCallback(
    async (direction: PanDirection, velocity: number = 0) => {
      if (!enablePrefetch) return;

      // Create prefetch builder if needed
      if (!prefetchBuilderRef.current) {
        prefetchBuilderRef.current = new IncrementalGraphBuilder({
          batchSize: 25,
          batchDelay: 50,
        });
      }

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
          nodes: Array.from(result['nodes'].values()),
          edges: Array.from(result['edges'].values()),
        });

        // Limit cache size
        if (prefetchCacheRef.current.size > 8) {
          const firstKey = prefetchCacheRef.current.keys().next().value;
          if (firstKey) {
            prefetchCacheRef.current.delete(firstKey);
          }
        }
      } catch (error) {
        // Silent fail for prefetch
        console.warn('Prefetch failed:', error);
      }
    },
    [projectId, viewport, enablePrefetch, apiBaseUrl]
  );

  // Auto-prefetch based on direction
  useEffect(() => {
    if (prefetchDirection && enablePrefetch) {
      const timer = setTimeout(() => {
        void prefetchDirectionData(prefetchDirection, prefetchVelocity);
      }, 100); // Debounce prefetch

      return () => clearTimeout(timer);
    }
    return undefined;
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
      nodes: [],
      edges: [],
      isLoading: false,
    });
  }, []);

  // Utility functions
  const hasNode = useCallback(
    (id: string) => builderRef.current?.hasNode(id) ?? false,
    []
  );

  const hasEdge = useCallback(
    (id: string) => builderRef.current?.hasEdge(id) ?? false,
    []
  );

  const getNode = useCallback(
    (id: string) => builderRef.current?.getNode(id),
    []
  );

  const getEdge = useCallback(
    (id: string) => builderRef.current?.getEdge(id),
    []
  );

  return {
    state,
    loadGraph,
    loadViewport,
    prefetchDirection: prefetchDirectionData,
    abort,
    reset,
    hasNode,
    hasEdge,
    getNode,
    getEdge,
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
  newViewport: ViewportBounds
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
  } else {
    // Diagonal
    if (dx > 0 && dy < 0) return 'northeast';
    if (dx < 0 && dy < 0) return 'northwest';
    if (dx > 0 && dy > 0) return 'southeast';
    if (dx < 0 && dy > 0) return 'southwest';
  }

  return null;
}

/**
 * Calculate pan velocity
 */
export function calculatePanVelocity(
  oldViewport: ViewportBounds,
  newViewport: ViewportBounds,
  deltaTime: number // milliseconds
): number {
  if (deltaTime === 0) return 0;

  const dx = newViewport.minX - oldViewport.minX;
  const dy = newViewport.minY - oldViewport.minY;
  const distance = Math.sqrt(dx * dx + dy * dy);

  return (distance / deltaTime) * 1000; // pixels per second
}
