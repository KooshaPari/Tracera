import { useNavigate, useSearch } from '@tanstack/react-router';
import { Clock, Plus, TrendingUp, Zap } from 'lucide-react';
import { useMemo, useState } from 'react';

import type { ADR, ADRStatus } from '@tracertm/types';

import { ADRCard } from '@/components/specifications/adr/ADRCard';
import { ADRGraph } from '@/components/specifications/adr/ADRGraph';
import { ADRTimeline } from '@/components/specifications/adr/ADRTimeline';
import { useADRs, useCreateADR } from '@/hooks/useSpecifications';
import { Button, Card, Skeleton, Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui';

import { ADRCreateModal } from './adr-list-create-modal';
import { ADRListFilters } from './adr-list-filters';

interface ADRListViewProps {
  projectId: string;
}

const MILLISECONDS_PER_DAY = 86_400_000;
const DATE_RANGE_DAYS: Record<string, number> = {
  week: 7,
  month: 30,
  quarter: 90,
};

export function ADRListView({ projectId }: ADRListViewProps): React.JSX.Element {
  const navigate = useNavigate();
  const searchParams = useSearch({ strict: false });
  const { data: adrsData, isLoading } = useADRs({ projectId });
  const adrs = adrsData?.adrs ?? [];
  const createADR = useCreateADR();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<ADRStatus | 'all'>(
    (searchParams?.status as ADRStatus) ?? 'all',
  );
  const [dateRange, setDateRange] = useState<'all' | 'week' | 'month' | 'quarter'>(
    searchParams?.dateRange ?? 'all',
  );
  const [viewMode, setViewMode] = useState<'cards' | 'timeline' | 'graph'>(
    searchParams?.view ?? 'cards',
  );

  const filteredADRs = useMemo(() => {
    const filtered = adrs.filter((adr: ADR) => {
      const matchesStatus = statusFilter === 'all' || adr.status === statusFilter;
      const lowerQuery = searchQuery.toLowerCase();
      const matchesQuery =
        adr.title.toLowerCase().includes(lowerQuery) ||
        adr.adrNumber.toLowerCase().includes(lowerQuery) ||
        (adr.context?.toLowerCase().includes(lowerQuery) ?? false);

      if (!matchesStatus || !matchesQuery) return false;
      if (dateRange !== 'all' && adr.date) {
        const adrDate = new Date(adr.date);
        const daysAgo = DATE_RANGE_DAYS[dateRange] ?? 0;
        const cutoffDate = new Date(Date.now() - daysAgo * MILLISECONDS_PER_DAY);
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

  const statusCounts = useMemo(
    () => ({
      all: filteredADRs.length,
      proposed: filteredADRs.filter((a: ADR) => a.status === 'proposed').length,
      accepted: filteredADRs.filter((a: ADR) => a.status === 'accepted').length,
      deprecated: filteredADRs.filter((a: ADR) => a.status === 'deprecated').length,
      superseded: filteredADRs.filter((a: ADR) => a.status === 'superseded').length,
      rejected: filteredADRs.filter((a: ADR) => a.status === 'rejected').length,
    }),
    [filteredADRs],
  );

  if (isLoading) {
    return (
      <div className='animate-pulse space-y-8 p-6'>
        <Skeleton className='h-10 w-48' />
        <div className='space-y-4'>
          {[1, 2, 3, 4, 5].map((index) => (
            <Skeleton key={index} className='h-32 w-full rounded-xl' />
          ))}
        </div>
      </div>
    );
  }

  const navigateToAdr = async (adr: ADR): Promise<void> => {
    await navigate({
      to: '/projects/$projectId/adrs/$adrId',
      params: { projectId, adrId: adr.id },
    });
  };

  return (
    <div className='animate-in fade-in mx-auto max-w-[1600px] space-y-8 p-6 pb-20 duration-500'>
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
          type='button'
          size='sm'
          onClick={() => {
            setShowCreateModal(true);
          }}
          className='shadow-primary/20 gap-2 rounded-xl shadow-lg'
        >
          <Plus className='h-4 w-4' /> New ADR
        </Button>
      </div>

      <ADRListFilters
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        statusFilter={statusFilter}
        onStatusChange={setStatusFilter}
        dateRange={dateRange}
        onDateRangeChange={setDateRange}
        statusCounts={statusCounts}
      />

      <Tabs
        value={viewMode}
        onValueChange={(value: string) => {
          setViewMode(value as typeof viewMode);
        }}
      >
        <TabsList className='border-border/50 h-auto w-full justify-start rounded-none border-b bg-transparent p-0'>
          <TabsTrigger
            value='cards'
            className='data-[state=active]:border-primary rounded-none data-[state=active]:border-b-2'
          >
            <TrendingUp className='mr-2 h-4 w-4' /> Cards
          </TabsTrigger>
          <TabsTrigger
            value='timeline'
            className='data-[state=active]:border-primary rounded-none data-[state=active]:border-b-2'
          >
            <Clock className='mr-2 h-4 w-4' /> Timeline
          </TabsTrigger>
          <TabsTrigger
            value='graph'
            className='data-[state=active]:border-primary rounded-none data-[state=active]:border-b-2'
          >
            <Zap className='mr-2 h-4 w-4' /> Graph
          </TabsTrigger>
        </TabsList>

        <TabsContent value='cards' className='mt-6'>
          {filteredADRs.length > 0 ? (
            <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
              {filteredADRs.map((adr: ADR) => (
                <button
                  key={adr.id}
                  type='button'
                  onClick={() => {
                    void navigateToAdr(adr);
                  }}
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
                onADRClick={(adr) => {
                  void navigateToAdr(adr);
                }}
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

      {showCreateModal && (
        <ADRCreateModal
          projectId={projectId}
          createADR={createADR}
          onClose={() => {
            setShowCreateModal(false);
          }}
        />
      )}
    </div>
  );
}
