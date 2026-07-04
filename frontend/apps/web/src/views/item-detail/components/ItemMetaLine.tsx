import { CalendarClock, CircleDot, Link2 } from 'lucide-react';

interface ItemMetaLineProps {
  createdAtLabel: string;
  updatedAtLabel: string;
  totalLinks: number;
}

export function ItemMetaLine({
  createdAtLabel,
  totalLinks,
  updatedAtLabel,
}: ItemMetaLineProps): JSX.Element {
  return (
    <div className='text-muted-foreground flex flex-wrap items-center gap-3 text-xs font-bold tracking-widest uppercase'>
      <span className='inline-flex items-center gap-2'>
        <CalendarClock className='h-3.5 w-3.5' />
        Created {createdAtLabel}
      </span>
      <span className='inline-flex items-center gap-2'>
        <CircleDot className='h-3.5 w-3.5' />
        Updated {updatedAtLabel}
      </span>
      <span className='inline-flex items-center gap-2'>
        <Link2 className='h-3.5 w-3.5' />
        {totalLinks} total links
      </span>
    </div>
  );
}
