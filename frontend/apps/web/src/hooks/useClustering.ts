/**
 * Clustering Hook
 *
 * Manages graph clustering state for large-scale visualization.
 * Provides cluster expansion/collapse, incremental loading, and cache management.
 */

import { useCallback, useEffect, useMemo, useState } from 'react';

import type { Item, Link } from '@tracertm/types';

import type { ClusterNode, ClusteringResult } from '../lib/graphClustering';

import {
  adaptiveClustering,
  calculateClusteringQuality,
  expandCluster,
  extractClusterEdges,
  labelPropagationClustering,
  louvainClustering,
} from '../lib/graphClustering';

/**
 * Clustering algorithm type
 */
export type ClusteringAlgorithm = 'louvain' | 'labelProp' | 'adaptive';

/**
 * Clustering configuration
 */
export interface ClusteringConfig {
  algorithm: ClusteringAlgorithm;
  targetClusters?: number;
  resolution?: number;
  minClusterSize?: number;
  enableCache?: boolean;
}

/**
 * Cluster expansion state
 */
interface ExpansionState {
  expandedClusters: Set<string>;
  visibleItems: Set<string>;
  activeClusters: Set<string>;
}

/**
 * Clustering hook return type
 */
export interface UseClusteringResult {
  // Current clustering result
  clustering: ClusteringResult | null;

  // Expansion state
  expandedClusters: Set<string>;
  visibleClusters: ClusterNode[];
  visibleItems: Item[];

  // Actions
  toggleCluster: (clusterId: string) => void;
  expandClusterById: (clusterId: string) => void;
  collapseCluster: (clusterId: string) => void;
  expandAll: () => void;
  collapseAll: () => void;
  drillDownToCluster: (clusterId: string) => void;

  // Configuration
  updateConfig: (config: Partial<ClusteringConfig>) => void;
  recluster: () => void;

  // Metrics
  compressionRatio: number;
  clusterCount: number;
  quality: {
    modularity: number;
    coverage: number;
    silhouette: number;
    conductance: number;
  } | null;

  // State
  isProcessing: boolean;
  error: Error | null;
}

/**
 * Default clustering configuration
 */
const DEFAULT_CONFIG: ClusteringConfig = {
  algorithm: 'adaptive',
  enableCache: true,
  minClusterSize: 2,
  resolution: 1,
  targetClusters: 500,
};

/**
 * Use clustering hook
 */
