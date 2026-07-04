import type { TimelineEvent } from '@/views/item-detail/types';

import { Card } from '@tracertm/ui';

const DATE_FORMAT_OPTIONS: Intl.DateTimeFormatOptions = {
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  month: 'short',
  year: 'numeric',
};

function renderEventDetail(detail: string | undefined): JSX.Element {
  if (detail !== undefined) {
    return <p className='text-muted-foreground mt-1 text-xs'>{detail}</p>;
  }
  return <span className='hidden' />;
}

export function ChangeLogCard({ events }: { events: TimelineEvent[] }): JSX.Element {
  let body: JSX.Element = (
    <p className='border-border/50 bg-background/50 text-muted-foreground rounded-xl border border-dashed py-6 text-center text-xs italic'>
      No change events recorded.
    </p>
  );

  if (events.length > 0) {
    body = (
      <div className='relative space-y-0'>
        <div className='bg-border absolute top-2 bottom-2 left-[11px] w-px' />
        {events.map((event) => (
          <div
            key={`${event.label}-${event.timestamp}`}
            className='relative flex items-start gap-4 pb-6 last:pb-0'
          >
            <div className='border-primary/40 bg-primary/10 relative z-10 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2'>
              <div className='bg-primary h-1.5 w-1.5 rounded-full' />
            </div>
            <div className='border-border/40 bg-card/60 min-w-0 flex-1 rounded-xl border px-4 py-3 shadow-sm'>
              <p className='text-foreground text-sm font-semibold'>{event.label}</p>
              {renderEventDetail(event.detail)}
              <p className='text-muted-foreground mt-2 text-[10px] font-medium tracking-wider uppercase'>
                {new Date(event.timestamp).toLocaleDateString(undefined, DATE_FORMAT_OPTIONS)}
              </p>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <Card className='bg-muted/40 space-y-4 border-0 p-6 shadow-sm'>
      <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
        Change log
      </h3>
      {body}
    </Card>
  );
}
