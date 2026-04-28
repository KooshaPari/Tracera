import { memo } from 'react';

import { useFPSMonitor } from '@/hooks/useFPSMonitor';
import { useMemoryMonitor } from '@/hooks/useMemoryMonitor';

import { PerformanceStats } from './PerformanceStats';

interface PerformanceOverlayProps {
  nodeCount: number;
  edgeCount: number;
  visibleNodeCount: number;
  visibleEdgeCount: number;
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | undefined;
  variant?: 'compact' | 'detailed' | undefined;
}

export const PerformanceOverlay = memo(function PerformanceOverlay({
  nodeCount,
  edgeCount,
  visibleNodeCount,
  visibleEdgeCount,
  position = 'top-right',
  variant = 'compact',
}: PerformanceOverlayProps) {
  const fpsStats = useFPSMonitor(true);
  const memoryStats = useMemoryMonitor(true);

  const positionClasses = {
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
  };

  return (
    <div className={`absolute ${positionClasses[position]} z-10`}>
      <PerformanceStats
        fps={fpsStats.current}
        nodeCount={nodeCount}
        edgeCount={edgeCount}
        visibleNodeCount={visibleNodeCount}
        visibleEdgeCount={visibleEdgeCount}
        memoryUsage={memoryStats?.usedJSHeapSize}
        variant={variant}
      />
    </div>
  );
});
