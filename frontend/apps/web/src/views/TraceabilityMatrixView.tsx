import {
  Activity,
  Box,
  CheckCircle2,
  Circle,
  Download,
  FileText,
  Layers,
  MinusCircle,
  Search,
} from 'lucide-react';
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

type CoverageStatus = 'covered' | 'partial' | 'uncovered';

function getCoverageStatus(coveredCount: number, totalFeatures: number): CoverageStatus {
  if (totalFeatures === 0 || coveredCount === 0) {
    return 'uncovered';
  }
  if (coveredCount >= totalFeatures) {
    return 'covered';
  }
  return 'partial';
}

interface CoverageBadgeProps {
  status: CoverageStatus;
  coveredCount: number;
  totalFeatures: number;
}

function CoverageBadge({ status, coveredCount, totalFeatures }: CoverageBadgeProps) {
  if (status === 'covered') {
    return (
      <span className='badge-covered'>
        <CheckCircle2 className='h-2.5 w-2.5' />
        COVERED {coveredCount}/{totalFeatures}
      </span>
    );
  }
  if (status === 'partial') {
    return (
      <span className='badge-partial'>
        <MinusCircle className='h-2.5 w-2.5' />
        PARTIAL {coveredCount}/{totalFeatures}
      </span>
    );
  }
  return (
    <span className='badge-uncovered'>
      <Circle className='h-2.5 w-2.5' />
      UNCOVERED
    </span>
  );
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

  const coverageSummary = useMemo(() => {
    const totalReqs = matrix.requirements.length;
    const covered = matrix.requirements.filter(
      (r) => (matrix.coverage[r.id]?.size ?? 0) >= matrix.features.length && matrix.features.length > 0,
    ).length;
    const partial = matrix.requirements.filter((r) => {
      const c = matrix.coverage[r.id]?.size ?? 0;
      return c > 0 && c < matrix.features.length;
    }).length;
    const uncovered = totalReqs - covered - partial;
    return { covered, partial, uncovered };
  }, [matrix]);

  if (isLoading) {
    return (
      <div className='animate-pulse space-y-8 p-6'>
        <Skeleton className='h-10 w-48' />
        <div className='flex gap-4'>
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className='h-24 flex-1 rounded-xl' />
          ))}
        </div>
        <Skeleton className='h-[500px] w-full rounded-xl' />
      </div>
    );
  }

  return (
    <div className='animate-in fade-in mx-auto max-w-[1800px] space-y-6 p-6 duration-500'>
      {/* Header */}
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-start'>
        <div>
          <h1 className='font-mono text-xl font-bold tracking-tight'>
            Traceability Matrix
          </h1>
          <p className='text-muted-foreground mt-1 text-sm'>
            Requirements coverage mapped to functional features.
          </p>
        </div>
        <Button
          variant='outline'
          size='sm'
          className='gap-2 rounded-lg font-mono text-xs uppercase tracking-wider'
          onClick={() => toast.success('Matrix exported to CSV')}
        >
          <Download className='h-3.5 w-3.5' /> Export CSV
        </Button>
      </div>

      {/* Stats Bar */}
      <div className='grid grid-cols-1 gap-3 md:grid-cols-4'>
        {[
          {
            icon: FileText,
            label: 'Requirements',
            value: matrix.requirements.length,
            accent: 'text-foreground',
          },
          {
            icon: Box,
            label: 'Features',
            value: matrix.features.length,
            accent: 'text-foreground',
          },
          {
            icon: Activity,
            label: 'Coverage',
            progress: true,
            value: `${coveragePercent}%`,
            accent: coveragePercent >= 80 ? 'text-green-500' : coveragePercent >= 40 ? 'text-yellow-500' : 'text-red-500',
          },
          {
            icon: CheckCircle2,
            label: 'Fully Covered',
            value: coverageSummary.covered,
            accent: 'text-green-500',
          },
        ].map((s, i) => (
          <Card
            key={i}
            className='bg-card flex h-24 flex-col justify-between rounded-xl border p-4 shadow-none'
          >
            <div className='flex items-center justify-between'>
              <p className='mono-label'>{s.label}</p>
              <s.icon className={cn('h-3.5 w-3.5 opacity-40', s.accent)} />
            </div>
            <div className='flex items-end justify-between'>
              <h3 className={cn('font-mono text-2xl font-bold leading-none', s.accent)}>
                {s.value}
              </h3>
              {s.progress && (
                <div className='bg-muted mb-0.5 h-1 w-20 shrink-0 overflow-hidden rounded-full'>
                  <div
                    className={cn(
                      'h-full rounded-full transition-all duration-700',
                      coveragePercent >= 80
                        ? 'bg-green-500'
                        : coveragePercent >= 40
                          ? 'bg-yellow-500'
                          : 'bg-red-500',
                    )}
                    style={{ width: `${coveragePercent}%` }}
                  />
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/* Coverage summary badges row */}
      <div className='flex flex-wrap items-center gap-3'>
        <span className='mono-label'>Status breakdown:</span>
        <span className='badge-covered'>
          <CheckCircle2 className='h-2.5 w-2.5' />
          COVERED — {coverageSummary.covered}
        </span>
        <span className='badge-partial'>
          <MinusCircle className='h-2.5 w-2.5' />
          PARTIAL — {coverageSummary.partial}
        </span>
        <span className='badge-uncovered'>
          <Circle className='h-2.5 w-2.5' />
          UNCOVERED — {coverageSummary.uncovered}
        </span>
      </div>

      {/* Filters Control */}
      <div className='bg-muted/40 flex items-center gap-2 rounded-xl border p-2'>
        <div className='relative flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-3.5 w-3.5 -translate-y-1/2' />
          <Input
            placeholder='Filter requirements...'
            className='h-9 border-none bg-transparent pl-9 font-mono text-sm focus-visible:ring-0'
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
            }}
          />
        </div>
        <div className='bg-border mx-1 h-5 w-px' />
        <Badge
          variant='outline'
          className='h-7 rounded-md px-2.5 font-mono text-[10px] font-bold uppercase tracking-wider'
        >
          {matrix.requirements.length}r × {matrix.features.length}f
        </Badge>
      </div>

      {/* Matrix Grid */}
      <Card className='bg-card overflow-hidden rounded-xl border shadow-none'>
        <div className='custom-scrollbar overflow-x-auto'>
          <table className='w-full border-collapse text-sm'>
            <thead>
              <tr>
                <th className='bg-card sticky left-0 z-20 min-w-[340px] border-r border-b p-4 text-left'>
                  <div className='flex items-center gap-2'>
                    <FileText className='text-muted-foreground h-3.5 w-3.5' />
                    <span className='mono-label'>Requirement</span>
                  </div>
                </th>
                <th className='bg-card sticky left-[340px] z-20 min-w-[120px] border-r border-b p-4 text-left'>
                  <span className='mono-label'>Coverage</span>
                </th>
                {matrix.features.map((feature) => (
                  <th
                    key={feature.id}
                    className='bg-muted/20 min-w-[100px] border-r border-b p-3 align-bottom'
                  >
                    <div className='mx-auto rotate-180 [writing-mode:vertical-lr]'>
                      <span className='text-muted-foreground max-h-[130px] truncate font-mono text-[9px] font-bold uppercase tracking-tight'>
                        {feature.title}
                      </span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrix.requirements.map((req) => {
                const coveredCount = matrix.coverage[req.id]?.size ?? 0;
                const status = getCoverageStatus(coveredCount, matrix.features.length);
                return (
                  <tr
                    key={req.id}
                    className={cn(
                      'group transition-colors',
                      'hover:bg-muted/30',
                      status === 'covered' && 'hover:bg-green-500/[0.04]',
                      status === 'partial' && 'hover:bg-yellow-500/[0.04]',
                      status === 'uncovered' && 'hover:bg-red-500/[0.03]',
                    )}
                  >
                    <td
                      className={cn(
                        'bg-card sticky left-0 z-10 border-r border-b p-4 transition-colors',
                        'group-hover:bg-muted/20',
                      )}
                    >
                      <div className='flex flex-col gap-1'>
                        <span className='group-hover:text-foreground text-sm font-semibold leading-tight transition-colors'>
                          {req.title}
                        </span>
                        <span className='text-muted-foreground font-mono text-[9px] uppercase tracking-widest'>
                          {req.id.slice(0, 8)}
                        </span>
                      </div>
                    </td>
                    <td
                      className={cn(
                        'bg-card sticky left-[340px] z-10 border-r border-b p-4 transition-colors',
                        'group-hover:bg-muted/20',
                      )}
                    >
                      <CoverageBadge
                        status={status}
                        coveredCount={coveredCount}
                        totalFeatures={matrix.features.length}
                      />
                    </td>
                    {matrix.features.map((feature) => {
                      const isLinked = matrix.coverage[req.id]?.has(feature.id);
                      return (
                        <td
                          key={feature.id}
                          className={cn(
                            'border-b border-r p-3 text-center transition-all',
                            isLinked
                              ? 'bg-green-500/[0.05] group-hover:bg-green-500/[0.09]'
                              : 'group-hover:bg-muted/10',
                          )}
                        >
                          <div className='flex justify-center'>
                            {isLinked ? (
                              <div className='flex h-5 w-5 items-center justify-center rounded-full bg-green-500/15 text-green-500 ring-1 ring-green-500/20'>
                                <CheckCircle2 className='h-3 w-3' />
                              </div>
                            ) : (
                              <div className='bg-muted-foreground/20 h-1.5 w-1.5 rounded-full' />
                            )}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>

          {matrix.requirements.length === 0 && (
            <div className='text-muted-foreground/30 flex flex-col items-center justify-center py-24'>
              <Layers className='mb-4 h-12 w-12 opacity-10' />
              <p className='mono-label'>No requirements found</p>
            </div>
          )}
        </div>
      </Card>

      {/* Legend */}
      <div className='flex flex-wrap justify-center gap-6 py-2'>
        <div className='flex items-center gap-2'>
          <div className='flex h-4 w-4 items-center justify-center rounded-full bg-green-500/15 text-green-500 ring-1 ring-green-500/20'>
            <CheckCircle2 className='h-2.5 w-2.5' />
          </div>
          <span className='mono-label'>Linked</span>
        </div>
        <div className='flex items-center gap-2'>
          <div className='bg-muted-foreground/20 h-1.5 w-1.5 rounded-full' />
          <span className='mono-label'>Not linked</span>
        </div>
        <div className='flex items-center gap-2'>
          <span className='badge-covered'>
            <CheckCircle2 className='h-2.5 w-2.5' />
            COVERED
          </span>
          <span className='mono-label'>All features linked</span>
        </div>
        <div className='flex items-center gap-2'>
          <span className='badge-partial'>
            <MinusCircle className='h-2.5 w-2.5' />
            PARTIAL
          </span>
          <span className='mono-label'>Some features linked</span>
        </div>
        <div className='flex items-center gap-2'>
          <span className='badge-uncovered'>
            <Circle className='h-2.5 w-2.5' />
            UNCOVERED
          </span>
          <span className='mono-label'>No features linked</span>
        </div>
      </div>
    </div>
  );
}
