import type { ItemStatus, Priority } from '@tracertm/types';

import { cn } from '@/lib/utils';
import { priorityColors, statusColors } from '@/views/item-detail/palette';
import { PRIORITY_OPTIONS, STATUS_OPTIONS } from '@/views/item-detail/types';
import {
  Badge,
  Card,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui';

interface StatusPriorityCardProps {
  isEditing: boolean;
  status: ItemStatus;
  priority: Priority;
  onChangeStatus: (value: ItemStatus) => void;
  onChangePriority: (value: Priority) => void;
}

export function StatusPriorityCard({
  isEditing,
  onChangePriority,
  onChangeStatus,
  priority,
  status,
}: StatusPriorityCardProps): JSX.Element {
  if (isEditing) {
    return (
      <Card className='bg-muted/40 space-y-3 border-0 px-4 py-3'>
        <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
          Status & Priority
        </p>
        <div className='grid grid-cols-2 gap-2'>
          <Select value={status} onValueChange={onChangeStatus}>
            <SelectTrigger className='h-8 text-xs'>
              <SelectValue placeholder='Status' />
            </SelectTrigger>
            <SelectContent>
              {STATUS_OPTIONS.map((option) => (
                <SelectItem key={option} value={option}>
                  {option.replace('_', ' ')}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={priority} onValueChange={onChangePriority}>
            <SelectTrigger className='h-8 text-xs'>
              <SelectValue placeholder='Priority' />
            </SelectTrigger>
            <SelectContent>
              {PRIORITY_OPTIONS.map((option) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </Card>
    );
  }

  return (
    <Card className='bg-muted/40 space-y-3 border-0 px-4 py-3'>
      <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
        Status & Priority
      </p>
      <div className='flex items-center gap-2'>
        <Badge
          className={cn('text-[10px] font-black uppercase tracking-widest', statusColors[status])}
        >
          {status.replace('_', ' ')}
        </Badge>
        <Badge
          className={cn(
            'text-[10px] font-black uppercase tracking-widest',
            priorityColors[priority],
          )}
        >
          {priority}
        </Badge>
      </div>
    </Card>
  );
}
