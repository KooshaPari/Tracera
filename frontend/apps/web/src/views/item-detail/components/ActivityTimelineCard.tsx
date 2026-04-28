import { Timer } from 'lucide-react';

import { Card } from '@tracertm/ui';

interface ActivityTimelineCardProps {
  createdAtLabel: string;
  updatedAtLabel: string;
}

export function ActivityTimelineCard({
  createdAtLabel,
  updatedAtLabel,
}: ActivityTimelineCardProps): JSX.Element {
  return (
    <Card className='bg-muted/40 space-y-4 border-0 p-6 shadow-sm'>
      <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
        Activity timeline
      </h3>
      <div className='space-y-3'>
        <div className='border-border/40 bg-card/60 flex items-center justify-between rounded-xl border px-4 py-3 shadow-sm'>
          <span className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
            Created
          </span>
          <span className='text-foreground text-sm font-semibold'>{createdAtLabel}</span>
        </div>
        <div className='border-border/40 bg-card/60 flex items-center justify-between rounded-xl border px-4 py-3 shadow-sm'>
          <span className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
            Updated
          </span>
          <span className='text-foreground text-sm font-semibold'>{updatedAtLabel}</span>
        </div>
        <div className='border-border/40 bg-card/60 flex items-center justify-between rounded-xl border px-4 py-3 shadow-sm'>
          <span className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
            System lag
          </span>
          <span className='text-foreground inline-flex items-center gap-1.5 text-sm font-semibold'>
            <Timer className='text-primary h-3.5 w-3.5' />
            recent
          </span>
        </div>
      </div>
    </Card>
  );
}
