/**
 * DetailHeader - Shared header component for all item detail views
 *
 * Provides consistent navigation, title display, and action buttons
 */

import { ArrowLeft, ExternalLink, MoreVertical, Trash2 } from 'lucide-react';

import type { TypedItem } from '@tracertm/types';

import { cn } from '@/lib/utils';
import {
  Badge,
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@tracertm/ui';

import type { DetailAction } from './BaseDetailView';

const statusColors: Record<string, string> = {
  blocked: 'bg-rose-500/15 text-rose-700 border-rose-500/30',
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

export interface DetailHeaderProps {
  item: TypedItem;
  actions?: DetailAction[] | undefined;
  onBack?: (() => void) | undefined;
}

/** Human-readable view label for detail heading (e.g. FEATURE -> "Feature") */
function viewHeadingLabel(view: string | undefined): string {
  if (!view) {
    return 'Item';
  }
  return view.charAt(0).toUpperCase() + view.slice(1).toLowerCase();
}

function handleShare() {
  const _shareUrl = `${globalThis.location.origin}${globalThis.location.pathname}`;
  undefined;
}

export function DetailHeader({ item, actions = [], onBack }: DetailHeaderProps) {
  const viewLabel = viewHeadingLabel(item.view);

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      globalThis.history.back();
    }
  };

  return (
    <div className='space-y-4'>
      {/* Navigation bar */}
      <div className='flex items-center justify-between'>
        <Button
          variant='ghost'
          size='sm'
          onClick={handleBack}
          className='text-muted-foreground hover:text-foreground gap-2'
        >
          <ArrowLeft className='h-4 w-4' />
          Back
        </Button>

        <div className='flex items-center gap-2'>
          <Button variant='outline' size='sm' className='gap-2 rounded-full' onClick={handleShare}>
            <ExternalLink className='h-3.5 w-3.5' />
            Share
          </Button>

          {/* Custom action buttons */}
          {actions.map((action, index) => (
            <Button
              key={index}
              variant={action.variant ?? 'outline'}
              size='sm'
              className='gap-2 rounded-full'
              onClick={action.onClick}
              disabled={action.disabled}
            >
              {action.icon && <action.icon className='h-3.5 w-3.5' />}
              {action.label}
            </Button>
          ))}

          {/* More menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <span>
                <Button variant='ghost' size='icon' className='rounded-full'>
                  <MoreVertical className='h-4 w-4' />
                </Button>
              </span>
            </DropdownMenuTrigger>
            <DropdownMenuContent align='end' className='w-48'>
              <DropdownMenuItem className='cursor-pointer gap-2'>
                <ExternalLink className='h-4 w-4' /> Open in New Tab
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className='text-destructive focus:text-destructive focus:bg-destructive/10 cursor-pointer gap-2'>
                <Trash2 className='h-4 w-4' /> Delete Item
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Item header card */}
      <div className='bg-card/60 space-y-4 rounded-lg border p-6 shadow-lg backdrop-blur-sm md:p-8'>
        {/* Badges */}
        <div className='flex flex-wrap items-center gap-2'>
          <Badge variant='outline' className='text-[10px] font-black tracking-[0.35em] uppercase'>
            {item.view || 'general'}
          </Badge>
          <Badge variant='outline' className='text-[10px] font-black tracking-[0.35em] uppercase'>
            {item.type}
          </Badge>
          <Badge
            className={cn(
              'text-[10px] font-black uppercase tracking-[0.35em]',
              statusColors[item.status] ?? statusColors['todo'],
            )}
          >
            {item.status.replace('_', ' ')}
          </Badge>
          <Badge
            className={cn(
              'text-[10px] font-black',
              priorityColors[item.priority] ?? priorityColors['medium'],
            )}
          >
            {item.priority}
          </Badge>
        </div>

        {/* Title and description */}
        <div>
          <p className='text-muted-foreground mb-1 text-sm font-semibold tracking-widest uppercase'>
            {viewLabel} · {item.type}
          </p>
          <h1
            className='mb-3 text-3xl leading-tight font-black tracking-tight md:text-4xl lg:text-5xl'
            style={{
              fontFamily: '"Space Grotesk","Sora","IBM Plex Sans",sans-serif',
            }}
          >
            {item.title}
          </h1>
          {item.description && (
            <p className='text-muted-foreground text-base leading-relaxed md:text-lg'>
              {item.description}
            </p>
          )}
        </div>

        {/* Metadata row */}
        <div className='text-muted-foreground flex flex-wrap items-center gap-3 text-xs font-bold tracking-widest uppercase'>
          <span>ID: {item.id.slice(0, 8)}</span>
          <span>•</span>
          <span>v{item.version}</span>
          {item.owner && (
            <>
              <span>•</span>
              <span>Owner: {item.owner}</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
