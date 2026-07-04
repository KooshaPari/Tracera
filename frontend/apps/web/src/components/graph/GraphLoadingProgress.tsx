/**
 * GraphLoadingProgress - UI component for streaming graph loading progress
 *
 * Features:
 * - Real-time progress visualization
 * - Stage-based progress tracking
 * - Estimated completion time
 * - Smooth animations
 * - Cancellable loading
 */

import type { ReactNode } from 'react';

import { CheckCircle2, Database, Loader2, Network, XCircle } from 'lucide-react';
import { useEffect, useState } from 'react';

import type { ProgressInfo, StreamMetadata } from '../../lib/graph/IncrementalGraphBuilder';

import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';

const ELAPSED_TICK_MS = 100;
const MS_IN_SECOND = 1000;
const SECONDS_IN_MINUTE = 60;

export interface GraphLoadingProgressProps {
  progress?: ProgressInfo | undefined;
  metadata?: StreamMetadata | undefined;
  isLoading: boolean;
  onCancel?: (() => void) | undefined;
  className?: string | undefined;
}

interface StageInfo {
  icon: ReactNode;
  label: string;
}

const getStageInfo = (stage: string): StageInfo => {
  switch (stage) {
    case 'nodes': {
      return { icon: <Database className='h-3 w-3' />, label: 'Loading Nodes' };
    }
    case 'edges': {
      return { icon: <Network className='h-3 w-3' />, label: 'Loading Edges' };
    }
    case 'complete': {
      return { icon: <CheckCircle2 className='h-3 w-3' />, label: 'Complete' };
    }
    default: {
      return {
        icon: <Loader2 className='h-3 w-3 animate-spin' />,
        label: 'Loading',
      };
    }
  }
};

const formatTime = (ms: number): string => {
  if (ms < MS_IN_SECOND) {
    return '<1s';
  }

  const seconds = Math.ceil(ms / MS_IN_SECOND);
  if (seconds < SECONDS_IN_MINUTE) {
    return `${seconds}s`;
  }

  const minutes = Math.floor(seconds / SECONDS_IN_MINUTE);
  const remainingSeconds = seconds % SECONDS_IN_MINUTE;
  if (remainingSeconds === 0) {
    return `${minutes}m`;
  }

  return `${minutes}m ${remainingSeconds}s`;
};

interface ProgressHeaderProps {
  isLoading: boolean;
}

const ProgressHeader = ({ isLoading }: ProgressHeaderProps) => (
  <CardHeader className='pb-3'>
    <CardTitle className='flex items-center gap-2 text-sm font-medium'>
      {isLoading ? (
        <>
          <Loader2 className='text-primary h-4 w-4 animate-spin' />
          Loading Graph
        </>
      ) : (
        <>
          <CheckCircle2 className='h-4 w-4 text-green-500' />
          Loaded
        </>
      )}
    </CardTitle>
  </CardHeader>
);

interface ProgressStageProps {
  percentage: number;
  stageInfo: StageInfo;
}

const ProgressStage = ({ percentage, stageInfo }: ProgressStageProps) => (
  <div className='space-y-1'>
    <div className='text-muted-foreground flex justify-between text-xs'>
      <span className='flex items-center gap-1'>
        {stageInfo.icon}
        {stageInfo.label}
      </span>
      <span className='font-mono'>{Math.round(percentage)}%</span>
    </div>
    <Progress value={percentage} className='h-2' />
  </div>
);

interface ProgressStatsProps {
  progress?: ProgressInfo | undefined;
  estimatedTime: number;
  remainingTime: number;
}

const ProgressStats = ({ progress, estimatedTime, remainingTime }: ProgressStatsProps) => {
  if (!progress) {
    return null;
  }

  return (
    <div className='grid grid-cols-2 gap-2 text-xs'>
      <div className='text-muted-foreground flex items-center gap-1.5'>
        <Database className='h-3.5 w-3.5' />
        <span>
          {progress.current.toLocaleString()} / {progress.total.toLocaleString()}
        </span>
      </div>

      {estimatedTime > 0 && (
        <div className='text-muted-foreground flex items-center gap-1.5'>
          <Network className='h-3.5 w-3.5' />
          <span>{formatTime(remainingTime)} remaining</span>
        </div>
      )}
    </div>
  );
};

interface MetadataSectionProps {
  metadata?: StreamMetadata | undefined;
}

const MetadataSection = ({ metadata }: MetadataSectionProps) => {
  if (!metadata) {
    return null;
  }

  return (
    <div className='text-muted-foreground space-y-1 border-t pt-2 text-xs'>
      <div className='flex justify-between'>
        <span>Total Nodes:</span>
        <span className='font-mono'>{metadata.totalNodes.toLocaleString()}</span>
      </div>
      <div className='flex justify-between'>
        <span>Total Edges:</span>
        <span className='font-mono'>{metadata.totalEdges.toLocaleString()}</span>
      </div>
      <div className='flex justify-between'>
        <span>Chunk Size:</span>
        <span className='font-mono'>{metadata.chunkSize}</span>
      </div>
    </div>
  );
};

interface CancelButtonProps {
  isLoading: boolean;
  onCancel?: (() => void) | undefined;
}

