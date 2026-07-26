// Performance optimization hook
// Handles virtual scrolling, lazy edge rendering, memoization, and performance monitoring

import type { Edge, Node } from '@xyflow/react';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

/**
 * Performance metrics
 */
export interface PerformanceMetrics {
  totalNodes: number;
  totalEdges: number;
  visibleNodes: number;
  visibleEdges: number;
  renderTime: number;
  memoryUsage: number;
  fps: number;
}

/**
 * Virtual scrolling configuration
 */
export interface VirtualScrollConfig {
  enabled: boolean;
  threshold: number; // Number of items to trigger virtualization
  itemsPerPage: number;
  overscan: number; // Extra items to render outside viewport
}

/**
 * Hook for performance optimization in large graphs
 */
export function usePerformance<T extends Node>(
  nodes: T[],
  edges: Edge[],
  config: Partial<VirtualScrollConfig> = {},
) {
  const finalConfig: VirtualScrollConfig = {
    enabled: true,
    threshold: 500,
    itemsPerPage: 50,
    overscan: 10,
    ...config,
  };

  // Performance metrics tracking
  const metricsRef = useRef<PerformanceMetrics>({
    fps: 60,
    memoryUsage: 0,
    renderTime: 0,
    totalEdges: edges.length,
    totalNodes: nodes.length,
    visibleEdges: edges.length,
    visibleNodes: nodes.length,
  });

  const [metrics, setMetrics] = useState<PerformanceMetrics>(metricsRef.current);
  const [visibleRange, setVisibleRange] = useState({
    end: finalConfig.itemsPerPage,
    start: 0,
  });

  // Determine if virtualization is needed
  const shouldVirtualize = nodes.length > finalConfig.threshold;

  // Get visible nodes (with virtualization if needed)
  const visibleNodes = useMemo(() => {
    if (!shouldVirtualize || !finalConfig.enabled) {
      return nodes;
    }

    const start = Math.max(0, visibleRange.start - finalConfig.overscan);
    const end = Math.min(nodes.length, visibleRange.end + finalConfig.overscan);

    return nodes.slice(start, end);
  }, [nodes, visibleRange, shouldVirtualize, finalConfig.enabled, finalConfig.overscan]);

  // Get visible edges (render edges only for visible nodes)
  const visibleEdges = useMemo(() => {
    if (!shouldVirtualize || !finalConfig.enabled) {
      return edges;
    }

    const visibleNodeIds = new Set(visibleNodes.map((n) => n.id));

    return edges.filter(
      (edge) => visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target),
    );
  }, [edges, visibleNodes, shouldVirtualize, finalConfig.enabled]);

  // Measure render time
  useEffect(() => {
    const startTime = performance.now();

    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;

      metricsRef.current = {
        ...metricsRef.current,
        renderTime,
        totalNodes: nodes.length,
        totalEdges: edges.length,
        visibleNodes: visibleNodes.length,
        visibleEdges: visibleEdges.length,
      };

      setMetrics(metricsRef.current);
    };
  }, [nodes.length, edges.length, visibleNodes.length, visibleEdges.length]);

  // Monitor memory usage (if available in Chrome DevTools)
  useEffect(() => {
    const interval = setInterval(() => {
      // Check if performance.memory is available (Chrome only)
      const perfMemory = performance as any;
      if (perfMemory.memory?.usedJSHeapSize) {
        const memoryMB = (perfMemory.memory.usedJSHeapSize / 1_048_576).toFixed(2);
        metricsRef.current.memoryUsage = Number.parseFloat(memoryMB);
        setMetrics({ ...metricsRef.current });
      }
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  // Monitor FPS
  useEffect(() => {
    let frameCount = 0;
    let lastTime = performance.now();

    const countFrame = () => {
      frameCount += 1;
      const currentTime = performance.now();

      if (currentTime - lastTime >= 1000) {
        metricsRef.current.fps = frameCount;
        setMetrics({ ...metricsRef.current });
        frameCount = 0;
        lastTime = currentTime;
      }

      requestAnimationFrame(countFrame);
    };

    const animationId = requestAnimationFrame(countFrame);

    return () => {
      cancelAnimationFrame(animationId);
    };
  }, []);

  // Handle scroll/viewport change
  const handleViewportChange = useCallback((newStart: number, newEnd: number) => {
    setVisibleRange({ end: newEnd, start: newStart });
  }, []);

  // Memoized lazy edge renderer
  const lazyRenderEdges = useCallback(
    (viewportNodes: Set<string>): Edge[] =>
      edges.filter((edge) => viewportNodes.has(edge.source) && viewportNodes.has(edge.target)),
    [edges],
  );

  // Memoized node clustering (group nearby nodes)
  const clusterNodes = useCallback(
    (maxClusterSize = 10): Map<string, T[]> => {
      const clusters = new Map<string, T[]>();

      let clusterIndex = 0;
      for (let i = 0; i < nodes.length; i += maxClusterSize) {
        const cluster = nodes.slice(i, i + maxClusterSize);
        clusters.set(`cluster-${(clusterIndex += 1)}`, cluster);
      }

      return clusters;
    },
    [nodes],
  );

  return {
    // Virtual scrolling
    visibleNodes,
    visibleEdges,
    shouldVirtualize,
    visibleRange,
    handleViewportChange,

    // Lazy rendering
    lazyRenderEdges,

    // Clustering
    clusterNodes,

    // Metrics
    metrics,
    getMetrics: () => ({ ...metricsRef.current }),

    // Utilities
    getTotalRenderCount: () => visibleNodes.length + visibleEdges.length,
    getReductionPercent: () =>
      Math.round(
        (1 - (visibleNodes.length + visibleEdges.length) / (nodes.length + edges.length)) * 100,
      ),
  };
}

/**
 * Hook for memoizing expensive calculations
 */
export function useMemoizedCalculation<T>(
  calculateFn: () => T,
  dependencies: React.DependencyList,
  cacheSize = 10,
) {
  const cacheRef = useRef<Map<string, T>>(new Map());
  const keysRef = useRef<string[]>([]);

  return useMemo(() => {
    const depKey = JSON.stringify(dependencies);

    // Check cache
    if (cacheRef.current.has(depKey)) {
      return cacheRef.current.get(depKey)!;
    }

    // Calculate new value
    const result = calculateFn();

    // Update cache with size limit
    cacheRef.current.set(depKey, result);
    keysRef.current.push(depKey);

    if (keysRef.current.length > cacheSize) {
      const oldestKey = keysRef.current.shift();
      if (oldestKey) {
        cacheRef.current.delete(oldestKey);
      }
    }

    return result;
  }, [...dependencies, cacheSize, calculateFn, dependencies]);
}

/**
 * Hook for debouncing expensive operations
 */
export function useDebouncedCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay = 300,
): (...args: Parameters<T>) => void {
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const debouncedCallback = useCallback(
    (...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        callback(...args);
      }, delay);
    },
    [callback, delay],
  );

  useEffect(
    () => () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    },
    [],
  );

  return debouncedCallback;
}

/**
 * Hook for throttling frequent operations
 */
export function useThrottledCallback<T extends (...args: any[]) => any>(
  callback: T,
  interval = 300,
): (...args: Parameters<T>) => void {
  const lastCallRef = useRef<number>(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const throttledCallback = useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now();

      if (now - lastCallRef.current >= interval) {
        lastCallRef.current = now;
        callback(...args);
      } else {
        // Schedule call for later
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }

        timeoutRef.current = setTimeout(
          () => {
            lastCallRef.current = Date.now();
            callback(...args);
          },
          interval - (now - lastCallRef.current),
        );
      }
    },
    [callback, interval],
  );

  useEffect(
    () => () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    },
    [],
  );

  return throttledCallback;
}
