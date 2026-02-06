/* eslint-disable
  import/no-default-export,
  import/no-named-export,
  import/max-dependencies,
  eslint/prefer-default-export,
  eslint/func-style,
  eslint/curly,
  eslint/id-length,
  eslint/max-lines,
  eslint/max-lines,
  eslint/max-lines-per-function,
  eslint/max-statements,
  eslint/no-inline-comments,
  eslint/no-magic-numbers,
  eslint/no-nested-ternary,
  eslint/no-ternary,
  eslint/sort-imports,
  eslint/sort-keys,
  typescript-eslint/explicit-function-return-type,
  typescript-eslint/explicit-module-boundary-types,
  typescript-eslint/no-explicit-any,
  eslint-plugin-react/button-has-type,
  eslint-plugin-react-hooks/exhaustive-deps,
  eslint-plugin-react/jsx-boolean-value,
  eslint-plugin-react/jsx-filename-extension,
  eslint-plugin-react/jsx-max-depth,
  eslint-plugin-react-perf/jsx-no-new-function-as-prop,
  eslint-plugin-jsx-a11y/click-events-have-key-events,
  eslint-plugin-jsx-a11y/label-has-associated-control,
  oxc/no-async-await,
  oxc/no-optional-chaining
 */
/* eslint-disable-next-line max-lines */
import { useNavigate, useSearch } from '@tanstack/react-router';
import { Calendar, Clock, Filter, Plus, Search, TrendingUp, Zap } from 'lucide-react';
import { useMemo, useState } from 'react';
import { toast } from 'sonner';

import type { ADR, ADRStatus } from '@tracertm/types';

