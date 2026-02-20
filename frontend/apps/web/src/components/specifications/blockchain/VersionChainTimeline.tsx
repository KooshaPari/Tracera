/**
 * Version Chain Timeline Component
 * Displays the blockchain-style version history of a specification
 */

import { cn } from '@/lib/utils';

interface VersionChainEntry {
  version_hash: string;
  version_number: number;
  content_hash: string;
  previous_hash: string | null;
  created_at: string;
  created_by: string | null;
  change_summary: string | null;
}

interface VersionChainTimelineProps {
  chainHead: string;
  chainLength: number;
  entries: VersionChainEntry[];
  chainValid: boolean;
  brokenLinks?: string[];
  maxDisplay?: number;
  className?: string;
}

export function VersionChainTimeline({
  chainHead,
  chainLength,
  entries,
  chainValid,
  brokenLinks = [],
  maxDisplay = 10,
  className,
}: VersionChainTimelineProps) {
  const displayEntries = entries.slice(0, maxDisplay);
  const hasMore = entries.length > maxDisplay;

  return (
    <div className={cn('rounded-lg border p-4 space-y-4', className)}>
      {/* Header */}
      <div className='flex items-start justify-between'>
        <div>
          <h3 className='flex items-center gap-2 text-lg font-semibold'>
            <span>⛓</span>
            Version Chain
          </h3>
          <p className='text-muted-foreground text-sm'>{chainLength} versions in chain</p>
        </div>
        <div className='flex items-center gap-2'>
          {chainValid ? (
            <span className='rounded-md bg-green-100 px-2 py-1 text-xs font-medium text-green-700'>
              ✓ Chain Valid
            </span>
          ) : (
            <span className='rounded-md bg-red-100 px-2 py-1 text-xs font-medium text-red-700'>
              ✕ Chain Invalid
            </span>
          )}
        </div>
      </div>

      {/* Chain Head */}
      <div className='bg-muted rounded p-2'>
        <div className='text-muted-foreground mb-1 text-xs'>Chain Head</div>
        <code className='font-mono text-xs break-all'>{chainHead}</code>
      </div>

      {/* Broken Links Warning */}
      {brokenLinks.length > 0 && (
        <div className='rounded-lg border border-red-200 bg-red-50 p-3'>
          <div className='mb-1 flex items-center gap-2 font-medium text-red-700'>
            <span>⚠</span>
            <span>Broken Links Detected</span>
          </div>
          <ul className='space-y-1 text-sm text-red-600'>
            {brokenLinks.map((link, idx) => (
              <li key={idx} className='font-mono text-xs'>
                {link}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Timeline */}
      <div className='relative'>
        {/* Vertical line */}
        <div className='bg-border absolute top-0 bottom-0 left-4 w-0.5' />

        {/* Entries */}
        <div className='space-y-4'>
          {displayEntries.map((entry, idx) => (
            <VersionChainEntry
              key={entry.version_hash}
              entry={entry}
              isHead={idx === 0}
              isLast={idx === displayEntries.length - 1 && !hasMore}
            />
          ))}

          {hasMore && (
            <div className='relative pl-10'>
              <div className='bg-muted-foreground absolute top-1/2 left-[14px] h-2 w-2 -translate-y-1/2 rounded-full' />
              <div className='text-muted-foreground text-sm'>
                +{entries.length - maxDisplay} more versions...
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

interface VersionChainEntryProps {
  entry: VersionChainEntry;
  isHead?: boolean;
  isLast?: boolean;
}

function VersionChainEntry({ entry, isHead }: VersionChainEntryProps) {
  const date = new Date(entry.created_at);
  const formattedDate = date.toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
  const formattedTime = date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className='relative pl-10'>
      {/* Node */}
      <div
        className={cn(
          'absolute left-[10px] top-2 w-3 h-3 rounded-full border-2 bg-background',
          isHead ? 'border-primary bg-primary' : 'border-muted-foreground',
        )}
      />

      {/* Content */}
      <div
        className={cn(
          'p-3 rounded-lg border',
          isHead ? 'bg-primary/5 border-primary/20' : 'bg-muted/50',
        )}
      >
        <div className='mb-2 flex items-start justify-between gap-2'>
          <div className='flex items-center gap-2'>
            <span className='font-semibold'>v{entry.version_number}</span>
            {isHead && (
              <span className='bg-primary text-primary-foreground rounded px-1.5 py-0.5 text-xs'>
                HEAD
              </span>
            )}
          </div>
          <div className='text-muted-foreground text-right text-xs'>
            <div>{formattedDate}</div>
            <div>{formattedTime}</div>
          </div>
        </div>

        {entry.change_summary && <p className='mb-2 text-sm'>{entry.change_summary}</p>}

        {entry.created_by && (
          <div className='text-muted-foreground mb-2 text-xs'>by {entry.created_by}</div>
        )}

        <div className='grid grid-cols-2 gap-2 text-xs'>
          <div>
            <span className='text-muted-foreground'>Hash: </span>
            <code className='font-mono'>{entry.version_hash.slice(0, 8)}...</code>
          </div>
          <div>
            <span className='text-muted-foreground'>Content: </span>
            <code className='font-mono'>{entry.content_hash.slice(0, 8)}...</code>
          </div>
        </div>

        {entry.previous_hash && (
          <div className='mt-2 border-t pt-2 text-xs'>
            <span className='text-muted-foreground'>Previous: </span>
            <code className='font-mono'>{entry.previous_hash.slice(0, 8)}...</code>
          </div>
        )}
      </div>
    </div>
  );
}

interface VersionChainBadgeProps {
  chainLength: number;
  chainValid: boolean;
  className?: string;
}

export function VersionChainBadge({ chainLength, chainValid, className }: VersionChainBadgeProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-sm font-medium',
        chainValid ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700',
        className,
      )}
    >
      <span>⛓</span>
      <span>{chainLength} versions</span>
      {chainValid ? (
        <span className='text-green-600'>✓</span>
      ) : (
        <span className='text-red-600'>✕</span>
      )}
    </div>
  );
}
