/**
 * Enterprise Loading Skeletons
 *
 * Replaces inline loading states with polished, animated skeletons
 * Professional feel that matches enterprise applications like Jira/Linear
 */

import type { CSSProperties, JSX } from 'react';

import { cn } from '@/lib/utils';

const CONTENT_ANIM_DELAY = 0.3;
const COLUMN_STAGGER_DELAY = 0.1;
const TABLE_ROW_COUNT_DEFAULT = 10;
const TABLE_COL_COUNT_DEFAULT = 6;
const KANBAN_COLUMN_COUNT_DEFAULT = 4;
const GRAPH_NODE_COUNT = 8;
const DASHBOARD_METRIC_COUNT = 4;
const DASHBOARD_PROJECT_COUNT = 5;
const DASHBOARD_ACTIVITY_COUNT = 8;
const KANBAN_MIN_CARDS = 3;
const KANBAN_CARD_VARIANCE = 5;
const GRAPH_OFFSET_LARGE = 140;
const GRAPH_OFFSET_MEDIUM = 120;
const GRAPH_OFFSET_SMALL = 100;
const GRAPH_OFFSET_XSMALL = 90;
const GRAPH_OFFSET_MINOR = 70;
const GRAPH_OFFSET_TINY = 40;
const GRAPH_OFFSET_MICRO = 20;
const SHIMMER_STYLE_HTML = `
  .shimmer-effect {
    background: linear-gradient(
      90deg,
      hsl(var(--muted)) 0%,
      hsl(var(--muted) / 0.8) 50%,
      hsl(var(--muted)) 100%
    );
    background-size: 200% 100%;
    animation: shimmer 2s infinite;
  }

  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }
`;
const SHIMMER_STYLE_CONTENT = { __html: SHIMMER_STYLE_HTML };
const GRAPH_NODE_POSITIONS: readonly (readonly [number, number])[] = [
  [-GRAPH_OFFSET_MEDIUM, -GRAPH_OFFSET_SMALL],
  [GRAPH_OFFSET_SMALL, -GRAPH_OFFSET_MEDIUM],
  [GRAPH_OFFSET_LARGE, GRAPH_OFFSET_TINY],
  [-GRAPH_OFFSET_XSMALL, GRAPH_OFFSET_MEDIUM],
  [0, 0],
  [GRAPH_OFFSET_MINOR, GRAPH_OFFSET_SMALL],
  [-GRAPH_OFFSET_LARGE, GRAPH_OFFSET_MICRO],
  [GRAPH_OFFSET_MICRO, -GRAPH_OFFSET_LARGE],
];
const GRAPH_NODE_STYLES: readonly CSSProperties[] = GRAPH_NODE_POSITIONS.map(([left, top]) => ({
  left: `${left}px`,
  top: `${top}px`,
}));
const delayStyleCache = new Map<string, CSSProperties>();

interface SkeletonProps {
  className?: string;
  animate?: boolean;
}

interface TableSkeletonProps {
  rows?: number;
  cols?: number;
}

interface KanbanSkeletonProps {
  columns?: number;
}

interface LoadingOverlayProps {
  message?: string;
}

function createKeys(prefix: string, count: number): string[] {
  return Array.from({ length: count }, (_unused, index) => `${prefix}-${index}`);
}

function createGridStyle(cols: number): CSSProperties {
  return { gridTemplateColumns: `repeat(${cols}, 1fr)` };
}

function hasMessage(message: string | undefined): message is string {
  return typeof message === 'string' && message.length > 0;
}

function getKanbanCardCount(columnIndex: number): number {
  return KANBAN_MIN_CARDS + (columnIndex % KANBAN_CARD_VARIANCE);
}

function getAnimationDelayStyle(delaySeconds: number): CSSProperties {
  const key = delaySeconds.toString();
  const cachedStyle = delayStyleCache.get(key);

  if (cachedStyle) {
    return cachedStyle;
  }

  const style = { animationDelay: `${delaySeconds}s` };
  delayStyleCache.set(key, style);

  return style;
}

export const Skeleton = ({ className, animate = true }: SkeletonProps): JSX.Element => (
  <>
    <div
      className={cn('animate-pulse rounded-md bg-muted', animate && 'shimmer-effect', className)}
    />
    <style dangerouslySetInnerHTML={SHIMMER_STYLE_CONTENT} />
  </>
);

// Card skeleton for projects/items
export function CardSkeleton(): JSX.Element {
  return (
    <div className='bg-card space-y-4 rounded-lg border p-6'>
      <div className='flex items-center space-x-4'>
        <Skeleton className='h-12 w-12 rounded-full' />
        <div className='flex-1 space-y-2'>
          <Skeleton className='h-4 w-3/4' />
          <Skeleton className='h-3 w-1/2' />
        </div>
        <Skeleton className='h-6 w-16 rounded-full' />
      </div>
      <Skeleton className='h-4 w-full' />
      <Skeleton className='h-4 w-2/3' />
    </div>
  );
}

