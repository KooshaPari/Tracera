import { MarkerType } from '@xyflow/react';

import type { CacheStatistics } from '@/lib/cache';
import type { LinkType } from '@tracertm/types';

import { LINK_STYLES } from '../types';

export const EDGE_LABEL_BG_STYLE = { fill: 'rgba(26, 26, 46, 0.9)' };

export interface EdgeStyleCacheEntry {
  style: object;
  labelStyle: object;
  label: string;
  markerEnd?: object | undefined;
}

const edgeStyleCache = new Map<LinkType, EdgeStyleCacheEntry>();

interface StoreCacheStatsBlock {
  totalEntries: number;
  hitRatio: number;
}

export const toPerformanceCacheStats = (
  statsBlock: StoreCacheStatsBlock,
  backendType: string,
): CacheStatistics => {
  const normalizedHitRatio = Number.isFinite(statsBlock.hitRatio)
    ? Math.min(Math.max(statsBlock.hitRatio, 0), 1)
    : 0;
  const totalEntries = Number.isFinite(statsBlock.totalEntries)
    ? Math.max(statsBlock.totalEntries, 0)
    : 0;
  const totalHits = Math.round(totalEntries * normalizedHitRatio);

  return {
    backendType,
    hitRatio: normalizedHitRatio,
    maxEntries: totalEntries,
    maxMemory: 0,
    memoryUsagePercent: 0,
    totalEntries,
    totalHits,
    totalMemory: 0,
    totalMisses: Math.max(totalEntries - totalHits, 0),
  };
};

export function getCachedEdgeStyle(linkType: LinkType): EdgeStyleCacheEntry {
  if (!edgeStyleCache.has(linkType)) {
    const linkStyle = LINK_STYLES[linkType] ?? {
      arrow: false,
      color: '#64748b',
      dashed: true,
    };
    edgeStyleCache.set(linkType, {
      style: {
        stroke: linkStyle.color,
        strokeWidth: 2,
        ...(linkStyle.dashed && { strokeDasharray: '5,5' }),
      },
      labelStyle: { fill: linkStyle.color, fontSize: 10 },
      label: linkType.replaceAll('_', ' '),
      ...(linkStyle.arrow && {
        markerEnd: { color: linkStyle.color, type: MarkerType.ArrowClosed },
      }),
    });
  }
  const cachedStyle = edgeStyleCache.get(linkType);
  if (cachedStyle === undefined) {
    throw new Error(`Missing cached edge style for link type: ${linkType}`);
  }
  return cachedStyle;
}
