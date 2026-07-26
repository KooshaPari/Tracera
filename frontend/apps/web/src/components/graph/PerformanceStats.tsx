import type { ReactNode } from 'react';

import { Activity, Cpu, Database, Zap } from 'lucide-react';
import { memo } from 'react';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

const FPS_GOOD_THRESHOLD = 55;
const FPS_WARN_THRESHOLD = 30;
const FPS_MAX = 60;
const PERCENT_MULTIPLIER = 100;

interface PerformanceStatsProps {
  fps: number;
  nodeCount: number;
  edgeCount: number;
  visibleNodeCount: number;
  visibleEdgeCount: number;
  memoryUsage?: number | undefined; // MB | undefined;
  renderTime?: number | undefined; // Ms | undefined;
  variant?: 'compact' | 'detailed' | undefined;
}

interface StatRowProps {
  label: ReactNode;
  value: ReactNode;
  valueClassName?: string | undefined;
}

const StatRow = ({ label, value, valueClassName }: StatRowProps) => (
  <div className='flex justify-between text-xs'>
    <span className='text-muted-foreground flex items-center gap-1'>{label}</span>
    <span className={valueClassName ?? 'font-medium'}>{value}</span>
  </div>
);

const getFpsColorClass = (fps: number): string => {
  if (fps >= FPS_GOOD_THRESHOLD) {
    return 'text-green-600';
  }

  if (fps >= FPS_WARN_THRESHOLD) {
    return 'text-yellow-600';
  }

  return 'text-red-600';
};

interface ProgressSectionProps {
  label: ReactNode;
  value: ReactNode;
  progressValue: number;
  valueClassName?: string | undefined;
}

const ProgressSection = ({ label, value, progressValue, valueClassName }: ProgressSectionProps) => (
  <div className='space-y-1'>
    <StatRow label={label} value={value} valueClassName={valueClassName} />
    <Progress value={progressValue} className='h-1' />
  </div>
);

interface CompactStatsProps {
  cullPercentage: number;
  fps: number;
  fpsClassName: string;
  nodeCount: number;
  visibleNodeCount: number;
}

const CompactStats = ({
  cullPercentage,
  fps,
  fpsClassName,
  nodeCount,
  visibleNodeCount,
}: CompactStatsProps) => (
  <div className='flex items-center gap-2 text-xs'>
    <Badge variant='outline' className={fpsClassName}>
      {Math.round(fps)} FPS
    </Badge>
    <span className='text-muted-foreground'>
      {visibleNodeCount}/{nodeCount} nodes
    </span>
    {cullPercentage > 0 && <span className='text-green-600'>{cullPercentage}% culled</span>}
  </div>
);

interface DetailedStatsProps {
  cullPercentage: number;
  edgeCount: number;
  fps: number;
  fpsClassName: string;
  memoryUsage?: number | undefined;
  nodeCount: number;
  renderTime?: number | undefined;
  visibleEdgeCount: number;
  visibleNodeCount: number;
}

const DetailedStats = ({
  cullPercentage,
  edgeCount,
  fps,
  fpsClassName,
  memoryUsage,
  nodeCount,
  renderTime,
  visibleEdgeCount,
  visibleNodeCount,
}: DetailedStatsProps) => (
  <Card className='w-64'>
    <CardHeader className='pb-3'>
      <CardTitle className='flex items-center gap-2 text-sm'>
        <Activity className='h-4 w-4' />
        Performance
      </CardTitle>
    </CardHeader>
    <CardContent className='space-y-3'>
      <ProgressSection
        label='Frame Rate'
        value={`${Math.round(fps)} FPS`}
        valueClassName={`font-medium ${fpsClassName}`}
        progressValue={(fps / FPS_MAX) * PERCENT_MULTIPLIER}
      />
      <ProgressSection
        label={
          <>
            <Database className='h-3 w-3' />
            Nodes
          </>
        }
        value={`${visibleNodeCount}/${nodeCount}`}
        progressValue={(visibleNodeCount / nodeCount) * PERCENT_MULTIPLIER}
      />
      <ProgressSection
        label='Edges'
        value={`${visibleEdgeCount}/${edgeCount}`}
        progressValue={(visibleEdgeCount / edgeCount) * PERCENT_MULTIPLIER}
      />
      {cullPercentage > 0 && (
        <StatRow
          label={
            <>
              <Zap className='h-3 w-3' />
              Culling
            </>
          }
          value={`${cullPercentage}%`}
          valueClassName='font-medium text-green-600'
        />
      )}
      {memoryUsage !== undefined && (
        <StatRow
          label={
            <>
              <Cpu className='h-3 w-3' />
              Memory
            </>
          }
          value={`${memoryUsage.toFixed(1)} MB`}
        />
      )}
      {renderTime !== undefined && <StatRow label='Render' value={`${renderTime.toFixed(1)} ms`} />}
    </CardContent>
  </Card>
);

const getCullPercentage = (nodeCount: number, visibleNodeCount: number): number => {
  if (nodeCount <= 0) {
    return 0;
  }

  return Math.round((1 - visibleNodeCount / nodeCount) * PERCENT_MULTIPLIER);
};

const PerformanceStats = memo(
  ({
    fps,
    nodeCount,
    edgeCount,
    visibleNodeCount,
    visibleEdgeCount,
    memoryUsage,
    renderTime,
    variant = 'compact',
  }: PerformanceStatsProps) => {
    const cullPercentage = getCullPercentage(nodeCount, visibleNodeCount);
    const fpsClassName = getFpsColorClass(fps);

    if (variant === 'compact') {
      return (
        <CompactStats
          cullPercentage={cullPercentage}
          fps={fps}
          fpsClassName={fpsClassName}
          nodeCount={nodeCount}
          visibleNodeCount={visibleNodeCount}
        />
      );
    }

    return (
      <DetailedStats
        cullPercentage={cullPercentage}
        edgeCount={edgeCount}
        fps={fps}
        fpsClassName={fpsClassName}
        memoryUsage={memoryUsage}
        nodeCount={nodeCount}
        renderTime={renderTime}
        visibleEdgeCount={visibleEdgeCount}
        visibleNodeCount={visibleNodeCount}
      />
    );
  },
);

export { PerformanceStats };
export type { PerformanceStatsProps };
