import { ExternalLink, Trash2 } from 'lucide-react';

import type { CardItem } from '@/components/mobile/ResponsiveCardView';
import type { TypedItem } from '@tracertm/types';

import { Badge, Button } from '@tracertm/ui';

import itemsTableConstants from './constants';
import itemsTableFormatters from './formatters';
import { PriorityDot } from './priority-dot';
import { StatusBadge } from './status-badges';

function buildCardItems(
  items: TypedItem[],
  onNavigate: (item: TypedItem) => void,
  onDelete: (id: string) => void,
): CardItem[] {
  return items.map((item) => {
    const owner = itemsTableFormatters.getItemOwnerLabel(item.owner);
    const priorityLabel = itemsTableFormatters.getPriorityLabel(item.priority);
    const handleNavigate = (): void => {
      onNavigate(item);
    };
    const handleDelete = (): void => {
      onDelete(item.id);
    };

    return {
      actions: (
        <div className='flex w-full items-center gap-2'>
          <Button
            variant='ghost'
            size='sm'
            className='h-8 min-h-[40px] w-8 flex-1 rounded-lg'
            onClick={handleNavigate}
            aria-label={`Open item ${item.title}`}
          >
            <ExternalLink className='h-3.5 w-3.5' />
            <span className='sr-only'>View</span>
          </Button>
          <Button
            variant='ghost'
            size='sm'
            className='text-destructive hover:bg-destructive/10 h-8 min-h-[40px] w-8 flex-1 rounded-lg'
            onClick={handleDelete}
            aria-label={`Delete item ${item.title}`}
          >
            <Trash2 className='h-3.5 w-3.5' />
            <span className='sr-only'>Delete</span>
          </Button>
        </div>
      ),
      badge: (
        <Badge
          variant='outline'
          className='h-5 px-1.5 text-[8px] font-black tracking-tighter uppercase'
        >
          {item.type}
        </Badge>
      ),
      id: item.id,
      onClick: handleNavigate,
      owner: (
        <div className='flex items-center gap-2'>
          <div className='bg-muted flex h-5 w-5 items-center justify-center rounded-full text-[8px] font-black uppercase'>
            {owner.initial}
          </div>
          <span className='text-muted-foreground text-[10px] font-bold uppercase'>
            {owner.label}
          </span>
        </div>
      ),
      priority: (
        <div className='flex items-center gap-1'>
          <PriorityDot priority={item.priority} />
          <span className='text-muted-foreground text-[10px] font-bold uppercase'>
            {priorityLabel}
          </span>
        </div>
      ),
      status: <StatusBadge status={item.status} />,
      subtitle: item.id.slice(0, itemsTableConstants.ITEM_ID_PREFIX_LENGTH),
      title: item.title,
    };
  });
}

export { buildCardItems };