const CancelButton = ({ isLoading, onCancel }: CancelButtonProps) => {
  if (!isLoading || !onCancel) {
    return null;
  }

  return (
    <Button variant='outline' size='sm' className='w-full' onClick={onCancel}>
      <XCircle className='mr-1.5 h-3.5 w-3.5' />
      Cancel Loading
    </Button>
  );
};

const LoadingDots = ({ isLoading }: { isLoading: boolean }) => {
  if (!isLoading) {
    return null;
  }

  return (
    <div className='flex items-center justify-center gap-1 pt-2'>
      <div className='bg-primary h-1 w-1 animate-pulse rounded-full [animation-delay:0ms]' />
      <div className='bg-primary h-1 w-1 animate-pulse rounded-full [animation-delay:150ms]' />
      <div className='bg-primary h-1 w-1 animate-pulse rounded-full [animation-delay:300ms]' />
    </div>
  );
};

const GraphLoadingProgress = ({
  progress,
  metadata,
  isLoading,
  onCancel,
  className = '',
}: GraphLoadingProgressProps) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (!isLoading) {
      setElapsedTime(0);
      return;
    }

    const interval = setInterval(() => {
      setElapsedTime(Date.now() - startTime);
    }, ELAPSED_TICK_MS);

    return () => {
      clearInterval(interval);
    };
  }, [isLoading, startTime]);

  if (!isLoading && !progress) {
    return null;
  }

  const percentage = progress?.percentage ?? 0;
  const stage = progress?.stage ?? 'nodes';
  const estimatedTime = metadata?.estimatedTime ?? 0;
  const remainingTime = Math.max(0, estimatedTime - elapsedTime);
  const stageInfo = getStageInfo(stage);

  return (
    <Card className={`${className} border-primary/20`}>
      <ProgressHeader isLoading={isLoading} />
      <CardContent className='space-y-3'>
        <ProgressStage percentage={percentage} stageInfo={stageInfo} />
        <ProgressStats
          progress={progress}
          estimatedTime={estimatedTime}
          remainingTime={remainingTime}
        />
        <MetadataSection metadata={metadata} />
        <CancelButton isLoading={isLoading} onCancel={onCancel} />
        <LoadingDots isLoading={isLoading} />
      </CardContent>
    </Card>
  );
};

type CompactProps = GraphLoadingProgressProps;

const GraphLoadingProgressCompact = ({
  progress,
  isLoading,
  onCancel,
  className = '',
}: CompactProps) => {
  if (!isLoading && !progress) {
    return null;
  }

  const percentage = progress?.percentage ?? 0;
  const stage = progress?.stage ?? 'nodes';
  const stageInfo = getStageInfo(stage);

  return (
    <div
      className={`${className} bg-card flex items-center gap-3 rounded-lg border p-3 text-sm shadow-sm`}
    >
      {isLoading ? (
        <Loader2 className='text-primary h-4 w-4 flex-shrink-0 animate-spin' />
      ) : (
        <CheckCircle2 className='h-4 w-4 flex-shrink-0 text-green-500' />
      )}

      <div className='min-w-0 flex-1'>
        <div className='mb-1 flex items-center gap-2'>
          <span className='text-muted-foreground flex items-center gap-1 text-xs'>
            {stageInfo.icon}
            {stageInfo.label}
          </span>
          <span className='text-muted-foreground ml-auto font-mono text-xs'>
            {Math.round(percentage)}%
          </span>
        </div>
        <Progress value={percentage} className='h-1.5' />
      </div>

      {isLoading && onCancel && (
        <Button variant='ghost' size='sm' className='h-8 w-8 flex-shrink-0 p-0' onClick={onCancel}>
          <XCircle className='h-4 w-4' />
        </Button>
      )}
    </div>
  );
};

type InlineProps = Pick<GraphLoadingProgressProps, 'progress' | 'isLoading'>;

const GraphLoadingProgressInline = ({ progress, isLoading }: InlineProps) => {
  if (!isLoading && !progress) {
    return null;
  }

  const percentage = progress?.percentage ?? 0;

  return (
    <div className='space-y-1'>
      <Progress value={percentage} className='h-1' />
      <div className='text-muted-foreground flex justify-between text-xs'>
        <span className='inline-flex items-center gap-2'>
          <Loader2 className='h-3 w-3 animate-spin' />
          Loading graph...
        </span>
        <span className='font-mono'>{Math.round(percentage)}%</span>
      </div>
    </div>
  );
};

type LoadingEstimate = {
  total: number;
  remaining: number;
  speed: number;
} | null;

const useLoadingEstimate = (
  metadata?: StreamMetadata,
  progress?: ProgressInfo,
): LoadingEstimate => {
  const [estimate, setEstimate] = useState<LoadingEstimate>(null);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (!metadata || !progress || progress.current === 0) {
      setEstimate(null);
      return;
    }

    const elapsed = Date.now() - startTime;
    const speed = progress.current / (elapsed / MS_IN_SECOND);
    const remaining = progress.total - progress.current;
    const remainingTime = (remaining / speed) * MS_IN_SECOND;

    setEstimate({
      remaining: remainingTime,
      speed,
      total: metadata.estimatedTime,
    });
  }, [metadata, progress, startTime]);

  return estimate;
};

export {
  GraphLoadingProgress,
  GraphLoadingProgressCompact,
  GraphLoadingProgressInline,
  useLoadingEstimate,
};
