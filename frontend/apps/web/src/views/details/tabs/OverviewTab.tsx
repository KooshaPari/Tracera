/**
 * OverviewTab - Generic overview information for items
 *
 * Displays:
 * - Title and description
 * - Creation and update dates
 * - Owner and assignee
 * - Version and perspective
 * - Status and priority
 */

import { CalendarClock, CircleDot, Hash, User } from 'lucide-react';

import type { TypedItem } from '@tracertm/types';

import { cn } from '@/lib/utils';
import { Badge, Card } from '@tracertm/ui';

const statusColors: Record<string, string> = {
  blocked: 'bg-rose-500/15 text-rose-700 border-rose-500/30',
  cancelled: 'bg-gray-500/15 text-gray-700 border-gray-500/30',
  done: 'bg-emerald-500/15 text-emerald-700 border-emerald-500/30',
  in_progress: 'bg-sky-500/15 text-sky-700 border-sky-500/30',
  todo: 'bg-slate-500/10 text-slate-600 border-slate-500/20',
};

const priorityColors: Record<string, string> = {
  critical: 'bg-rose-500 text-white',
  high: 'bg-orange-500 text-white',
  low: 'bg-emerald-500 text-white',
  medium: 'bg-indigo-500 text-white',
};

export interface OverviewTabProps {
  /** The item to display */
  item: TypedItem;

  /** Optional additional content */
  children?: React.ReactNode;

  /** Optional CSS classes */
  className?: string;
}

/**
 * OverviewTab displays basic item information in a consistent layout.
 */
export function OverviewTab({ item, children, className }: OverviewTabProps) {
  const createdAtLabel = item.createdAt
    ? new Date(item.createdAt).toLocaleDateString(undefined, {
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        month: 'long',
        year: 'numeric',
      })
    : 'Unknown';

  const updatedAtLabel = item.updatedAt
    ? new Date(item.updatedAt).toLocaleDateString(undefined, {
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        month: 'long',
        year: 'numeric',
      })
    : 'Unknown';

  const detailsHeading =
    item.view && typeof item.view === 'string'
      ? `${item.view.charAt(0).toUpperCase()}${item.view.slice(1).toLowerCase()} Details`
      : 'Item Details';

  return (
    <div className={cn('space-y-6', className)}>
      {/* Primary Information */}
      <div className='space-y-4'>
        <h2 className='text-lg font-black tracking-tight'>{detailsHeading}</h2>

        <div className='grid grid-cols-1 gap-4 md:grid-cols-2'>
          {/* Status & Priority */}
          <Card className='bg-muted/40 space-y-3 border-0 p-4'>
            <p
              className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'
              id='status-priority-label'
            >
              Status & Priority
            </p>
            <div className='flex items-center gap-2' aria-labelledby='status-priority-label'>
              <Badge
                className={cn(
                  'text-[10px] font-black uppercase tracking-widest',
                  statusColors[item.status] ?? statusColors['todo'],
                )}
              >
                {item.status.replace('_', ' ')}
              </Badge>
              <Badge
                className={cn(
                  'text-[10px] font-black uppercase tracking-widest',
                  priorityColors[item.priority] ?? priorityColors['medium'],
                )}
              >
                {item.priority}
              </Badge>
            </div>
          </Card>

          {/* Owner */}
          <Card className='bg-muted/40 space-y-3 border-0 p-4'>
            <p
              className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'
              id='owner-label'
            >
              Owner
            </p>
            <div className='flex items-center gap-2' aria-labelledby='owner-label'>
              <div className='bg-primary/10 flex h-7 w-7 items-center justify-center rounded-full'>
                <User className='text-primary h-3 w-3' aria-hidden='true' />
              </div>
              <span className='text-sm font-bold'>{item.owner ?? 'Unassigned'}</span>
            </div>
          </Card>

          {/* Version & Perspective */}
          <Card className='bg-muted/40 space-y-3 border-0 p-4'>
            <p
              className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'
              id='version-label'
            >
              Version & Perspective
            </p>
            <div
              className='flex items-center justify-between text-sm font-bold'
              aria-labelledby='version-label'
            >
              <span>
                <span className='sr-only'>Version </span>v{item.version}
              </span>
              <span className='text-muted-foreground'>{item.perspective ?? 'default'}</span>
            </div>
          </Card>

          {/* Identifiers */}
          <Card className='bg-muted/40 space-y-3 border-0 p-4'>
            <p
              className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'
              id='identifiers-label'
            >
              Identifiers
            </p>
            <div className='space-y-2' aria-labelledby='identifiers-label'>
              <div className='flex items-center gap-2 text-xs'>
                <Hash className='text-muted-foreground h-3 w-3' aria-hidden='true' />
                <span className='text-muted-foreground font-mono'>ID:</span>
                <span className='truncate font-bold'>{item.id}</span>
              </div>
              {item.canonicalId && (
                <div className='flex items-center gap-2 text-xs'>
                  <CircleDot className='text-muted-foreground h-3 w-3' aria-hidden='true' />
                  <span className='text-muted-foreground font-mono'>Canonical:</span>
                  <span className='truncate font-bold'>{item.canonicalId}</span>
                </div>
              )}
              {item.parentId && (
                <div className='flex items-center gap-2 text-xs'>
                  <CircleDot className='text-muted-foreground h-3 w-3' aria-hidden='true' />
                  <span className='text-muted-foreground font-mono'>Parent:</span>
                  <span className='truncate font-bold'>{item.parentId.slice(0, 8)}...</span>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>

      {/* Timestamps */}
      <div className='space-y-4'>
        <h2 className='text-lg font-black tracking-tight'>Timeline</h2>

        <Card className='bg-muted/40 border-0 p-4'>
          <div className='grid grid-cols-1 gap-4 text-sm md:grid-cols-2'>
            <div className='flex items-center gap-3'>
              <div className='bg-primary/10 flex h-10 w-10 items-center justify-center rounded-lg'>
                <CalendarClock className='text-primary h-4 w-4' aria-hidden='true' />
              </div>
              <div>
                <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                  Created
                </p>
                <p className='font-bold'>{createdAtLabel}</p>
              </div>
            </div>

            <div className='flex items-center gap-3'>
              <div className='bg-primary/10 flex h-10 w-10 items-center justify-center rounded-lg'>
                <CircleDot className='text-primary h-4 w-4' aria-hidden='true' />
              </div>
              <div>
                <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                  Last Updated
                </p>
                <p className='font-bold'>{updatedAtLabel}</p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Description */}
      {item.description && (
        <div className='space-y-4'>
          <h2 className='text-lg font-black tracking-tight'>Description</h2>
          <Card className='bg-muted/40 border-0 p-4'>
            <p className='text-sm leading-relaxed whitespace-pre-wrap'>{item.description}</p>
          </Card>
        </div>
      )}

      {/* Additional content */}
      {children}
    </div>
  );
}