export function useClustering(
  items: Item[],
  links: Link[],
  initialConfig?: Partial<ClusteringConfig>,
): UseClusteringResult {
  const [config, setConfig] = useState<ClusteringConfig>({
    ...DEFAULT_CONFIG,
    ...initialConfig,
  });

  const [clustering, setClustering] = useState<ClusteringResult | null>(null);
  const [expansionState, setExpansionState] = useState<ExpansionState>({
    activeClusters: new Set(),
    expandedClusters: new Set(),
    visibleItems: new Set(),
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Perform clustering
  const performClustering = useCallback(() => {
    if (items.length === 0) {
      setClustering(null);
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      let result: ClusteringResult;

      switch (config.algorithm) {
        case 'louvain': {
          result = louvainClustering(items, links, config.resolution ?? 1);
          break;
        }
        case 'labelProp': {
          result = labelPropagationClustering(items, links, 100);
          break;
        }
        case 'adaptive':
        default: {
          result = adaptiveClustering(items, links, config.targetClusters);
          break;
        }
      }

      setClustering(result);

      // Initialize active clusters at highest level
      const highestLevel = result['maxLevel'];
      const topLevelClusters = result['hierarchy'].get(highestLevel) ?? [];
      setExpansionState({
        activeClusters: new Set(topLevelClusters.map((c) => c.id)),
        expandedClusters: new Set(),
        visibleItems: new Set(),
      });
    } catch (error) {
      setError(error instanceof Error ? error : new Error(String(error)));
      setClustering(null);
    } finally {
      setIsProcessing(false);
    }
  }, [items, links, config]);

  // Perform initial clustering
  useEffect(() => {
    performClustering();
  }, [performClustering]);

  // Toggle cluster expansion
  const toggleCluster = useCallback(
    (clusterId: string) => {
      setExpansionState((prev) => {
        const expanded = new Set(prev.expandedClusters);
        const visible = new Set(prev.visibleItems);
        const active = new Set(prev.activeClusters);

        if (expanded.has(clusterId)) {
          // Collapse: remove from expanded, hide items, show cluster
          expanded.delete(clusterId);

          if (clustering) {
            const cluster = clustering.clusters.get(clusterId);
            if (cluster) {
              for (const itemId of cluster.itemIds) {
                visible.delete(itemId);
              }
            }
          }

          active.add(clusterId);
        } else {
          // Expand: add to expanded, show items, hide cluster
          expanded.add(clusterId);
          active.delete(clusterId);

          if (clustering) {
            const cluster = clustering.clusters.get(clusterId);
            if (cluster) {
              for (const itemId of cluster.itemIds) {
                visible.add(itemId);
              }
            }
          }
        }

        return {
          activeClusters: active,
          expandedClusters: expanded,
          visibleItems: visible,
        };
      });
    },
    [clustering],
  );

  // Expand cluster
  const expandClusterById = useCallback(
    (clusterId: string) => {
      setExpansionState((prev) => {
        if (prev.expandedClusters.has(clusterId)) {
          return prev;
        }

        const expanded = new Set(prev.expandedClusters);
        const visible = new Set(prev.visibleItems);
        const active = new Set(prev.activeClusters);

        expanded.add(clusterId);
        active.delete(clusterId);

        if (clustering) {
          const cluster = clustering.clusters.get(clusterId);
          if (cluster) {
            for (const itemId of cluster.itemIds) {
              visible.add(itemId);
            }
          }
        }

        return {
          activeClusters: active,
          expandedClusters: expanded,
          visibleItems: visible,
        };
      });
    },
    [clustering],
  );

  // Collapse cluster
  const collapseCluster = useCallback(
    (clusterId: string) => {
      setExpansionState((prev) => {
        if (!prev.expandedClusters.has(clusterId)) {
          return prev;
        }

        const expanded = new Set(prev.expandedClusters);
        const visible = new Set(prev.visibleItems);
        const active = new Set(prev.activeClusters);

        expanded.delete(clusterId);
        active.add(clusterId);

        if (clustering) {
          const cluster = clustering.clusters.get(clusterId);
          if (cluster) {
            for (const itemId of cluster.itemIds) {
              visible.delete(itemId);
            }
          }
        }

        return {
          activeClusters: active,
          expandedClusters: expanded,
          visibleItems: visible,
        };
      });
    },
    [clustering],
  );

  // Expand all clusters
  const expandAll = useCallback(() => {
    if (!clustering) {
      return;
    }

    const expanded = new Set<string>();
    const visible = new Set<string>();
    const active = new Set<string>();

    for (const cluster of clustering.clusters.values()) {
      expanded.add(cluster.id);
      for (const itemId of cluster.itemIds) {
        visible.add(itemId);
      }
    }

    setExpansionState({
      activeClusters: active,
      expandedClusters: expanded,
      visibleItems: visible,
    });
  }, [clustering]);

  // Collapse all clusters
  const collapseAll = useCallback(() => {
    if (!clustering) {
      return;
    }

    const active = new Set<string>();
    const highestLevel = clustering.maxLevel;
    const topLevelClusters = clustering.hierarchy.get(highestLevel) ?? [];

    for (const cluster of topLevelClusters) {
      active.add(cluster.id);
    }

    setExpansionState({
      activeClusters: active,
      expandedClusters: new Set(),
      visibleItems: new Set(),
    });
  }, [clustering]);

  // Drill down to specific cluster
  const drillDownToCluster = useCallback(
    (clusterId: string) => {
      if (!clustering) {
        return;
      }

      const cluster = clustering.clusters.get(clusterId);
      if (!cluster) {
        return;
      }

      // Expand this cluster and collapse all others at same level
      const expanded = new Set([clusterId]);
      const visible = new Set(cluster.itemIds);
      const active = new Set<string>();

      setExpansionState({
        activeClusters: active,
        expandedClusters: expanded,
        visibleItems: visible,
      });
    },
    [clustering],
  );

  // Update configuration
  const updateConfig = useCallback((newConfig: Partial<ClusteringConfig>) => {
    setConfig((prev) => ({ ...prev, ...newConfig }));
  }, []);

  // Recluster with current config
  const recluster = useCallback(() => {
    performClustering();
  }, [performClustering]);

  // Get visible clusters
  const visibleClusters = useMemo(() => {
    if (!clustering) {
      return [];
    }

    return [...expansionState.activeClusters]
      .map((id) => clustering.clusters.get(id))
      .filter((c): c is ClusterNode => c !== undefined);
  }, [clustering, expansionState.activeClusters]);

  // Get visible items
  const visibleItems = useMemo(
    () => items.filter((item) => expansionState.visibleItems.has(item.id)),
    [items, expansionState.visibleItems],
  );

  // Calculate quality metrics
  const quality = useMemo(() => {
    if (!clustering) {
      return null;
    }
    return calculateClusteringQuality(clustering, links);
  }, [clustering, links]);

  // Calculate metrics
  const compressionRatio = clustering?.compressionRatio ?? 1;
  const clusterCount = clustering?.totalClusters ?? 0;

  return {
    clusterCount,
    clustering,
    collapseAll,
    collapseCluster,
    compressionRatio,
    drillDownToCluster,
    error,
    expandAll,
    expandClusterById,
    expandedClusters: expansionState.expandedClusters,
    isProcessing,
    quality,
    recluster,
    toggleCluster,
    updateConfig,
    visibleClusters,
    visibleItems,
  };
}

/**
 * Hook for cluster edge bundling
 */
export function useClusterEdges(clustering: ClusteringResult | null, links: Link[], level = 0) {
  return useMemo(() => {
    if (!clustering) {
      return [];
    }
    return extractClusterEdges(clustering, links, level);
  }, [clustering, links, level]);
}

/**
 * Hook for cluster expansion with items
 */
export function useExpandedClusterItems(
  clusterId: string | null,
  clustering: ClusteringResult | null,
  items: Item[],
) {
  return useMemo(() => {
    if (!clusterId || !clustering) {
      return [];
    }
    return expandCluster(clusterId, clustering, items);
  }, [clusterId, clustering, items]);
}
