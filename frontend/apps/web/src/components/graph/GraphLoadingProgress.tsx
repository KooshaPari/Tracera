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

import _React, { useEffect, useState } from 'react';
import type { ProgressInfo, StreamMetadata } from '../../lib/graph/IncrementalGraphBuilder';
import { Progress } from '../ui/progress';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Loader2, XCircle, CheckCircle2, Database, Network } from 'lucide-react';

export interface GraphLoadingProgressProps {
  progress?: ProgressInfo;
  metadata?: StreamMetadata;
  isLoading: boolean;
  onCancel?: () => void;
  className?: string;
}

export function GraphLoadingProgress({
  progress,
  metadata,
  isLoading,
  onCancel,
  className = '',
}: GraphLoadingProgressProps) {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [startTime] = useState(Date.now());

  // Update elapsed time
  useEffect(() => {
    if (!isLoading) {
      setElapsedTime(0);
      return;
    }

    const interval = setInterval(() => {
      setElapsedTime(Date.now() - startTime);
    }, 100);

    return () => clearInterval(interval);
  }, [isLoading, startTime]);

  if (!isLoading && !progress) {
    return null;
  }

  const percentage = progress?.percentage || 0;
  const stage = progress?.stage || 'nodes';
  const estimatedTime = metadata?.estimatedTime || 0;
  const remainingTime = Math.max(0, estimatedTime - elapsedTime);

  const stageInfo = getStageInfo(stage);

  return (
    <Card className={`${className} border-primary/20`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm font-medium">
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
              Loading Graph
            </>
          ) : (
            <>
              <CheckCircle2 className="h-4 w-4 text-green-500" />
              Loaded
            </>
          )}
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Progress Bar */}
        <div className="space-y-1">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              {stageInfo.icon}
              {stageInfo.label}
            </span>
            <span className="font-mono">{Math.round(percentage)}%</span>
          </div>
          <Progress value={percentage} className="h-2" />
        </div>

        {/* Stats */}
        {progress && (
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Database className="h-3.5 w-3.5" />
              <span>
                {progress.current.toLocaleString()} / {progress.total.toLocaleString()}
              </span>
            </div>

            {estimatedTime > 0 && (
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Network className="h-3.5 w-3.5" />
                <span>{formatTime(remainingTime)} remaining</span>
              </div>
            )}
          </div>
        )}

        {/* Metadata */}
        {metadata && (
          <div className="pt-2 border-t text-xs text-muted-foreground space-y-1">
            <div className="flex justify-between">
              <span>Total Nodes:</span>
              <span className="font-mono">{metadata.totalNodes.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span>Total Edges:</span>
              <span className="font-mono">{metadata.totalEdges.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span>Chunk Size:</span>
              <span className="font-mono">{metadata.chunkSize}</span>
            </div>
          </div>
        )}

        {/* Cancel Button */}
        {isLoading && onCancel && (
          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={onCancel}
          >
            <XCircle className="h-3.5 w-3.5 mr-1.5" />
            Cancel Loading
          </Button>
        )}

        {/* Loading Animation */}
        {isLoading && (
          <div className="flex items-center justify-center gap-1 pt-2">
            <div className="h-1 w-1 rounded-full bg-primary animate-pulse [animation-delay:0ms]" />
            <div className="h-1 w-1 rounded-full bg-primary animate-pulse [animation-delay:150ms]" />
            <div className="h-1 w-1 rounded-full bg-primary animate-pulse [animation-delay:300ms]" />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Compact loading progress indicator
 */
export function GraphLoadingProgressCompact({
  progress,
  isLoading,
  onCancel,
  className = '',
}: GraphLoadingProgressProps) {
  if (!isLoading && !progress) {
    return null;
  }

  const percentage = progress?.percentage || 0;
  const stage = progress?.stage || 'nodes';
  const stageInfo = getStageInfo(stage);

  return (
    <div
      className={`${className} flex items-center gap-3 rounded-lg border bg-card p-3 text-sm shadow-sm`}
    >
      {isLoading ? (
        <Loader2 className="h-4 w-4 animate-spin text-primary flex-shrink-0" />
      ) : (
        <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0" />
      )}

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs text-muted-foreground flex items-center gap-1">
            {stageInfo.icon}
            {stageInfo.label}
          </span>
          <span className="text-xs font-mono text-muted-foreground ml-auto">
            {Math.round(percentage)}%
          </span>
        </div>
        <Progress value={percentage} className="h-1.5" />
      </div>

      {isLoading && onCancel && (
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0 flex-shrink-0"
          onClick={onCancel}
        >
          <XCircle className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}

/**
 * Inline progress bar (minimal)
 */
export function GraphLoadingProgressInline({
  progress,
  isLoading,
}: Pick<GraphLoadingProgressProps, 'progress' | 'isLoading'>) {
  if (!isLoading && !progress) {
    return null;
  }

  const percentage = progress?.percentage || 0;

  return (
    <div className="space-y-1">
      <Progress value={percentage} className="h-1" />
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>Loading graph...</span>
        <span className="font-mono">{Math.round(percentage)}%</span>
      </div>
    </div>
  );
}

/**
 * Get stage display information
 */
function getStageInfo(stage: string) {
  switch (stage) {
    case 'nodes':
      return {
        label: 'Loading Nodes',
        icon: <Database className="h-3 w-3" />,
      };
    case 'edges':
      return {
        label: 'Loading Edges',
        icon: <Network className="h-3 w-3" />,
      };
    case 'complete':
      return {
        label: 'Complete',
        icon: <CheckCircle2 className="h-3 w-3" />,
      };
    default:
      return {
        label: 'Loading',
        icon: <Loader2 className="h-3 w-3 animate-spin" />,
      };
  }
}

/**
 * Format milliseconds to human-readable time
 */
function formatTime(ms: number): string {
  if (ms < 1000) {
    return '<1s';
  }

  const seconds = Math.ceil(ms / 1000);

  if (seconds < 60) {
    return `${seconds}s`;
  }

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  if (remainingSeconds === 0) {
    return `${minutes}m`;
  }

  return `${minutes}m ${remainingSeconds}s`;
}

/**
 * useLoadingEstimate - Hook for estimating loading time
 */
export function useLoadingEstimate(
  metadata?: StreamMetadata,
  progress?: ProgressInfo
) {
  const [estimate, setEstimate] = useState<{
    total: number;
    remaining: number;
    speed: number; // items per second
  } | null>(null);

  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (!metadata || !progress || progress.current === 0) {
      setEstimate(null);
      return;
    }

    const elapsed = Date.now() - startTime;
    const speed = progress.current / (elapsed / 1000);
    const remaining = progress.total - progress.current;
    const remainingTime = (remaining / speed) * 1000;

    setEstimate({
      total: metadata.estimatedTime,
      remaining: remainingTime,
      speed,
    });
  }, [metadata, progress, startTime]);

  return estimate;
}
