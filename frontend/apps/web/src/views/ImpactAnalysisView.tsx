import {
  ArrowRight,
  ChevronRight,
  FileText,
  Info,
  Search,
  ShieldAlert,
  Target,
  Zap,
} from 'lucide-react';
import { useMemo, useState } from 'react';

import { cn } from '@/lib/utils';
import { Input, Separator } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { Skeleton } from '@tracertm/ui/components/Skeleton';

import { useItems } from '../hooks/useItems';
import { useLinks } from '../hooks/useLinks';

interface ImpactAnalysisViewProps {
  projectId: string;
}

export function ImpactAnalysisView({ projectId }: ImpactAnalysisViewProps) {
  const { data: itemsData, isLoading: itemsLoading } = useItems({
    projectId,
  });
  const { data: linksData } = useLinks({
    projectId,
  });
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const items = itemsData?.items ?? [];
  const links = linksData?.links ?? [];

  const filteredItems = useMemo(
    () => items.filter((i) => i.title.toLowerCase().includes(searchQuery.toLowerCase())),
    [items, searchQuery],
  );

  const analyzeImpact = (itemId: string) => {
    if (links.length === 0) {
      return { direct: [], indirect: [] };
    }

    const direct = new Set<string>();
    const indirect = new Set<string>();

    links.forEach((link: any) => {
      if (link.sourceId === itemId) {
        direct.add(link.targetId);
      }
    });

    direct.forEach((directId) => {
      links.forEach((link: any) => {
        if (link.sourceId === directId && !direct.has(link.targetId) && link.targetId !== itemId) {
          indirect.add(link.targetId);
        }
      });
    });

    return {
      direct: [...direct],
      indirect: [...indirect],
    };
  };

  const impact = selectedItemId ? analyzeImpact(selectedItemId) : null;
  const selectedItem = items.find((i: any) => i.id === selectedItemId);

  if (itemsLoading) {
    return (
      <div className='animate-pulse space-y-8 p-6'>
        <Skeleton className='h-10 w-48' />
        <div className='grid grid-cols-1 gap-8 md:grid-cols-2'>
          <Skeleton className='h-[600px] rounded-2xl' />
          <Skeleton className='h-[600px] rounded-2xl' />
        </div>
      </div>
    );
  }

  return (
    <div className='animate-in fade-in mx-auto max-w-[1600px] space-y-8 p-6 duration-500'>
      {/* Header */}
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-2xl font-black tracking-tight uppercase'>Impact Intelligence</h1>
          <p className='text-muted-foreground text-sm font-medium'>
            Predict the ripple effect of changes across the traceability network.
          </p>
        </div>
        <div className='flex gap-2'>
          <Button
            variant='outline'
            size='sm'
            className='gap-2 rounded-xl text-[10px] font-bold tracking-widest uppercase'
          >
            <ShieldAlert className='h-3 w-3' /> Risk Map
          </Button>
        </div>
      </div>

      <div className='grid grid-cols-1 gap-8 lg:grid-cols-5'>
        {/* Selection Column */}
        <div className='space-y-4 lg:col-span-2'>
          <div className='mb-2 flex items-center gap-2'>
            <Search className='text-primary h-4 w-4' />
            <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
              Source Node
            </h3>
          </div>
          <Card className='bg-muted/30 space-y-4 rounded-2xl border-none p-4'>
            <div className='relative'>
              <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
              <Input
                placeholder='Search project items...'
                className='bg-background rounded-xl border-none pl-10 shadow-sm'
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                }}
              />
            </div>
            <div className='custom-scrollbar max-h-[60vh] space-y-1 overflow-y-auto pr-2'>
              {filteredItems.map((item) => (
                <div
                  key={item.id}
                  onClick={() => {
                    setSelectedItemId(item.id);
                  }}
                  className={cn(
                    'p-3 rounded-xl cursor-pointer transition-all border-2 border-transparent group',
                    selectedItemId === item.id
                      ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20 border-primary'
                      : 'bg-background/50 hover:bg-background hover:border-primary/20',
                  )}
                >
                  <div className='flex items-center justify-between gap-3'>
                    <div className='flex min-w-0 items-center gap-3'>
                      <div
                        className={cn(
                          'h-8 w-8 rounded-lg flex items-center justify-center shrink-0 transition-colors',
                          selectedItemId === item.id
                            ? 'bg-primary-foreground/20'
                            : 'bg-muted text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary',
                        )}
                      >
                        <FileText className='h-4 w-4' />
                      </div>
                      <div className='min-w-0'>
                        <p className='truncate text-sm font-bold'>{item.title}</p>
                        <p
                          className={cn(
                            'text-[9px] font-black uppercase tracking-widest leading-none mt-1',
                            selectedItemId === item.id
                              ? 'text-primary-foreground/60'
                              : 'text-muted-foreground',
                          )}
                        >
                          {item.type}
                        </p>
                      </div>
                    </div>
                    <ChevronRight
                      className={cn(
                        'h-4 w-4 opacity-40 shrink-0',
                        selectedItemId === item.id ? 'text-primary-foreground' : '',
                      )}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Result Column */}
        <div className='space-y-6 lg:col-span-3'>
          {selectedItem && impact ? (
            <div className='animate-in slide-in-from-right-4 space-y-6 duration-500'>
              {/* Assessment Summary */}
              <div className='grid grid-cols-1 gap-4 md:grid-cols-3'>
                <Card className='bg-primary text-primary-foreground shadow-primary/20 rounded-2xl border-none p-5 shadow-xl'>
                  <p className='text-[10px] font-black tracking-widest uppercase opacity-70'>
                    Blast Radius
                  </p>
                  <div className='mt-2 flex items-end gap-2'>
                    <span className='text-4xl font-black'>
                      {impact.direct.length + impact.indirect.length}
                    </span>
                    <span className='mb-1 text-xs font-bold opacity-70'>NODES</span>
                  </div>
                </Card>
                <Card className='bg-muted/30 rounded-2xl border-none p-5'>
                  <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                    Direct Links
                  </p>
                  <div className='mt-2 flex items-end gap-2'>
                    <span className='text-4xl font-black'>{impact.direct.length}</span>
                    <div className='mb-2 h-2 w-2 animate-pulse rounded-full bg-orange-500' />
                  </div>
                </Card>
                <Card className='bg-muted/30 rounded-2xl border-none p-5'>
                  <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                    Indirect (Lv2)
                  </p>
                  <div className='mt-2 flex items-end gap-2'>
                    <span className='text-4xl font-black'>{impact.indirect.length}</span>
                    <div className='mb-2 h-2 w-2 rounded-full bg-yellow-500' />
                  </div>
                </Card>
              </div>

              {/* Detail Card */}
              <Card className='bg-card/50 space-y-8 rounded-[2rem] border-none p-8 shadow-sm'>
                <div className='flex items-center gap-4'>
                  <div className='bg-muted flex h-12 w-12 items-center justify-center rounded-2xl'>
                    <Target className='text-primary h-6 w-6' />
                  </div>
                  <div>
                    <h2 className='text-xl font-black tracking-tight uppercase'>Analysis Report</h2>
                    <p className='text-muted-foreground text-xs font-bold tracking-widest uppercase'>
                      Selected Item: {selectedItem.id.slice(0, 8)}
                    </p>
                  </div>
                </div>

                <div className='space-y-6'>
                  {/* Direct Section */}
                  <div className='space-y-4'>
                    <div className='flex items-center gap-2'>
                      <div className='h-1.5 w-1.5 rounded-full bg-orange-500' />
                      <h3 className='text-xs font-black tracking-widest uppercase'>
                        Primary Impact Surface
                      </h3>
                    </div>
                    <div className='grid grid-cols-1 gap-3 md:grid-cols-2'>
                      {impact.direct.length > 0 ? (
                        impact.direct.map((id) => {
                          const item = items.find((i) => i.id === id);
                          return (
                            <div
                              key={id}
                              className='group rounded-xl border border-orange-500/20 bg-orange-500/5 p-3 transition-colors hover:bg-orange-500/10'
                            >
                              <p className='truncate text-xs font-bold'>{item?.title ?? id}</p>
                              <div className='mt-1 flex items-center justify-between'>
                                <Badge
                                  variant='outline'
                                  className='h-3.5 border-orange-500/30 px-1 text-[8px] font-black text-orange-600 uppercase'
                                >
                                  {item?.type ?? 'node'}
                                </Badge>
                                <ArrowRight className='h-3 w-3 text-orange-500 opacity-0 transition-opacity group-hover:opacity-100' />
                              </div>
                            </div>
                          );
                        })
                      ) : (
                        <div className='text-muted-foreground col-span-full rounded-2xl border-2 border-dashed p-8 text-center italic'>
                          <p className='text-xs'>No direct dependencies identified</p>
                        </div>
                      )}
                    </div>
                  </div>

                  <Separator className='bg-border/50' />

                  {/* Indirect Section */}
                  <div className='space-y-4'>
                    <div className='flex items-center gap-2'>
                      <div className='h-1.5 w-1.5 rounded-full bg-yellow-500' />
                      <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
                        Secondary Ripple Effect
                      </h3>
                    </div>
                    <div className='grid grid-cols-1 gap-3 md:grid-cols-2'>
                      {impact.indirect.length > 0 ? (
                        impact.indirect.map((id) => {
                          const item = items.find((i) => i.id === id);
                          return (
                            <div
                              key={id}
                              className='border-border bg-muted/20 group hover:bg-muted/40 rounded-xl border p-3 transition-colors'
                            >
                              <p className='text-muted-foreground group-hover:text-foreground truncate text-xs font-bold transition-colors'>
                                {item?.title ?? id}
                              </p>
                              <div className='mt-1 flex items-center justify-between'>
                                <Badge
                                  variant='outline'
                                  className='h-3.5 px-1 text-[8px] font-black uppercase'
                                >
                                  {item?.type ?? 'node'}
                                </Badge>
                                <ArrowRight className='text-muted-foreground h-3 w-3 opacity-0 transition-opacity group-hover:opacity-100' />
                              </div>
                            </div>
                          );
                        })
                      ) : (
                        <div className='text-muted-foreground col-span-full rounded-2xl border-2 border-dashed p-8 text-center italic'>
                          <p className='text-xs'>No secondary impacts predicted</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* AI Footer Alert */}
                <div className='flex items-start gap-4 rounded-2xl border border-blue-500/20 bg-blue-500/10 p-4'>
                  <Info className='h-5 w-5 shrink-0 text-blue-500' />
                  <div className='space-y-1'>
                    <p className='text-xs font-bold text-blue-700 dark:text-blue-400'>
                      Heuristic Analysis Tip
                    </p>
                    <p className='text-[10px] leading-relaxed font-medium text-blue-600 dark:text-blue-300'>
                      Items in the ripple effect have a higher probability of requiring regression
                      testing. Consider prioritizing these in your next sprint.
                    </p>
                  </div>
                </div>
              </Card>
            </div>
          ) : (
            <div className='text-muted-foreground/40 flex h-full min-h-[400px] flex-col items-center justify-center rounded-[2rem] border-2 border-dashed p-12 text-center'>
              <div className='bg-muted mb-6 flex h-20 w-20 items-center justify-center rounded-full'>
                <Zap className='h-10 w-10 opacity-20' />
              </div>
              <h3 className='text-sm font-black tracking-[0.2em] uppercase'>System Standby</h3>
              <p className='mt-2 text-xs font-medium'>
                Select a node from the registry to initialize impact computation.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
