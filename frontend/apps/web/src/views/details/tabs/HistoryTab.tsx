/**
 * HistoryTab - Displays audit trail and change history
 *
 * Shows:
 * - Creation timestamp and user
 * - Last update timestamp and user
 * - Version history
 * - Timeline of changes
 */

import { CalendarClock, CircleDot, GitBranch, Timer } from 'lucide-react';
import { useMemo } from 'react';

import type { TypedItem } from '@tracertm/types';

import { cn } from '@/lib/utils';
import { Badge, Card } from '@tracertm/ui';

export interface HistoryTabProps {
  /** The item to display history for */
  item: TypedItem;

  /** Optional CSS classes */
  className?: string;
}

interface TimelineEvent {
  label: string;
  timestamp: string;
  detail?: string;
  icon?: React.ComponentType<{ className?: string }>;
  color?: string;
}

/**
 * HistoryTab displays the audit trail and change history for an item.
 */
export function HistoryTab({ item, className }: HistoryTabProps) {
  const createdAtLabel = item.createdAt
    ? new Date(item.createdAt).toLocaleString(undefined, {
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        month: 'long',
        year: 'numeric',
      })
    : 'Unknown';

  const updatedAtLabel = item.updatedAt
    ? new Date(item.updatedAt).toLocaleString(undefined, {
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        month: 'long',
        year: 'numeric',
      })
    : 'Unknown';

  const timelineEvents = useMemo<TimelineEvent[]>(() => {
    const events: TimelineEvent[] = [];

    if (item.createdAt) {
      events.push({
        color: 'text-emerald-500',
        detail: `Status: ${item.status}`,
        icon: CalendarClock,
        label: 'Item Created',
        timestamp: item.createdAt,
      });
    }

    if (item.updatedAt && item.updatedAt !== item.createdAt) {
      events.push({
        color: 'text-sky-500',
        detail: `Version ${item.version}`,
        icon: CircleDot,
        label: 'Last Updated',
        timestamp: item.updatedAt,
      });
    }

    if (item.version > 1 && item.updatedAt) {
      events.push({
        color: 'text-violet-500',
        detail: `Now at v${item.version}`,
        icon: GitBranch,
        label: 'Version Bumped',
        timestamp: item.updatedAt,
      });
    }

    // Sort events by timestamp (newest first)
    return [...events].toSorted((a, b) => (a.timestamp > b.timestamp ? -1 : 1));
  }, [item]);

  const timeSinceUpdate = useMemo(() => {
    if (!item.updatedAt) {
      return 'Unknown';
    }

    const now = new Date();
    const updated = new Date(item.updatedAt);
    const diffMs = now.getTime() - updated.getTime();
    const diffMins = Math.floor(diffMs / 60_000);
    const diffHours = Math.floor(diffMs / 3_600_000);
    const diffDays = Math.floor(diffMs / 86_400_000);

    if (diffMins < 60) {
      return `${diffMins} minutes ago`;
    }
    if (diffHours < 24) {
      return `${diffHours} hours ago`;
    }
    return `${diffDays} days ago`;
  }, [item.updatedAt]);

  return (
    <div className={cn('space-y-6', className)}>
      {/* Summary Cards */}
      <div className='grid grid-cols-1 gap-4 md:grid-cols-3'>
        <Card className='bg-muted/40 space-y-3 border-0 p-4'>
          <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
            Created
          </p>
          <div className='flex items-center gap-3'>
            <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10'>
              <CalendarClock className='h-4 w-4 text-emerald-500' aria-hidden='true' />
            </div>
            <div>
              <p className='text-sm font-bold'>{createdAtLabel}</p>
              {item.owner && <p className='text-muted-foreground text-xs'>by {item.owner}</p>}
            </div>
          </div>
        </Card>

        <Card className='bg-muted/40 space-y-3 border-0 p-4'>
          <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
            Last Updated
          </p>
          <div className='flex items-center gap-3'>
            <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-sky-500/10'>
              <CircleDot className='h-4 w-4 text-sky-500' aria-hidden='true' />
            </div>
            <div>
              <p className='text-sm font-bold'>{updatedAtLabel}</p>
              <p className='text-muted-foreground text-xs'>{timeSinceUpdate}</p>
            </div>
          </div>
        </Card>

        <Card className='bg-muted/40 space-y-3 border-0 p-4'>
          <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
            Version
          </p>
          <div className='flex items-center gap-3'>
            <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-violet-500/10'>
              <GitBranch className='h-4 w-4 text-violet-500' aria-hidden='true' />
            </div>
            <div>
              <p className='text-2xl font-black'>v{item.version}</p>
              <p className='text-muted-foreground text-xs'>
                {item.version === 1 ? 'Initial version' : 'Updated'}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Timeline */}
      <div className='space-y-4'>
        <h2 className='text-lg font-black tracking-tight'>Activity Timeline</h2>

        <Card className='bg-muted/40 border-0 p-6'>
          <div className='space-y-6' role='list' aria-label='Activity timeline'>
            {timelineEvents.length > 0 ? (
              timelineEvents.map((event, index) => {
                const Icon = event.icon ?? CircleDot;
                return (
                  <div
                    key={`${event.label}-${event.timestamp}`}
                    className='relative flex items-start gap-4'
                    role='listitem'
                  >
                    {/* Connector line */}
                    {index < timelineEvents.length - 1 && (
                      <div
                        className='bg-border absolute top-10 bottom-0 left-5 w-px'
                        aria-hidden='true'
                      />
                    )}

                    {/* Icon */}
                    <div
                      className={cn(
                        'h-10 w-10 rounded-full bg-muted flex items-center justify-center flex-shrink-0 relative z-10',
                        event.color,
                      )}
                    >
                      <Icon className='h-5 w-5' aria-hidden='true' />
                    </div>

                    {/* Content */}
                    <div className='flex-1 pt-1.5'>
                      <div className='flex flex-wrap items-start justify-between gap-4'>
                        <div>
                          <p className='text-sm font-bold'>{event.label}</p>
                          {event.detail && (
                            <p className='text-muted-foreground text-xs'>{event.detail}</p>
                          )}
                        </div>
                        <Badge variant='secondary' className='text-xs whitespace-nowrap'>
                          {new Date(event.timestamp).toLocaleDateString(undefined, {
                            day: 'numeric',
                            month: 'short',
                            year: 'numeric',
                          })}
                        </Badge>
                      </div>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className='text-muted-foreground py-8 text-center'>
                <Timer className='mx-auto mb-2 h-8 w-8 opacity-20' aria-hidden='true' />
                <p className='text-sm font-medium'>No activity recorded</p>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Additional Metadata */}
      <div className='space-y-4'>
        <h2 className='text-lg font-black tracking-tight'>Metadata</h2>

        <div className='grid grid-cols-1 gap-4 md:grid-cols-2'>
          <Card className='bg-muted/40 border-0 p-4'>
            <div className='space-y-2 text-sm'>
              <div className='flex items-center justify-between'>
                <span className='text-muted-foreground'>Canonical ID</span>
                <span className='ml-2 truncate font-bold'>{item.canonicalId ?? '—'}</span>
              </div>
              <div className='flex items-center justify-between'>
                <span className='text-muted-foreground'>Parent ID</span>
                <span className='ml-2 truncate font-bold'>
                  {item.parentId ? `${item.parentId.slice(0, 12)}...` : 'Root'}
                </span>
              </div>
              <div className='flex items-center justify-between'>
                <span className='text-muted-foreground'>Perspective</span>
                <span className='font-bold'>{item.perspective ?? 'Default'}</span>
              </div>
            </div>
          </Card>

          <Card className='bg-muted/40 border-0 p-4'>
            <div className='space-y-2 text-sm'>
              <div className='flex items-center justify-between'>
                <span className='text-muted-foreground'>Project ID</span>
                <span className='ml-2 truncate font-bold'>{item.projectId.slice(0, 12)}...</span>
              </div>
              <div className='flex items-center justify-between'>
                <span className='text-muted-foreground'>Item ID</span>
                <span className='ml-2 truncate font-bold'>{item.id.slice(0, 12)}...</span>
              </div>
              <div className='flex items-center justify-between'>
                <span className='text-muted-foreground'>View</span>
                <span className='font-bold capitalize'>
                  {item.view?.toLowerCase() || 'General'}
                </span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
