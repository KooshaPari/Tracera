import type { PerformanceMetrics } from './types';

import {
  BYTES_PER_MB,
  FPS_GOOD_THRESHOLD,
  FPS_WARN_THRESHOLD,
  NO_DECIMALS,
  PERCENT_DECIMALS,
  PERCENT_SCALE,
  ZERO,
} from './constants';

function getFpsColor(metrics: PerformanceMetrics): string {
  if (metrics.fps.current >= FPS_GOOD_THRESHOLD) {
    return 'color: #10b981';
  }
  if (metrics.fps.current >= FPS_WARN_THRESHOLD) {
    return 'color: #f59e0b';
  }
  return 'color: #ef4444';
}

function formatInteraction(metrics: PerformanceMetrics): string | undefined {
  const fragments: string[] = [];
  if (metrics.interaction.isPanning) {
    fragments.push(`pan: ${metrics.interaction.panDuration.toFixed(NO_DECIMALS)}ms`);
  }
  if (metrics.interaction.isZooming) {
    fragments.push(`zoom: ${metrics.interaction.zoomDuration.toFixed(NO_DECIMALS)}ms`);
  }
  if (fragments.length <= ZERO) {
    return undefined;
  }
  return `Interaction: ${metrics.interaction.lastInteractionType} (${fragments.join(' ')})`;
}

function formatSummary(metrics: PerformanceMetrics): string {
  const lines = [
    `FPS: ${metrics.fps.current} (avg: ${metrics.fps.average})`,
    `Nodes: ${metrics.nodes.rendered}/${metrics.nodes.total} rendered (${metrics.nodes.cullingRatio.toFixed(PERCENT_DECIMALS)}% culled)`,
    `Edges: ${metrics.edges.rendered}/${metrics.edges.total} rendered (${metrics.edges.cullingRatio.toFixed(PERCENT_DECIMALS)}% culled)`,
    `Cache Hit Rate: ${(metrics.cache.combined.hitRatio * PERCENT_SCALE).toFixed(PERCENT_DECIMALS)}%`,
  ];
  if (metrics.memory) {
    const heapMB = (metrics.memory.usedJSHeapSize / BYTES_PER_MB).toFixed(PERCENT_DECIMALS);
    lines.push(`Memory: ${heapMB}MB`);
  }
  return lines.join(' | ');
}

export { formatInteraction, formatSummary, getFpsColor };