import { ADRCard } from '@/components/specifications/adr/ADRCard';
import { ADRGraph } from '@/components/specifications/adr/ADRGraph';
import { ADRTimeline } from '@/components/specifications/adr/ADRTimeline';
import { useADRs, useCreateADR } from '@/hooks/useSpecifications';
import {
  Button,
  Card,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Skeleton,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@tracertm/ui';

interface ADRListViewProps {
  projectId: string;
}

export function ADRListView({ projectId }: ADRListViewProps) {
  const navigate = useNavigate();
  const searchParams = useSearch({ strict: false }) as any;

  const { data: adrsData, isLoading } = useADRs({ projectId });
  const adrs = adrsData?.adrs ?? [];
  const createADR = useCreateADR();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<ADRStatus | 'all'>(
    (searchParams?.status as ADRStatus) || 'all',
  );
  const [dateRange, setDateRange] = useState<'all' | 'week' | 'month' | 'quarter'>(
    (searchParams?.dateRange as any) || 'all',
  );
  const [viewMode, setViewMode] = useState<'cards' | 'timeline' | 'graph'>(
    (searchParams?.view as any) || 'cards',
  );

  const [newTitle, setNewTitle] = useState('');
  const [newStatus, setNewStatus] = useState<ADRStatus>('proposed');
  const [newContext, setNewContext] = useState('');
  const [newDecision, setNewDecision] = useState('');

  const filteredADRs = useMemo(() => {
    const filtered = adrs.filter((adr: ADR) => {
      const matchesStatus = statusFilter === 'all' || adr.status === statusFilter;
      const matchesQuery =
        adr.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        adr.adrNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (adr.context?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);

      if (!matchesStatus || !matchesQuery) return false;

      // Date range filtering
      if (dateRange !== 'all' && adr.date) {
        const adrDate = new Date(adr.date);
        const now = new Date();
        const daysAgo =
          dateRange === 'week' ? 7 : dateRange === 'month' ? 30 : dateRange === 'quarter' ? 90 : 0;

        const cutoffDate = new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000);
        if (adrDate < cutoffDate) return false;
      }

      return true;
    });

    return filtered.toSorted((a: ADR, b: ADR) => {
      const dateA = a.date ? new Date(a.date).getTime() : 0;
      const dateB = b.date ? new Date(b.date).getTime() : 0;
      return dateB - dateA;
    });
  }, [adrs, statusFilter, searchQuery, dateRange]);

  const handleCreate = async () => {
    if (!newTitle.trim()) {
      toast.error('Title is required');
      return;
    }
    try {
      await createADR.mutateAsync({
        projectId,
        title: newTitle,
        context: newContext,
        decision: newDecision,
        consequences: '', // Required by CreateADRData
      });
      toast.success('ADR created successfully');
      setNewTitle('');
      setNewContext('');
      setNewDecision('');
      setNewStatus('proposed');
      setShowCreateModal(false);
    } catch {
      toast.error('Failed to create ADR');
    }
  };

  const statusCounts = useMemo(() => {
    const counts = {
      all: filteredADRs.length,
      proposed: filteredADRs.filter((a: ADR) => a.status === 'proposed').length,
      accepted: filteredADRs.filter((a: ADR) => a.status === 'accepted').length,
      deprecated: filteredADRs.filter((a: ADR) => a.status === 'deprecated').length,
      superseded: filteredADRs.filter((a: ADR) => a.status === 'superseded').length,
      rejected: filteredADRs.filter((a: ADR) => a.status === 'rejected').length,
    };
    return counts;
  }, [filteredADRs]);

  if (isLoading) {
    return (
      <div className='animate-pulse space-y-8 p-6'>
        <Skeleton className='h-10 w-48' />
        <div className='space-y-4'>
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className='h-32 w-full rounded-xl' />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className='animate-in fade-in mx-auto max-w-[1600px] space-y-8 p-6 pb-20 duration-500'>
      {/* Header */}
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-2xl font-black tracking-tight uppercase'>
            Architecture Decision Records
          </h1>
          <p className='text-muted-foreground text-sm font-medium'>
            Track architectural decisions and their compliance status.
          </p>
        </div>
        <Button
          size='sm'
          onClick={() => setShowCreateModal(true)}
          className='shadow-primary/20 gap-2 rounded-xl shadow-lg'
        >
          <Plus className='h-4 w-4' /> New ADR
        </Button>
      </div>

      {/* Filters Bar */}
      <Card className='bg-muted/30 flex flex-wrap items-center gap-3 rounded-2xl border-none p-3'>
        <div className='relative min-w-[250px] flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <Input
            placeholder='Search by title, number, or context...'
            className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className='bg-border/50 hidden h-6 w-px md:block' />

        <Select value={statusFilter} onValueChange={(v) => setStatusFilter(v as ADRStatus | 'all')}>
          <SelectTrigger className='hover:bg-background/50 h-10 w-[160px] border-none bg-transparent'>
            <div className='flex items-center gap-2'>
              <Filter className='text-muted-foreground h-3.5 w-3.5' />
              <SelectValue placeholder='Status' />
            </div>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='all'>All Statuses ({statusCounts.all})</SelectItem>
            <SelectItem value='proposed'>Proposed ({statusCounts.proposed})</SelectItem>
            <SelectItem value='accepted'>Accepted ({statusCounts.accepted})</SelectItem>
            <SelectItem value='deprecated'>Deprecated ({statusCounts.deprecated})</SelectItem>
            <SelectItem value='superseded'>Superseded ({statusCounts.superseded})</SelectItem>
            <SelectItem value='rejected'>Rejected ({statusCounts.rejected})</SelectItem>
          </SelectContent>
        </Select>

        <Select
          value={dateRange}
          onValueChange={(v) => setDateRange(v as 'all' | 'week' | 'month' | 'quarter')}
        >
          <SelectTrigger className='hover:bg-background/50 h-10 w-[140px] border-none bg-transparent'>
            <div className='flex items-center gap-2'>
              <Calendar className='text-muted-foreground h-3.5 w-3.5' />
              <SelectValue placeholder='Date' />
            </div>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='all'>Any Time</SelectItem>
            <SelectItem value='week'>This Week</SelectItem>
            <SelectItem value='month'>This Month</SelectItem>
            <SelectItem value='quarter'>This Quarter</SelectItem>
          </SelectContent>
        </Select>
      </Card>

      {/* View Mode Tabs */}
      <Tabs value={viewMode} onValueChange={(v: any) => setViewMode(v)}>
        <TabsList className='border-border/50 h-auto w-full justify-start rounded-none border-b bg-transparent p-0'>
          <TabsTrigger
            value='cards'
            className='data-[state=active]:border-primary rounded-none data-[state=active]:border-b-2'
          >
            <TrendingUp className='mr-2 h-4 w-4' />
            Cards
          </TabsTrigger>
          <TabsTrigger
            value='timeline'
            className='data-[state=active]:border-primary rounded-none data-[state=active]:border-b-2'
          >
            <Clock className='mr-2 h-4 w-4' />
            Timeline
          </TabsTrigger>
          <TabsTrigger
            value='graph'
            className='data-[state=active]:border-primary rounded-none data-[state=active]:border-b-2'
          >
            <Zap className='mr-2 h-4 w-4' />
            Graph
          </TabsTrigger>
        </TabsList>

        <TabsContent value='cards' className='mt-6'>
          {filteredADRs.length > 0 ? (
            <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
              {filteredADRs.map((adr: ADR) => (
                <button
                  key={adr.id}
                  onClick={() =>
                    navigate({
                      to: '/projects/$projectId/adrs/$adrId',
                      params: { projectId, adrId: adr.id },
                    })
                  }
                  className='text-left'
                >
                  <ADRCard adr={adr} showComplianceGauge={true} />
                </button>
              ))}
            </div>
          ) : (
            <Card className='bg-muted/20 border-none py-12'>
              <div className='text-muted-foreground/40 flex flex-col items-center justify-center'>
                <Zap className='mb-4 h-12 w-12' />
                <p className='text-sm font-medium'>No ADRs found</p>
                <p className='text-muted-foreground/50 text-xs'>
                  Create your first ADR to get started
                </p>
              </div>
            </Card>
          )}
        </TabsContent>

        <TabsContent value='timeline' className='mt-6'>
          {filteredADRs.length > 0 ? (
            <Card className='bg-card/50 rounded-2xl border-none'>
              <ADRTimeline
                adrs={filteredADRs}
                onADRClick={(adr) =>
                  navigate({
                    to: '/projects/$projectId/adrs/$adrId',
                    params: { projectId, adrId: adr.id },
                  })
                }
              />
            </Card>
          ) : (
            <Card className='bg-muted/20 border-none py-12'>
              <div className='text-muted-foreground/40 flex flex-col items-center justify-center'>
                <Clock className='mb-4 h-12 w-12' />
                <p className='text-sm font-medium'>No timeline data</p>
              </div>
            </Card>
          )}
        </TabsContent>

        <TabsContent value='graph' className='mt-6'>
          {filteredADRs.length > 0 ? (
            <Card className='bg-card/50 h-[600px] rounded-2xl border-none'>
              <ADRGraph adrs={filteredADRs} />
            </Card>
          ) : (
            <Card className='bg-muted/20 border-none py-12'>
              <div className='text-muted-foreground/40 flex flex-col items-center justify-center'>
                <Zap className='mb-4 h-12 w-12' />
                <p className='text-sm font-medium'>No graph data</p>
              </div>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Create Modal */}
      {showCreateModal && (
        <div className='fixed inset-0 z-50 flex items-center justify-center'>
          <div
            className='fixed inset-0 bg-black/50 backdrop-blur-sm'
            onClick={() => setShowCreateModal(false)}
          />
          <div
            className='bg-background relative w-full max-w-2xl rounded-xl border p-6 shadow-2xl'
            role='dialog'
            aria-modal='true'
            aria-labelledby='create-adr-title'
          >
            <div className='mb-6 flex items-center justify-between'>
              <h2 id='create-adr-title' className='text-lg font-semibold'>
                Create New ADR
              </h2>
              <button
                type='button'
                onClick={() => setShowCreateModal(false)}
                aria-label='Close dialog'
                className='hover:bg-accent rounded-lg p-1'
              >
                ✕
              </button>
            </div>

            <div className='space-y-4'>
              <div>
                <label className='mb-1 block text-sm font-medium'>Title</label>
                <Input
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder='e.g., Use PostgreSQL for persistence'
                  className='h-10'
                />
              </div>

              <div className='grid gap-4 sm:grid-cols-2'>
                <div>
                  <label className='mb-1 block text-sm font-medium'>Status</label>
                  <Select value={newStatus} onValueChange={(v) => setNewStatus(v as ADRStatus)}>
                    <SelectTrigger className='h-10'>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value='proposed'>Proposed</SelectItem>
                      <SelectItem value='accepted'>Accepted</SelectItem>
                      <SelectItem value='deprecated'>Deprecated</SelectItem>
                      <SelectItem value='superseded'>Superseded</SelectItem>
                      <SelectItem value='rejected'>Rejected</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <label className='mb-1 block text-sm font-medium'>Context</label>
                <textarea
                  value={newContext}
                  onChange={(e) => setNewContext(e.target.value)}
                  placeholder='Describe the issue or context that led to this decision...'
                  className='border-input bg-background h-24 w-full rounded-lg border px-3 py-2'
                />
              </div>

              <div>
                <label className='mb-1 block text-sm font-medium'>Decision</label>
                <textarea
                  value={newDecision}
                  onChange={(e) => setNewDecision(e.target.value)}
                  placeholder='Describe the decision that was made...'
                  className='border-input bg-background h-24 w-full rounded-lg border px-3 py-2'
                />
              </div>

              <div className='flex justify-end gap-2 pt-4'>
                <Button variant='ghost' onClick={() => setShowCreateModal(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreate} disabled={createADR.isPending || !newTitle.trim()}>
                  {createADR.isPending ? 'Creating...' : 'Create ADR'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
/* eslint-enable
  import/no-default-export,
  import/no-named-export,
  import/max-dependencies,
  eslint/prefer-default-export,
  eslint/func-style,
  eslint/curly,
  eslint/id-length,
  eslint/max-lines,
  eslint/curly,
  eslint/id-length,
  eslint/max-lines,
  eslint/max-lines-per-function,
  eslint/max-statements,
  eslint/no-inline-comments,
  eslint/no-magic-numbers,
  eslint/no-nested-ternary,
  eslint/no-ternary,
  eslint/sort-imports,
  eslint/sort-keys,
  typescript-eslint/explicit-function-return-type,
  typescript-eslint/explicit-module-boundary-types,
  typescript-eslint/no-explicit-any,
  eslint-plugin-react/button-has-type,
  eslint-plugin-react-hooks/exhaustive-deps,
  eslint-plugin-react/jsx-boolean-value,
  eslint-plugin-react/jsx-filename-extension,
  eslint-plugin-react/jsx-max-depth,
  eslint-plugin-react-perf/jsx-no-new-function-as-prop,
  eslint-plugin-jsx-a11y/click-events-have-key-events,
  eslint-plugin-jsx-a11y/label-has-associated-control,
  oxc/no-async-await,
  oxc/no-optional-chaining
 */
/* eslint-disable-next-line max-lines */
