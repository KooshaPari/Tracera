/**
 * LinksTab - Shared component for displaying item relationships
 * Shows upstream and downstream links in a consistent format
 */

import { Link } from '@tanstack/react-router';
import { ArrowLeft, ExternalLink } from 'lucide-react';

import type { Link as LinkType } from '@tracertm/types';

import { Card } from '@tracertm/ui';

export interface LinksTabProps {
  sourceLinks: LinkType[];
  targetLinks: LinkType[];
  buildItemLink: (id: string) => string;
}

export function LinksTab({ sourceLinks, targetLinks, buildItemLink }: LinksTabProps) {
  return (
    <div className='grid grid-cols-1 gap-6 md:grid-cols-2'>
      {/* Upstream links */}
      <Card className='bg-muted/40 space-y-3 border-0 p-4'>
        <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
          Upstream Dependencies
        </h3>
        <div className='space-y-2'>
          {targetLinks.length > 0 ? (
            targetLinks.map((link) => (
              <Link
                key={link.id}
                to={buildItemLink(link.sourceId)}
                className='bg-card/50 hover:bg-muted/60 flex items-center gap-3 rounded-xl border px-3 py-2 transition-colors'
              >
                <div className='flex h-8 w-8 items-center justify-center rounded-lg bg-orange-500/10'>
                  <ArrowLeft className='h-4 w-4 text-orange-500' />
                </div>
                <div className='min-w-0 flex-1'>
                  <p className='text-muted-foreground text-[10px] font-black uppercase'>
                    {link.type}
                  </p>
                  <p className='truncate text-xs font-bold'>{link.sourceId}</p>
                </div>
                <ExternalLink className='text-muted-foreground h-3.5 w-3.5' />
              </Link>
            ))
          ) : (
            <p className='text-muted-foreground py-4 text-center text-xs italic'>
              No upstream dependencies
            </p>
          )}
        </div>
      </Card>

      {/* Downstream links */}
      <Card className='bg-muted/40 space-y-3 border-0 p-4'>
        <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
          Downstream Impact
        </h3>
        <div className='space-y-2'>
          {sourceLinks.length > 0 ? (
            sourceLinks.map((link) => (
              <Link
                key={link.id}
                to={buildItemLink(link.targetId)}
                className='bg-card/50 hover:bg-muted/60 flex items-center gap-3 rounded-xl border px-3 py-2 transition-colors'
              >
                <div className='flex h-8 w-8 items-center justify-center rounded-lg bg-sky-500/10'>
                  <ArrowLeft className='h-4 w-4 rotate-180 text-sky-500' />
                </div>
                <div className='min-w-0 flex-1'>
                  <p className='text-muted-foreground text-[10px] font-black uppercase'>
                    {link.type}
                  </p>
                  <p className='truncate text-xs font-bold'>{link.targetId}</p>
                </div>
                <ExternalLink className='text-muted-foreground h-3.5 w-3.5' />
              </Link>
            ))
          ) : (
            <p className='text-muted-foreground py-4 text-center text-xs italic'>
              No downstream impact
            </p>
          )}
        </div>
      </Card>
    </div>
  );
}
