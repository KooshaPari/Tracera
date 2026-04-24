/**
 * Graph Clustering Utilities - Louvain Community Detection
 *
 * Provides community detection using the Louvain algorithm for graph visualization.
 * Optimized for large graphs (10k+ nodes) with caching and performance monitoring.
 */

import Graph from 'graphology';
import louvain from 'graphology-communities-louvain';

import type { Item, Link } from '@tracertm/types';

// Community color palette - visually distinct colors for up to 12 communities
export const COMMUNITY_COLORS = [
  '#3B82F6', // blue
  '#10B981', // green
  '#F59E0B', // amber
  '#EF4444', // red
  '#8B5CF6', // violet
  '#EC4899', // pink
  '#14B8A6', // teal
  '#F97316', // orange
  '#6366F1', // indigo
  '#84CC16', // lime
  '#06B6D4', // cyan
  '#A855F7', // purple
] as const;

// Additional colors for graphs with >12 communities
export const EXTENDED_COMMUNITY_COLORS = [
  ...COMMUNITY_COLORS,
  '#64748B', // slate
  '#DC2626', // red-600
  '#059669', // emerald-600
  '#7C3AED', // violet-600
  '#DB2777', // pink-600
  '#0891B2', // cyan-600
  '#EA580C', // orange-600
  '#4F46E5', // indigo-600
];

export interface CommunityResult {
  /** Map of node ID to community ID */
  communities: Map<string, string>;

  /** Map of community ID to color */
  colors: Map<string, string>;

  /** Community statistics */
  stats: CommunityStats;

  /** Performance metrics */
  performance: {
    clusteringTimeMs: number;
    nodeCount: number;
    edgeCount: number;
  };
}

export interface CommunityStats {
  /** Total number of communities detected */
  communityCount: number;

  /** Map of community ID to node count */
  communitySizes: Map<string, number>;

  /** Largest community size */
  maxCommunitySize: number;

  /** Smallest community size */
  minCommunitySize: number;

  /** Average community size */
  avgCommunitySize: number;

  /** Modularity score (quality metric) */
  modularity?: number | undefined;
}

export interface ClusteringOptions {
  /** Resolution parameter for Louvain (default: 1.0) */
  resolution?: number | undefined;

  /** Whether to use cached results if available */
  useCache?: boolean | undefined;

  /** Minimum community size (filter out smaller communities) */
  minCommunitySize?: number | undefined;

  /** Maximum number of iterations */
  maxIterations?: number | undefined;
}

// Cache for clustering results
const clusteringCache = new Map<string, CommunityResult>();
const MAX_CACHE_SIZE = 10;

/**
 * Generate cache key from items and links
 */
function generateCacheKey(items: Item[], links: Link[], options: ClusteringOptions): string {
  const itemIds = items
    .map((i) => i['id'])
    .sort()
    .join(',');
  const linkIds = links
    .map((l) => `${l.sourceId}-${l.targetId}`)
    .sort()
    .join(',');
  const opts = `${options.resolution || 1}-${options.minCommunitySize || 0}`;
  return `${itemIds}-${linkIds}-${opts}`;
}

/**
 * Build graphology Graph from items and links
 */
function buildGraph(items: Item[], links: Link[]): Graph {
  const graph = new Graph({ type: 'undirected' });

  // Add nodes
  for (const item of items) {
    graph.addNode(item['id'], {
      label: item.title,
      type: item.type,
    });
  }

  // Add edges (convert directed to undirected for community detection)
  const addedEdges = new Set<string>();

  for (const link of links) {
    // Skip if nodes don't exist
    if (!graph.hasNode(link.sourceId) || !graph.hasNode(link.targetId)) {
      continue;
    }

    // Create normalized edge key (alphabetically sorted for undirected)
    const [nodeA, nodeB] = [link.sourceId, link.targetId].sort();
    const edgeKey = `${nodeA}-${nodeB}`;

    // Skip if edge already added
    if (addedEdges.has(edgeKey)) {
      continue;
    }

    try {
      graph.addEdge(link.sourceId, link.targetId, {
        id: edgeKey,
        type: link.type,
      });
      addedEdges.add(edgeKey);
    } catch (error) {
      // Edge may already exist (shouldn't happen with our Set check, but handle it)
      // Silently skip duplicate edges
    }
  }

  return graph;
}

/**
 * Calculate community statistics
 */
function calculateStats(communities: Map<string, string>, modularity?: number): CommunityStats {
  const communitySizes = new Map<string, number>();

  // Count nodes per community
  for (const communityId of communities.values()) {
    communitySizes.set(communityId, (communitySizes.get(communityId) || 0) + 1);
  }

  const sizes = Array.from(communitySizes.values());
  const communityCount = communitySizes.size;
  const maxCommunitySize = Math.max(...sizes, 0);
  const minCommunitySize = Math.min(...sizes, 0);
  const avgCommunitySize = sizes.length > 0 ? sizes.reduce((a, b) => a + b, 0) / sizes.length : 0;

  return {
    communityCount,
    communitySizes,
    maxCommunitySize,
    minCommunitySize,
    avgCommunitySize,
    modularity,
  };
}

/**
 * Assign colors to communities
 */
function assignColors(communityIds: Set<string>): Map<string, string> {
  const colors = new Map<string, string>();
  const colorPalette =
    communityIds.size <= COMMUNITY_COLORS.length ? COMMUNITY_COLORS : EXTENDED_COMMUNITY_COLORS;

  const sortedIds = Array.from(communityIds).sort();

  sortedIds.forEach((id, index) => {
    // Cycle through colors if more communities than colors
    const color = colorPalette[index % colorPalette.length]!;
    colors.set(id, color);
  });

  return colors;
}

