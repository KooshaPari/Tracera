import { logger } from '@/lib/logger';

import type { PerformanceMetrics } from './types';

import { BYTES_PER_MB, PERCENT_DECIMALS, PERCENT_SCALE, ZERO } from './constants';
import { formatInteraction, getFpsColor } from './formatting';
import { safeToLocaleTimeString } from './storage';

function logGraphPerformanceMetrics(metrics: PerformanceMetrics): void {
  const timeLabel = safeToLocaleTimeString(metrics.timestamp);
  logger.group(`[Graph Performance] ${timeLabel}`);

  const fpsColor = getFpsColor(metrics);
  logger.info(
    `%cFPS: ${metrics.fps.current} (avg: ${metrics.fps.average}, min: ${metrics.fps.min}, max: ${metrics.fps.max})`,
    fpsColor,
  );

  logger.info(
    `Nodes: ${metrics.nodes.rendered}/${metrics.nodes.total} (${metrics.nodes.cullingRatio.toFixed(PERCENT_DECIMALS)}% culled)`,
  );
  logger.info(
    `Edges: ${metrics.edges.rendered}/${metrics.edges.total} (${metrics.edges.cullingRatio.toFixed(PERCENT_DECIMALS)}% culled)`,
  );
  logger.info(
    `LOD: High=${metrics.lod.high} Med=${metrics.lod.medium} Low=${metrics.lod.low} Skeleton=${metrics.lod.skeleton}`,
  );
  logger.info(
    `Cache Hit Rate: ${(metrics.cache.combined.hitRatio * PERCENT_SCALE).toFixed(PERCENT_DECIMALS)}% (${metrics.cache.combined.hits}/${metrics.cache.combined.totalRequests})`,
  );

  if (metrics.timing.viewportLoadMs > ZERO) {
    logger.info(`Viewport Load: ${metrics.timing.viewportLoadMs.toFixed(PERCENT_DECIMALS)}ms`);
  }

  if (metrics.memory) {
    const heapMB = (metrics.memory.usedJSHeapSize / BYTES_PER_MB).toFixed(PERCENT_DECIMALS);
    const limitMB = (metrics.memory.jsHeapSizeLimit / BYTES_PER_MB).toFixed(PERCENT_DECIMALS);
    logger.info(
      `Memory: ${heapMB}MB / ${limitMB}MB (${metrics.memory.heapUsagePercent.toFixed(PERCENT_DECIMALS)}%)`,
    );
  }

  const interactionLine = formatInteraction(metrics);
  if (interactionLine !== undefined && interactionLine.length > ZERO) {
    logger.info(interactionLine);
  }

  logger.groupEnd();
}

export { logGraphPerformanceMetrics };
