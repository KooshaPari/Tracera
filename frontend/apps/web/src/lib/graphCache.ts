/**
 * Simple graph cache stub for examples
 */

import { useGraphCacheOperations } from '@/stores/graph-cache-operations';

export interface GraphCacheNode {
  id: string;
  data: Record<string, unknown>;
}

export interface GraphCacheEntry {
  nodes: GraphCacheNode[];
  timestamp: number;
}

export const graphCache = new Map<string, GraphCacheEntry>();
export const groupingCache = new Map<string, unknown>();

export function useGraphCache() {
  return useGraphCacheOperations();
}

export function getCacheKey(viewport: { x: number; y: number; zoom: number }): string {
  return `${viewport.x}:${viewport.y}:${viewport.zoom}`;
}

export function setCache(key: string, entry: GraphCacheEntry | GraphCacheNode[]): void {
  const cacheEntry: GraphCacheEntry = Array.isArray(entry)
    ? {
        nodes: entry,
        timestamp: Date.now(),
      }
    : entry;

  graphCache.set(key, cacheEntry);
}

export function getCache(key: string): GraphCacheEntry | undefined {
  return graphCache.get(key);
}

export function clearCache(): void {
  graphCache.clear();
}
