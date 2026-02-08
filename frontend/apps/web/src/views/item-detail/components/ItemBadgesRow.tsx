import { Hash } from 'lucide-react';

import type { ItemStatus, Priority } from '@tracertm/types';

import { cn } from '@/lib/utils';
import { priorityColors, statusColors } from '@/views/item-detail/palette';
import { Badge } from '@tracertm/ui';

interface ItemBadgesRowProps {
  viewLabel: string;
  typeLabel: string;
  status: ItemStatus;
  priority: Priority;
  itemId: string;
}

export function ItemBadgesRow({
  itemId,
  priority,
  status,
  typeLabel,
  viewLabel,
}: ItemBadgesRowProps): JSX.Element {
  const trimmedView = viewLabel.trim();
  let safeView = 'general';
  if (trimmedView.length > 0) {
    safeView = trimmedView;
  }

  return (
    <div className='flex flex-wrap items-center gap-2'>
      <Badge variant='outline' className='text-[10px] font-black tracking-[0.35em] uppercase'>
        {safeView}
      </Badge>
      <Badge variant='outline' className='text-[10px] font-black tracking-[0.35em] uppercase'>
        {typeLabel}
      </Badge>
      <Badge
        className={cn('text-[10px] font-black uppercase tracking-[0.35em]', statusColors[status])}
      >
        {status.replace('_', ' ')}
      </Badge>
      <Badge
        className={cn(
          'text-[10px] font-black uppercase tracking-[0.35em]',
          priorityColors[priority],
        )}
      >
        {priority}
      </Badge>
      <Badge variant='secondary' className='gap-1 text-[10px] tracking-[0.35em] uppercase'>
        <Hash className='h-3 w-3' />
        {itemId}
      </Badge>
    </div>
  );
}