// Table skeleton for data grids
export function TableSkeleton({
  rows = TABLE_ROW_COUNT_DEFAULT,
  cols = TABLE_COL_COUNT_DEFAULT,
}: TableSkeletonProps): JSX.Element {
  const headerKeys = createKeys('table-header-col', cols);
  const rowKeys = createKeys('table-row', rows);
  const rowColumnKeys = createKeys('table-row-col', cols);
  const gridStyle = createGridStyle(cols);

  return (
    <div className='w-full'>
      <div className='mb-4 border-b pb-4'>
        <div className='grid gap-4' style={gridStyle}>
          {headerKeys.map((columnKey) => (
            <Skeleton key={columnKey} className='h-4' animate={false} />
          ))}
        </div>
      </div>

      <div className='space-y-2'>
        {rowKeys.map((rowKey) => (
          <div key={rowKey} className='border-b py-2'>
            <div className='grid gap-4' style={gridStyle}>
              {rowColumnKeys.map((columnKey) => (
                <Skeleton
                  key={`${rowKey}-${columnKey}`}
                  className='h-4'
                  animate={columnKey === 'table-row-col-0'}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Kanban board skeleton
export function KanbanSkeleton({
  columns = KANBAN_COLUMN_COUNT_DEFAULT,
}: KanbanSkeletonProps): JSX.Element {
  const columnKeys = createKeys('kanban-column', columns);

  return (
    <div className='flex gap-4 pb-4'>
      {columnKeys.map((columnKey, columnIndex) => {
        const cardKeys = createKeys(`${columnKey}-card`, getKanbanCardCount(columnIndex));

        return (
          <div
            key={columnKey}
            className='min-w-0 flex-1'
            style={getAnimationDelayStyle(columnIndex * COLUMN_STAGGER_DELAY)}
          >
            <div className='bg-muted/30 rounded-lg border p-4'>
              <Skeleton className='mb-4 h-4 w-3/4' animate={false} />
              <div className='space-y-2'>
                {cardKeys.map((cardKey) => (
                  <CardSkeleton key={cardKey} />
                ))}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Graph visualization skeleton
export function GraphSkeleton(): JSX.Element {
  const nodeKeys = createKeys('graph-node', GRAPH_NODE_COUNT);

  return (
    <div className='flex h-full min-h-[400px] items-center justify-center'>
      <div className='relative'>
        {nodeKeys.map((nodeKey, nodeIndex) => (
          <div key={nodeKey} className='absolute' style={GRAPH_NODE_STYLES[nodeIndex]}>
            <Skeleton className='h-8 w-8 rounded-full' animate={false} />
          </div>
        ))}
        <div className='flex min-h-[400px] min-w-[400px] items-center justify-center'>
          <Skeleton className='h-6 w-32' animate={false} />
        </div>
      </div>
    </div>
  );
}

// Dashboard skeleton with multiple sections
export function DashboardSkeleton(): JSX.Element {
  const metricKeys = createKeys('dashboard-metric', DASHBOARD_METRIC_COUNT);
  const projectCardKeys = createKeys('dashboard-project', DASHBOARD_PROJECT_COUNT);
  const activityKeys = createKeys('dashboard-activity', DASHBOARD_ACTIVITY_COUNT);

  return (
    <div className='space-y-6'>
      <div className='grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4'>
        {metricKeys.map((metricKey, metricIndex) => (
          <div key={metricKey} style={getAnimationDelayStyle(metricIndex * COLUMN_STAGGER_DELAY)}>
            <div className='bg-card rounded-lg border p-6'>
              <Skeleton className='mb-2 h-4 w-20' animate={false} />
              <Skeleton className='h-8 w-16' />
            </div>
          </div>
        ))}
      </div>

      <div className='grid grid-cols-1 gap-6 lg:grid-cols-3'>
        <div className='lg:col-span-2' style={getAnimationDelayStyle(CONTENT_ANIM_DELAY)}>
          <div className='bg-card rounded-lg border p-6'>
            <Skeleton className='mb-4 h-6 w-32' animate={false} />
            <div className='space-y-2'>
              {projectCardKeys.map((projectCardKey) => (
                <CardSkeleton key={projectCardKey} />
              ))}
            </div>
          </div>
        </div>

        <div>
          <div className='bg-card rounded-lg border p-6'>
            <Skeleton className='mb-4 h-6 w-24' animate={false} />
            <div className='space-y-3'>
              {activityKeys.map((activityKey) => (
                <div key={activityKey} className='flex items-center space-x-3'>
                  <Skeleton className='h-8 w-8 rounded-full' />
                  <div className='flex-1 space-y-1'>
                    <Skeleton className='h-3 w-full' />
                    <Skeleton className='h-2 w-3/4' />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Professional loading spinner for overlays
export function LoadingOverlay({ message }: LoadingOverlayProps): JSX.Element {
  return (
    <div className='bg-background/80 fixed inset-0 z-50 flex items-center justify-center backdrop-blur-sm'>
      <div className='bg-card flex flex-col items-center space-y-4 rounded-lg border p-6 shadow-lg'>
        <div className='relative'>
          <div className='border-primary h-12 w-12 animate-spin rounded-full border-4 border-t-transparent' />
          <div className='border-primary/20 absolute inset-0 h-12 w-12 animate-spin rounded-full border-4 border-t-transparent' />
        </div>
        {hasMessage(message) ? (
          <p className='text-muted-foreground max-w-sm text-center'>{message}</p>
        ) : null}
      </div>
    </div>
  );
}
