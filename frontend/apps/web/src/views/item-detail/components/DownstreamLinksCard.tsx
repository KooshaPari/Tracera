import { Link } from '@tanstack/react-router';
import { ArrowRight, ExternalLink } from 'lucide-react';

import type { ItemLink } from '@/views/item-detail/types';

import { shortId } from '@/views/item-detail/selectors';
import { Badge, Card } from '@tracertm/ui';

interface DownstreamLinksCardProps {
  links: ItemLink[];
  buildLinkToItem: (id: string) => string;
}

export function DownstreamLinksCard({
  buildLinkToItem,
  links,
}: DownstreamLinksCardProps): JSX.Element {
  let body: JSX.Element = (
    <p className='border-border/50 bg-background/50 text-muted-foreground rounded-xl border border-dashed py-6 text-center text-xs italic'>
      Items impacted by this work will appear here.
    </p>
  );

  if (links.length > 0) {
    body = (
      <div className='space-y-3'>
        {links.map((link) => (
          <Link
            key={link.id}
            to={buildLinkToItem(link.targetId)}
            className='border-border/50 bg-card/80 hover:bg-muted/50 flex items-center gap-4 rounded-xl border px-4 py-3 shadow-sm transition-all hover:border-sky-500/30 hover:shadow-md'
          >
            <div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-sky-500/10'>
              <ArrowRight className='h-5 w-5 text-sky-500' />
            </div>
            <div className='min-w-0 flex-1 space-y-1'>
              <Badge
                variant='secondary'
                className='text-[10px] font-semibold tracking-wider uppercase'
              >
                {link.type}
              </Badge>
              <p
                className='text-foreground truncate font-mono text-xs font-medium'
                title={link.targetId}
              >
                {shortId(link.targetId)}
              </p>
            </div>
            <ExternalLink className='text-muted-foreground h-4 w-4 shrink-0' />
          </Link>
        ))}
      </div>
    );
  }

  return (
    <Card className='bg-muted/40 space-y-4 border-0 p-5'>
      <div className='flex items-center gap-2'>
        <div className='flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500/15'>
          <ArrowRight className='h-4 w-4 text-sky-600' />
        </div>
        <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
          Downstream
        </h3>
      </div>
      {body}
    </Card>
  );
}
