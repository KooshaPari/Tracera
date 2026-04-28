/**
 * Streaming Progress Indicator Component
 * Displays progress for NDJSON streaming operations
 */

import type { StreamingStats } from '../lib/ndjson-parser';

import { calculateThroughput } from '../lib/ndjson-parser';

const BYTES_IN_KB = 1024;
const BYTES_IN_MB = BYTES_IN_KB * BYTES_IN_KB;
const DECIMAL_PLACES_BYTES = 2;
const DECIMAL_PLACES_MS = 0;
const DECIMAL_PLACES_SECONDS = 1;
const MS_PER_SECOND = 1000;
const MINUTES_PER_HOUR = 60;
const MS_PER_MINUTE = MINUTES_PER_HOUR * MS_PER_SECOND;
const PERCENTAGE_SCALE = 100;

export interface StreamingProgressProps {
  stats: StreamingStats | null;
  isStreaming: boolean;
  showThroughput?: boolean;
  showBytes?: boolean;
  className?: string;
}

const formatBytes = (bytes: number): string => {
  if (bytes < BYTES_IN_KB) {
    return `${bytes} B`;
  }
  if (bytes < BYTES_IN_MB) {
    return `${(bytes / BYTES_IN_KB).toFixed(DECIMAL_PLACES_BYTES)} KB`;
  }
  return `${(bytes / BYTES_IN_MB).toFixed(DECIMAL_PLACES_BYTES)} MB`;
};

const formatDuration = (ms: number): string => {
  if (ms < MS_PER_SECOND) {
    return `${ms.toFixed(DECIMAL_PLACES_MS)}ms`;
  }
  if (ms < MS_PER_MINUTE) {
    return `${(ms / MS_PER_SECOND).toFixed(DECIMAL_PLACES_SECONDS)}s`;
  }
  return `${(ms / MS_PER_MINUTE).toFixed(DECIMAL_PLACES_SECONDS)}m`;
};

const hasErrors = (stats: StreamingStats | null): boolean =>
  stats !== null && stats.errors.length > 0;

const StatItem = ({ label, value }: { label: string; value: string | number }) => (
  <div className='flex flex-col'>
    <span className='text-muted-foreground'>{label}</span>
    <span className='font-mono font-semibold'>{value}</span>
  </div>
);

const ErrorStat = ({ count }: { count: number }) => (
  <div className='flex flex-col'>
    <span className='text-destructive'>Errors</span>
    <span className='text-destructive font-mono font-semibold'>{count}</span>
  </div>
);

const ErrorDetails = ({ errors }: { errors: string[] }) => (
  <div className='text-destructive mt-2 text-sm'>
    <details>
      <summary className='cursor-pointer'>
        {errors.length} error{errors.length > 1 ? 's' : ''} occurred
      </summary>
      <ul className='mt-1 list-inside list-disc pl-4'>
        {errors.map((error, idx) => (
          <li key={`${error}-${idx}`}>{error}</li>
        ))}
      </ul>
    </details>
  </div>
);

const StatsRow = ({
  stats,
  showBytes,
  showThroughput,
  throughput,
}: {
  stats: StreamingStats | null;
  showBytes: boolean;
  showThroughput: boolean;
  throughput: ReturnType<typeof calculateThroughput> | null;
}) => (
  <div className='flex gap-6 text-sm'>
    <StatItem label='Items' value={stats?.itemsReceived.toLocaleString() ?? 0} />

    {showBytes && stats && <StatItem label='Data' value={formatBytes(stats.bytesReceived)} />}

    {showThroughput && throughput && (
      <StatItem label='Speed' value={`${throughput.itemsPerSecond.toFixed(0)} items/s`} />
    )}

    {stats && (
      <StatItem
        label='Duration'
        value={formatDuration((stats.endTime ?? Date.now()) - stats.startTime)}
      />
    )}

    {hasErrors(stats) && <ErrorStat count={stats!.errors.length} />}
  </div>
);

const Spinner = () => (
  <div className='border-primary h-4 w-4 animate-spin rounded-full border-2 border-t-transparent' />
);

const ProgressBar = () => (
  <div className='bg-muted mt-2 h-1 w-full overflow-hidden rounded-full'>
    <div className='bg-primary h-full animate-pulse' />
  </div>
);

const StatusText = ({ isStreaming }: { isStreaming: boolean }) => (
  <div className='text-muted-foreground ml-auto text-sm'>
    {isStreaming ? 'Streaming...' : 'Complete'}
  </div>
);

export const StreamingProgress = ({
  stats,
  isStreaming,
  showThroughput = true,
  showBytes = false,
  className = '',
}: StreamingProgressProps) => {
  if (!stats && !isStreaming) {
    return null;
  }

  const throughput = stats ? calculateThroughput(stats) : null;
  const errorStats = hasErrors(stats) ? stats : null;

  return (
    <div className={`streaming-progress ${className}`}>
      <div className='flex items-center gap-4'>
        {isStreaming && <Spinner />}
        <StatsRow
          stats={stats}
          showBytes={showBytes}
          showThroughput={showThroughput}
          throughput={throughput}
        />
        <StatusText isStreaming={isStreaming} />
      </div>

      {isStreaming && <ProgressBar />}

      {errorStats && <ErrorDetails errors={errorStats.errors} />}
    </div>
  );
};

export interface CompactStreamingProgressProps {
  stats: StreamingStats | null;
  isStreaming: boolean;
}

export const CompactStreamingProgress = ({ stats, isStreaming }: CompactStreamingProgressProps) => {
  if (!stats && !isStreaming) {
    return null;
  }

  return (
    <div className='text-muted-foreground inline-flex items-center gap-2 text-sm'>
      {isStreaming && (
        <div className='border-primary h-3 w-3 animate-spin rounded-full border-2 border-t-transparent' />
      )}
      <span className='font-mono'>{stats?.itemsReceived.toLocaleString() ?? 0} items</span>
      {isStreaming && <span>streaming...</span>}
    </div>
  );
};

export interface StreamingProgressBarProps {
  current: number;
  total?: number;
  isStreaming: boolean;
  className?: string;
}

export const StreamingProgressBar = ({
  current,
  total,
  isStreaming,
  className = '',
}: StreamingProgressBarProps) => {
  const percentage = total ? (current / total) * PERCENTAGE_SCALE : 0;
  const showPercentage = total && total > 0;

  return (
    <div className={`streaming-progress-bar ${className}`}>
      <div className='mb-1 flex justify-between text-sm'>
        <span className='text-muted-foreground'>
          {current.toLocaleString()}
          {total ? ` / ${total.toLocaleString()}` : ''} items
        </span>
        {showPercentage && (
          <span className='font-mono font-semibold'>
            {percentage.toFixed(DECIMAL_PLACES_SECONDS)}%
          </span>
        )}
      </div>
      <div className='bg-muted h-2 w-full overflow-hidden rounded-full'>
        {showPercentage ? (
          <div
            className='bg-primary h-full transition-all duration-300'
            style={{ width: `${percentage}%` }}
          />
        ) : (
          isStreaming && <div className='bg-primary h-full animate-pulse' />
        )}
      </div>
    </div>
  );
};
