import type { LucideIcon } from 'lucide-react';

import { formatValue } from '@/views/item-detail/selectors';
import { Card } from '@tracertm/ui';

type MetadataEntry = readonly [key: string, value: unknown];

interface MetadataCategoryCardProps {
  title: string;
  Icon: LucideIcon;
  iconClassName: string;
  entries: readonly MetadataEntry[];
  emptyMessage: string;
}

export function MetadataCategoryCard({
  emptyMessage,
  entries,
  Icon,
  iconClassName,
  title,
}: MetadataCategoryCardProps): JSX.Element {
  let body: JSX.Element = (
    <p className='border-border/50 bg-background/50 text-muted-foreground rounded-xl border border-dashed py-6 text-center text-xs italic'>
      {emptyMessage}
    </p>
  );

  if (entries.length > 0) {
    body = (
      <div className='space-y-3'>
        {entries.map(([key, value]) => (
          <div
            key={key}
            className='border-border/40 bg-card/60 flex items-start justify-between gap-4 rounded-xl border px-4 py-3 shadow-sm'
          >
            <span className='text-muted-foreground min-w-0 flex-1 truncate text-[10px] font-black tracking-widest uppercase'>
              {key}
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
    <Card className='bg-muted/40 space-y-4 border-0 p-5'>
      <div className='flex items-center justify-between'>
        <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
          {title}
        </h3>
        <Icon className={iconClassName} />
      </div>
      {body}
    </Card>
  );
}
