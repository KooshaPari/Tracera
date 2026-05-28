import type { useGraphPerformanceMonitor } from '@/hooks/useGraphPerformanceMonitor';

import { FPS_GOOD_THRESHOLD, FPS_WARN_THRESHOLD } from './flowGraphConstants';

type PerformanceMonitor = ReturnType<typeof useGraphPerformanceMonitor>;

interface FlowGraphDevPerformancePanelProps {
  performanceMonitor: PerformanceMonitor;
  getFpsClassName: (fps: number) => string;
}

export function FlowGraphDevPerformancePanel({
  performanceMonitor,
  getFpsClassName,
}: FlowGraphDevPerformancePanelProps) {
  const metrics = performanceMonitor.currentMetrics;
  if (!metrics) {
    return null;
  }

  return (
    <div className='bg-card/90 space-y-0.5 rounded-md border p-1.5 font-mono text-[9px] backdrop-blur-sm sm:rounded-lg sm:p-2 sm:text-[10px]'>
      <div className='flex items-center gap-1'>
        <span className='text-muted-foreground'>FPS:</span>
        <span className={getFpsClassName(metrics.fps.current)}>{metrics.fps.current}</span>
        <span className='text-muted-foreground text-[8px]'>(avg: {metrics.fps.average})</span>
      </div>
      <div className='flex items-center gap-1'>
        <span className='text-muted-foreground'>Nodes:</span>
        <span className='text-primary'>
          {metrics.nodes.rendered}/{metrics.nodes.total}
        </span>
        <span className='text-muted-foreground text-[8px]'>
          ({metrics.nodes.cullingRatio.toFixed(0)}% culled)
        </span>
      </div>
      <div className='flex items-center gap-1'>
        <span className='text-muted-foreground'>Edges:</span>
        <span className='text-primary'>
          {metrics.edges.rendered}/{metrics.edges.total}
        </span>
        <span className='text-muted-foreground text-[8px]'>
          ({metrics.edges.cullingRatio.toFixed(0)}% culled)
        </span>
      </div>
      <div className='flex items-center gap-1'>
        <span className='text-muted-foreground'>Cache:</span>
        <span className='text-primary'>
          {(metrics.cache.combined.hitRatio * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
}