/**
 * Run Louvain community detection on graph
 *
 * @param items - Array of graph nodes
 * @param links - Array of graph edges
 * @param options - Clustering options
 * @returns Community detection results with performance metrics
 */
export async function detectCommunities(
  items: Item[],
  links: Link[],
  options: ClusteringOptions = {},
): Promise<CommunityResult> {
  const startTime = performance.now();

  // Check cache
  if (options.useCache !== false) {
    const cacheKey = generateCacheKey(items, links, options);
    const cached = clusteringCache.get(cacheKey);
    if (cached) {
      return cached;
    }
  }

  // Build graph
  const graph = buildGraph(items, links);

  const nodeCount = graph.order; // number of nodes
  const edgeCount = graph.size; // number of edges

  // Handle edge cases
  if (nodeCount === 0) {
    return {
      communities: new Map(),
      colors: new Map(),
      stats: {
        communityCount: 0,
        communitySizes: new Map(),
        maxCommunitySize: 0,
        minCommunitySize: 0,
        avgCommunitySize: 0,
      },
      performance: {
        clusteringTimeMs: performance.now() - startTime,
        nodeCount: 0,
        edgeCount: 0,
      },
    };
  }

  if (nodeCount === 1) {
    const singleNode = graph.nodes()[0]!;
    const communities = new Map([[singleNode, '0']]);
    const colors = new Map([['0', COMMUNITY_COLORS[0]!]]);

    return {
      communities,
      colors,
      stats: {
        communityCount: 1,
        communitySizes: new Map([['0', 1]]),
        maxCommunitySize: 1,
        minCommunitySize: 1,
        avgCommunitySize: 1,
      },
      performance: {
        clusteringTimeMs: performance.now() - startTime,
        nodeCount: 1,
        edgeCount: 0,
      },
    };
  }

  // Run Louvain algorithm
  const louvainOptions: any = {};
  if (options.resolution !== undefined) {
    louvainOptions.resolution = options.resolution;
  }

  // louvain mutates the graph by adding community attributes
  const detailed = louvain.detailed(graph, louvainOptions);

  // Extract community assignments
  const communities = new Map<string, string>();
  graph.forEachNode((node, attributes) => {
    const communityId = String(attributes['community'] || '0');
    communities.set(node, communityId);
  });

  // Filter by minimum community size if specified
  if (options.minCommunitySize && options.minCommunitySize > 1) {
    const communitySizes = new Map<string, number>();
    for (const communityId of communities.values()) {
      communitySizes.set(communityId, (communitySizes.get(communityId) || 0) + 1);
    }

    // Reassign small communities to '0' (unclustered)
    for (const [nodeId, communityId] of communities.entries()) {
      const size = communitySizes.get(communityId) || 0;
      if (size < options.minCommunitySize) {
        communities.set(nodeId, '0');
      }
    }
  }

  // Get unique community IDs
  const communityIds = new Set(communities.values());

  // Assign colors
  const colors = assignColors(communityIds);

  // Calculate statistics
  const stats = calculateStats(communities, detailed.modularity);

  const clusteringTimeMs = performance.now() - startTime;

  const result: CommunityResult = {
    communities,
    colors,
    stats,
    performance: {
      clusteringTimeMs,
      nodeCount,
      edgeCount,
    },
  };

  // Cache result
  if (options.useCache !== false) {
    const cacheKey = generateCacheKey(items, links, options);
    clusteringCache.set(cacheKey, result);

    // Limit cache size
    if (clusteringCache.size > MAX_CACHE_SIZE) {
      const firstKey = clusteringCache.keys().next().value;
      if (firstKey) {
        clusteringCache.delete(firstKey);
      }
    }
  }

  return result;
}

/**
 * Clear clustering cache
 */
export function clearClusteringCache(): void {
  clusteringCache.clear();
}

/**
 * Get color for a community ID
 */
export function getCommunityColor(communityId: string, colors: Map<string, string>): string {
  return colors.get(communityId) || COMMUNITY_COLORS[0];
}

/**
 * Format community stats for display
 */
export function formatCommunityStats(stats: CommunityStats): string {
  return `${stats.communityCount} communities (avg: ${Math.round(stats.avgCommunitySize)} nodes)`;
}

/**
 * Export community data as JSON
 */
export function exportCommunitiesJSON(result: CommunityResult): string {
  const data = {
    communities: Array.from(result.communities.entries()).map(([nodeId, communityId]) => ({
      nodeId,
      communityId,
      color: result.colors.get(communityId),
    })),
    stats: {
      ...result.stats,
      communitySizes: Array.from(result.stats.communitySizes.entries()).map(([id, size]) => ({
        communityId: id,
        size,
        color: result.colors.get(id),
      })),
    },
    performance: result.performance,
  };

  return JSON.stringify(data, null, 2);
}

/**
 * Export community data as CSV
 */
export function exportCommunitiesCSV(result: CommunityResult): string {
  const rows = [['Node ID', 'Community ID', 'Color']];

  for (const [nodeId, communityId] of result.communities.entries()) {
    const color = result.colors.get(communityId) || '';
    rows.push([nodeId, communityId, color]);
  }

  return rows.map((row) => row.join(',')).join('\n');
}
