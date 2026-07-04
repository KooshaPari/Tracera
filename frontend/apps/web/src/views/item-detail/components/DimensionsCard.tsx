import { GitBranch } from 'lucide-react';

import type { DimensionEntry } from '@/views/item-detail/types';

import { formatValue } from '@/views/item-detail/selectors';
import { Card } from '@tracertm/ui';

interface DimensionsCardProps {
  entries: DimensionEntry[];
}

export function DimensionsCard({ entries }: DimensionsCardProps): JSX.Element {
  let body: JSX.Element = (
    <p className='border-border/50 bg-background/50 text-muted-foreground rounded-xl border border-dashed py-4 text-center text-xs italic'>
      No dimensions configured.
    </p>
  );
  if (entries.length > 0) {
    body = (
      <div className='space-y-3'>
        {entries.map(([label, value]) => (
          <div
            key={label}
            className='border-border/40 bg-card/60 flex items-center justify-between rounded-xl border px-4 py-3 shadow-sm'
          >
            <span className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              {label}
            </span>
            <span
              className='text-foreground max-w-[60%] truncate text-sm font-semibold'
              title={formatValue(value)}
            >
              {formatValue(value)}
            </span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <Card className='bg-muted/40 space-y-4 border-0 p-6 shadow-sm'>
      <div className='flex items-center gap-2'>
        <div className='flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500/15'>
          <GitBranch className='h-4 w-4 text-sky-600' />
        </div>
        <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
          Dimensions
        </h3>
      </div>
      {body}
    </Card>
  );
}
