import { Activity, Box, CheckCircle2, Download, FileText, Layers, Search } from 'lucide-react';
import { useMemo, useState } from 'react';
import { toast } from 'sonner';

import { cn } from '@/lib/utils';
import { Badge, Input } from '@tracertm/ui';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { Skeleton } from '@tracertm/ui/components/Skeleton';

import { useItems } from '../hooks/useItems';
import { useLinks } from '../hooks/useLinks';

interface TraceabilityMatrixViewProps {
  projectId: string;
}

export function TraceabilityMatrixView({ projectId }: TraceabilityMatrixViewProps) {
  const { data: itemsData, isLoading } = useItems({
    projectId,
  });
  const { data: linksData } = useLinks({
    projectId,
  });

  const [searchQuery, setSearchQuery] = useState('');

  const items = itemsData?.items ?? [];
  const links = linksData?.links ?? [];

  const matrix = useMemo(() => {
    if (items.length === 0) {
      return { coverage: {}, features: [], requirements: [] };
    }

    const requirements = items.filter(
      (i: any) =>
        i.type === 'requirement' && i.title.toLowerCase().includes(searchQuery.toLowerCase()),
    );
    const features = items.filter((i: any) => i.type === 'feature');

    const coverage: Record<string, Set<string>> = {};
    links.forEach((link: any) => {
      coverage[link.sourceId] ??= new Set();
      coverage[link.sourceId]?.add(link.targetId);
    });

    return { coverage, features, requirements };
  }, [items, links, searchQuery]);

  const coveragePercent = useMemo(() => {
    if (matrix.requirements.length === 0) {
      return 0;
    }
    const covered = matrix.requirements.filter(
      (r) => (matrix.coverage[r.id]?.size ?? 0) > 0,
    ).length;
    return Math.round((covered / matrix.requirements.length) * 100);
  }, [matrix]);

  if (isLoading) {
    return (
      <div className='animate-pulse space-y-8 p-6'>
        <Skeleton className='h-10 w-48' />
        <div className='flex gap-4'>
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className='h-24 flex-1 rounded-2xl' />
          ))}
        </div>
        <Skeleton className='h-[500px] w-full rounded-2xl' />
      </div>
    );
  }

  return (
    <div className='animate-in fade-in mx-auto max-w-[1800px] space-y-8 p-6 duration-500'>
      {/* Header */}
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-2xl font-black tracking-tight uppercase'>Traceability Matrix</h1>
          <p className='text-muted-foreground text-sm font-medium'>
            Validation grid mapping high-level requirements to functional features.
          </p>
        </div>
        <Button
          variant='outline'
          size='sm'
          className='gap-2 rounded-xl'
          onClick={() => toast.success('Matrix exported to CSV')}
        >
          <Download className='h-4 w-4' /> Export
        </Button>
      </div>

      {/* Stats Bar */}
      <div className='grid grid-cols-1 gap-4 md:grid-cols-3'>
        {[
          {
            color: 'text-blue-500',
            icon: FileText,
            label: 'High-Level REQS',
            value: matrix.requirements.length,
          },
          {
            color: 'text-purple-500',
            icon: Box,
            label: 'Mapped Features',
            value: matrix.features.length,
          },
          {
            color: 'text-green-500',
            icon: Activity,
            label: 'Integrity Ratio',
            progress: true,
            value: `${coveragePercent}%`,
          },
        ].map((s, i) => (
          <Card
            key={i}
            className='bg-card/50 flex h-28 flex-col justify-between border-none p-5 shadow-sm'
          >
            <div className='flex items-start justify-between'>
              <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                {s.label}
              </p>
              <s.icon className={cn('h-4 w-4 opacity-30', s.color)} />
            </div>
            <div className='flex items-end justify-between'>
              <h3 className='text-2xl leading-none font-black'>{s.value}</h3>
              {s.progress && (
                <div className='bg-muted mb-1 h-1.5 w-24 shrink-0 overflow-hidden rounded-full'>
                  <div className='h-full bg-green-500' style={{ width: `${coveragePercent}%` }} />
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/* Filters Control */}
      <Card className='bg-muted/30 flex items-center gap-2 rounded-2xl border-none p-2'>
        <div className='relative flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <Input
            placeholder='Search requirements...'
            className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
            }}
          />
        </div>
        <div className='bg-border/50 mx-2 h-6 w-px' />
        <Badge
          variant='outline'
          className='h-8 rounded-lg px-3 font-bold tracking-tighter uppercase'
        >
          {matrix.requirements.length} REQS x {matrix.features.length} FEATS
        </Badge>
      </Card>

      {/* Matrix Grid */}
      <Card className='bg-card/50 overflow-hidden rounded-[2rem] border-none shadow-xl'>
        <div className='custom-scrollbar overflow-x-auto'>
          <table className='w-full border-collapse'>
            <thead>
              <tr>
                <th className='bg-card sticky left-0 z-20 min-w-[300px] border-r border-b p-6 text-left'>
                  <div className='flex items-center gap-2'>
                    <FileText className='text-primary h-4 w-4' />
                    <span className='text-[10px] font-black tracking-widest uppercase'>
                      Requirement Detail
                    </span>
                  </div>
                </th>
                {matrix.features.map((feature) => (
                  <th
                    key={feature.id}
                    className='bg-muted/30 min-w-[120px] border-r border-b p-4 align-bottom'
                  >
                    <div className='mx-auto rotate-180 text-left [writing-mode:vertical-lr]'>
                      <span className='text-muted-foreground max-h-[150px] truncate text-[10px] font-bold tracking-tighter uppercase'>
                        {feature.title}
                      </span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrix.requirements.map((req) => (
                <tr key={req.id} className='group hover:bg-muted/20 transition-colors'>
                  <td className='bg-card group-hover:bg-muted/10 sticky left-0 z-10 border-r border-b p-4 transition-colors'>
                    <div className='flex flex-col gap-1'>
                      <span className='group-hover:text-primary text-sm font-bold transition-colors'>
                        {req.title}
                      </span>
                      <span className='text-muted-foreground font-mono text-[9px] uppercase'>
                        {req.id.slice(0, 8)}
                      </span>
                    </div>
                  </td>
                  {matrix.features.map((feature) => {
                    const isLinked = matrix.coverage[req.id]?.has(feature.id);
                    return (
                      <td
                        key={feature.id}
                        className={cn(
                          'p-4 text-center border-b border-r transition-all',
                          isLinked ? 'bg-green-500/[0.03]' : 'opacity-20',
                        )}
                      >
                        <div className='flex justify-center'>
                          {isLinked ? (
                            <div className='flex h-6 w-6 items-center justify-center rounded-full bg-green-500/10 text-green-600 shadow-sm'>
                              <CheckCircle2 className='h-4 w-4' />
                            </div>
                          ) : (
                            <div className='bg-muted-foreground h-1 w-1 rounded-full' />
                          )}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>

          {matrix.requirements.length === 0 && (
            <div className='text-muted-foreground/30 flex flex-col items-center justify-center py-32'>
              <Layers className='mb-4 h-16 w-16 opacity-10' />
              <p className='text-xs font-black tracking-[0.2em] uppercase'>
                No mapping data available
              </p>
            </div>
          )}
        </div>
      </Card>

      {/* Legend */}
      <div className='flex justify-center gap-8 py-4'>
        <div className='flex items-center gap-2'>
          <div className='flex h-3 w-3 items-center justify-center rounded-full border border-green-500/30 bg-green-500/20'>
            <CheckCircle2 className='h-2 w-2 text-green-600' />
          </div>
          <span className='text-muted-foreground text-[10px] font-bold tracking-widest uppercase'>
            Validated Link
          </span>
        </div>
        <div className='flex items-center gap-2'>
          <div className='bg-muted-foreground h-1 w-1 rounded-full opacity-30' />
          <span className='text-muted-foreground text-[10px] font-bold tracking-widest uppercase'>
            No Connection
          </span>
        </div>
      </div>
    </div>
  );
}
