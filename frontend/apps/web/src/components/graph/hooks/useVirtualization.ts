import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

export interface ViewportBounds {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
}

export interface NodePosition {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

export type LODLevel = 'high' | 'medium' | 'low';

export interface VirtualizationMetrics {
  visibleNodeCount: number;
  totalNodeCount: number;
  culledNodeCount: number;
  lodLevel: LODLevel;
  viewportArea: number;
  renderTime: number;
}

interface UseVirtualizationOptions {
  nodeWidth?: number | undefined;
  nodeHeight?: number | undefined;
  padding?: number | undefined;
  enableLOD?: boolean | undefined;
  lodThresholds?: {
    zoomHigh: number;
    zoomMedium: number;
  };
}

/**
 * Hook for managing virtual rendering of large graphs
 * Only renders nodes visible in viewport + padding buffer
 * Implements level-of-detail (LOD) rendering based on zoom level
 */
export function useVirtualization(
  nodes: NodePosition[],
  viewport: {
    x: number;
    y: number;
    width: number;
    height: number;
    zoom: number;
  },
  options: UseVirtualizationOptions = {},
) {
  const {
    padding = 500,
    enableLOD = true,
    lodThresholds = { zoomHigh: 0.8, zoomMedium: 0.5 },
  } = options;

  // Performance tracking
  const renderStartRef = useRef<number>(0);
  const [metrics, setMetrics] = useState<VirtualizationMetrics>({
    culledNodeCount: nodes.length,
    lodLevel: 'medium',
    renderTime: 0,
    totalNodeCount: nodes.length,
    viewportArea: 0,
    visibleNodeCount: 0,
  });

  // Calculate viewport bounds with padding
  const viewportBounds = useMemo((): ViewportBounds => {
    const left = viewport.x - padding;
    const top = viewport.y - padding;
    const right = viewport.x + viewport.width / viewport.zoom + padding;
    const bottom = viewport.y + viewport.height / viewport.zoom + padding;

    return { maxX: right, maxY: bottom, minX: left, minY: top };
  }, [viewport, padding]);

  // Determine LOD level based on zoom
  const lodLevel = useMemo((): LODLevel => {
    if (!enableLOD) {
      return 'high';
    }

    if (viewport.zoom >= lodThresholds.zoomHigh) {
      return 'high';
    }
    if (viewport.zoom >= lodThresholds.zoomMedium) {
      return 'medium';
    }
    return 'low';
  }, [viewport.zoom, enableLOD, lodThresholds]);

  // Calculate visible nodes
  const visibleNodes = useMemo(() => {
    renderStartRef.current = performance.now();

    const visible: NodePosition[] = [];
    let culled = 0;

    for (const node of nodes) {
      const isVisible =
        node.x + node.width > viewportBounds.minX &&
        node.x < viewportBounds.maxX &&
        node.y + node.height > viewportBounds.minY &&
        node.y < viewportBounds.maxY;

      if (isVisible) {
        visible.push(node);
      } else {
        culled += 1;
      }
    }

    const renderTime = performance.now() - renderStartRef.current;

    setMetrics({
      culledNodeCount: culled,
      lodLevel,
      renderTime,
      totalNodeCount: nodes.length,
      viewportArea: viewport.width * viewport.height,
      visibleNodeCount: visible.length,
    });

    return visible;
  }, [nodes, viewportBounds, viewport, lodLevel]);

  // Get LOD simplified node data
  const getNodeLOD = useCallback(
    (nodeId: string, data: Record<string, unknown>) => {
      switch (lodLevel) {
        case 'low': {
          // Only show ID and type for very zoomed out
          return {
            id: nodeId,
            type: data['type'],
          };
        }
        case 'medium': {
          // Show ID, type, and label
          return {
            id: nodeId,
            label: data['label'],
            type: data['type'],
          };
        }
        case 'high': {
          // Show full node data
          return data;
        }
        default: {
          return data;
        }
      }
    },
    [lodLevel],
  );

  // Get simplified node renderer based on LOD level
  const getSimplifiedNodeComponent = useCallback(() => {
    switch (lodLevel) {
      case 'low': {
        return 'simplifiedPill';
      }
      case 'medium': {
        return 'mediumPill';
      }
      case 'high': {
        return 'richPill';
      }
      default: {
        return 'richPill';
      }
    }
  }, [lodLevel]);

  // Track viewport changes
  useEffect(() => {
    // Performance optimization: batch updates
    const timer = requestAnimationFrame(() => {
      // Viewport change will trigger useMemo recalculation
    });

    return () => {
      cancelAnimationFrame(timer);
    };
  }, []);

  return {
    // Rendered nodes
    visibleNodes,
    visibleNodeIds: new Set(visibleNodes.map((n) => n.id)),

    // LOD management
    lodLevel,
    getNodeLOD,
    getSimplifiedNodeComponent,

    // Viewport
    viewportBounds,

    // Metrics
    metrics,
    cullingRatio: nodes.length > 0 ? metrics.culledNodeCount / nodes.length : 0,
  };
}

/**
 * Hook for tracking intersection observer visibility
 * More efficient for very large datasets
 */
export function useIntersectionVisibility(
  containerRef: React.RefObject<HTMLElement>,
  _nodeIds: string[],
  options: IntersectionObserverInit = {},
) {
  const [visibleIds, setVisibleIds] = useState<Set<string>>(new Set());
  const observerRef = useRef<IntersectionObserver | null>(null);
  const nodeRefsMap = useRef<Map<string, Element>>(new Map());

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        setVisibleIds((prev) => {
          const next = new Set(prev);
          for (const entry of entries) {
            const { nodeId } = (entry.target as HTMLElement).dataset;
            if (nodeId) {
              if (entry.isIntersecting) {
                next.add(nodeId);
              } else {
                next.delete(nodeId);
              }
            }
          }
          return next;
        });
      },
      {
        root: containerRef.current,
        rootMargin: '200px',
        threshold: 0,
        ...options,
      },
    );

    observerRef.current = observer;

    return () => {
      observer.disconnect();
      observerRef.current = null;
    };
  }, [containerRef, options]);

  const registerNode = useCallback((nodeId: string, element: Element) => {
    nodeRefsMap.current.set(nodeId, element);
    observerRef.current?.observe(element);
  }, []);

  const unregisterNode = useCallback((nodeId: string) => {
    const element = nodeRefsMap.current.get(nodeId);
    if (element && observerRef.current) {
      observerRef.current.unobserve(element);
    }
    nodeRefsMap.current.delete(nodeId);
  }, []);

  return {
    registerNode,
    unregisterNode,
    visibleIds,
  };
}

/**
 * Hook for progressive loading of detailed node data
 */
export function useProgressiveLoading<T extends { id: string }>(
  items: T[],
  batchSize = 50,
  delay = 100,
) {
  const [loadedItems, setLoadedItems] = useState<Set<string>>(new Set());
  const loaderRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    if (loadedItems.size >= items.length) {
      return;
    }

    loaderRef.current = globalThis.setTimeout(() => {
      setLoadedItems((prev) => {
        const next = new Set(prev);
        const itemsToLoad = items.slice(prev.size, prev.size + batchSize).map((item) => item.id);

        itemsToLoad.forEach((id) => next.add(id));
        return next;
      });
    }, delay);

    return () => {
      if (loaderRef.current) {
        clearTimeout(loaderRef.current);
      }
    };
  }, [items, batchSize, delay, loadedItems]);

  const resetLoading = useCallback(() => {
    setLoadedItems(new Set());
  }, []);

  const isLoaded = useCallback((itemId: string) => loadedItems.has(itemId), [loadedItems]);

  const progress = items.length > 0 ? (loadedItems.size / items.length) * 100 : 100;

  return {
    allLoaded: loadedItems.size === items.length,
    isLoaded,
    loadedItems,
    progress,
    resetLoading,
  };
}
