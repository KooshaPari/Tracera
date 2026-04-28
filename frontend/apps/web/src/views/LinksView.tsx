import { Link } from '@tanstack/react-router';
import {
  Activity,
  ArrowRight,
  ExternalLink,
  Layers,
  Link2,
  Network,
  Plus,
  Search,
  Trash2,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { toast } from 'sonner';

import { CardErrorFallback } from '@/lib/lazy-loading';
import { cn } from '@/lib/utils';
import { Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { Skeleton } from '@tracertm/ui/components/Skeleton';

import { useItems } from '../hooks/useItems';
import { useDeleteLink, useLinks } from '../hooks/useLinks';

function buildItemLink(
  itemId: string,
  item?: {
    projectId?: string;
    project_id?: string;
    view?: string;
    view_type?: string;
  },
) {
  const projectId = item?.projectId ?? item?.project_id;
  const viewType = item?.view ?? item?.view_type ?? 'feature';
  return projectId
    ? `/projects/${projectId}/views/${String(viewType).toLowerCase()}/${itemId}`
    : '/projects';
}

export function LinksView() {
  const { data: linksData, isLoading: linksLoading, error } = useLinks();
  const { data: itemsData } = useItems();
  const deleteLink = useDeleteLink();

  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');

  const links = linksData?.links ?? [];
  const items = itemsData?.items ?? [];

  const filteredLinks = useMemo(
    () =>
      links.filter((link) => {
        const matchesQuery =
          link.sourceId.toLowerCase().includes(searchQuery.toLowerCase()) ||
          link.targetId.toLowerCase().includes(searchQuery.toLowerCase()) ||
          link.type.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesType = typeFilter === 'all' || link.type === typeFilter;
        return matchesQuery && matchesType;
      }),
    [links, searchQuery, typeFilter],
  );

  const handleDelete = async (id: string) => {
    try {
      await deleteLink.mutateAsync(id);
      toast.success('Relationship link dissolved');
    } catch {
      toast.error('Failed to delete link');
    }
  };

  // Surface load failures to the user via toast
  useEffect(() => {
    if (error) {
      toast.error('Failed to load links', {
        action: {
          label: 'Retry',
          onClick: () => {
            globalThis.location.reload();
          },
        },
        description: error.message,
      });
    }
  }, [error]);

  if (linksLoading) {
    return (
      <div className='animate-pulse space-y-8 p-6'>
        <Skeleton className='h-10 w-48' />
        <Skeleton className='h-12 w-full rounded-2xl' />
        <div className='space-y-4'>
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className='h-20 w-full rounded-xl' />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className='mx-auto max-w-md p-6'>
        <CardErrorFallback
          title='Traceability interrupted'
          message='Failed to synchronize relationship graph.'
          error={error}
          retry={() => {
            globalThis.location.reload();
          }}
          className='border-destructive/20 bg-destructive/5 flex flex-col items-center justify-center rounded-lg border p-8 text-center'
        />
      </div>
    );
  }

  return (
    <div className='animate-in-fade-up mx-auto max-w-[1400px] space-y-8 p-6'>
      {/* Header */}
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-2xl font-black tracking-tight uppercase'>Traceability Links</h1>
          <p className='text-muted-foreground text-sm font-medium'>
            Manage the semantic connections between project entities.
          </p>
        </div>
        <Button
          size='sm'
          className='shadow-primary/20 gap-2 rounded-xl shadow-lg'
          onClick={() => toast.info('Create a link by selecting source and target items')}
        >
          <Plus className='h-4 w-4' /> Create Connection
        </Button>
      </div>

      {/* Executive Summary */}
      <div className='stagger-children grid grid-cols-1 gap-4 md:grid-cols-3'>
        {[
          {
            color: 'text-blue-500',
            icon: Network,
            label: 'Total Connections',
            value: links.length,
          },
          {
            color: 'text-green-500',
            icon: Activity,
            label: 'Connection Density',
            value: `${items.length > 0 ? (links.length / items.length).toFixed(2) : 0}`,
          },
          {
            color: 'text-orange-500',
            icon: Layers,
            label: 'Orphan Nodes',
            value: items.filter(
              (i) => !links.some((l) => l.sourceId === i.id || l.targetId === i.id),
            ).length,
          },
        ].map((s, i) => (
          <Card
            key={i}
            className='bg-card/50 group hover:bg-card flex items-center justify-between border-none p-5 shadow-sm transition-all duration-200 ease-out hover:shadow-md active:scale-[0.99]'
          >
            <div>
              <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                {s.label}
              </p>
              <p className='mt-1 text-2xl font-black'>{s.value}</p>
            </div>
            <div
              className={cn(
                'h-10 w-10 rounded-xl bg-muted flex items-center justify-center group-hover:scale-110 transition-transform',
                s.color,
              )}
            >
              <s.icon className='h-5 w-5' />
            </div>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card className='bg-muted/30 flex flex-wrap items-center gap-2 rounded-2xl border-none p-2'>
        <div className='relative min-w-[300px] flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <Input
            placeholder='Search by ID or connection type...'
            className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
            }}
          />
        </div>
        <div className='bg-border/50 mx-2 hidden h-6 w-px md:block' />
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className='hover:bg-background/50 h-10 w-[180px] border-none bg-transparent transition-colors'>
            <SelectValue placeholder='Link Type' />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='all'>All Types</SelectItem>
            {[...new Set(links.map((l) => l.type))].map((t) => (
              <SelectItem key={t} value={t}>
                {t}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </Card>

      {/* Links List */}
      <div className='stagger-children space-y-3'>
        {filteredLinks.length > 0 ? (
          filteredLinks.map((link) => {
            const sourceItem = items.find((i) => i.id === link.sourceId);
            const targetItem = items.find((i) => i.id === link.targetId);

            return (
              <Card
                key={link.id}
                className='bg-card/50 hover:bg-card group relative overflow-hidden border-none p-4 transition-all duration-200 ease-out hover:shadow-md active:scale-[0.99]'
              >
                <div className='relative z-10 flex flex-col gap-6 md:flex-row md:items-center'>
                  {/* Source */}
                  <Link to={buildItemLink(link.sourceId, sourceItem)} className='min-w-0 flex-1'>
                    <div className='bg-background/50 hover:border-primary/50 group/node rounded-xl border p-3 transition-colors'>
                      <div className='mb-1 flex items-center justify-between'>
                        <span className='text-muted-foreground text-[9px] font-black uppercase'>
                          Source
                        </span>
                        <ExternalLink className='h-3 w-3 opacity-0 transition-opacity group-hover/node:opacity-100' />
                      </div>
                      <p className='truncate text-sm font-bold'>
                        {sourceItem?.title ?? link.sourceId}
                      </p>
                      <p className='text-primary truncate font-mono text-[10px]'>
                        {link.sourceId.slice(0, 8)}
                      </p>
                    </div>
                  </Link>

                  {/* Relationship Type */}
                  <div className='flex shrink-0 flex-col items-center justify-center'>
                    <Badge
                      variant='secondary'
                      className='bg-primary/10 text-primary border-none px-3 py-1 text-[10px] font-black tracking-widest uppercase'
                    >
                      {link.type}
                    </Badge>
                    <div className='text-muted-foreground/30 mt-2 flex items-center gap-1'>
                      <div className='h-px w-8 bg-current' />
                      <ArrowRight className='h-4 w-4' />
                      <div className='h-px w-8 bg-current' />
                    </div>
                  </div>

                  {/* Target */}
                  <Link to={buildItemLink(link.targetId, targetItem)} className='min-w-0 flex-1'>
                    <div className='bg-background/50 hover:border-primary/50 group/node rounded-xl border p-3 transition-colors'>
                      <div className='mb-1 flex items-center justify-between'>
                        <span className='text-muted-foreground text-[9px] font-black uppercase'>
                          Target
                        </span>
                        <ExternalLink className='h-3 w-3 opacity-0 transition-opacity group-hover/node:opacity-100' />
                      </div>
                      <p className='truncate text-sm font-bold'>
                        {targetItem?.title ?? link.targetId}
                      </p>
                      <p className='text-primary truncate font-mono text-[10px]'>
                        {link.targetId.slice(0, 8)}
                      </p>
                    </div>
                  </Link>

                  {/* Actions */}
                  <div className='flex justify-end pr-2'>
                    <Button
                      variant='ghost'
                      size='icon'
                      onClick={async () => handleDelete(link.id)}
                      className='text-muted-foreground hover:text-destructive hover:bg-destructive/10 h-9 w-9 rounded-full'
                    >
                      <Trash2 className='h-4 w-4' />
                    </Button>
                  </div>
                </div>

                {/* Background decoration */}
                <div className='bg-primary/5 text-primary/40 absolute top-0 right-0 rounded-bl-xl p-1 text-[8px] font-black uppercase opacity-0 transition-opacity group-hover:opacity-100'>
                  ID: {link.id.slice(0, 6)}
                </div>
              </Card>
            );
          })
        ) : (
          <div className='text-muted-foreground/40 flex flex-col items-center justify-center py-20'>
            <Link2 className='mb-4 h-16 w-16 opacity-10' />
            <p className='text-xs font-black tracking-[0.2em] uppercase'>No connections found</p>
          </div>
        )}
      </div>
    </div>
  );
}
