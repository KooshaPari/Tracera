import { AlertCircle, CheckCircle2, Clock, Monitor, Terminal, TrendingUp, X } from 'lucide-react';

import { useItems } from '@/hooks/useItems';
import { ItemsTableView } from '@/views/ItemsTableView';
import { Card, CardContent, CardHeader, CardTitle, Skeleton } from '@tracertm/ui';

interface MonitoringViewProps {
  projectId: string;
}

const statusConfig: Record<string, { label: string; color: string; icon: typeof CheckCircle2 }> = {
  blocked: {
    color: 'bg-red-500/10 text-red-600 border-red-500/20',
    icon: AlertCircle,
    label: 'Blocked',
  },
  cancelled: {
    color: 'bg-orange-500/10 text-orange-600 border-orange-500/20',
    icon: X,
    label: 'Cancelled',
  },
  done: {
    color: 'bg-green-500/10 text-green-600 border-green-500/20',
    icon: CheckCircle2,
    label: 'Done',
  },
  in_progress: {
    color: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
    icon: Clock,
    label: 'In progress',
  },
  todo: {
    color: 'bg-muted text-muted-foreground',
    icon: Terminal,
    label: 'To do',
  },
};

export function MonitoringView({ projectId }: MonitoringViewProps) {
  const { data, isLoading } = useItems({ projectId, view: 'monitoring' });
  const items = data?.items ?? [];
  const total = items.length;

  const byStatus = items.reduce<Record<string, number>>((acc, item) => {
    const s = item.status || 'todo';
    acc[s] = (acc[s] ?? 0) + 1;
    return acc;
  }, {});

  const criticalHigh = items.filter(
    (i) => i.priority === 'critical' || i.priority === 'high',
  ).length;

  return (
    <div className='flex h-full flex-col'>
      {/* Header */}
      <div className='shrink-0 px-6 pt-6 pb-4'>
        <div className='mb-1 flex items-center gap-3'>
          <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-teal-500/10 text-teal-600'>
            <Monitor className='h-5 w-5' />
          </div>
          <div>
            <h1 className='text-2xl font-bold tracking-tight'>Monitoring</h1>
            <p className='text-muted-foreground text-sm'>
              Observability, metrics, and monitoring items for this project
            </p>
          </div>
        </div>
      </div>

      {/* Summary cards */}
      <div className='shrink-0 px-6 pb-4'>
        <div className='grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6'>
          <Card>
            <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
              <CardTitle className='text-sm font-medium'>Total items</CardTitle>
              <Monitor className='text-muted-foreground h-4 w-4' />
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className='h-8 w-12' />
              ) : (
                <>
                  <div className='text-2xl font-bold'>{total}</div>
                  <p className='text-muted-foreground text-xs'>monitoring & performance</p>
                </>
              )}
            </CardContent>
          </Card>
          {(['done', 'in_progress', 'blocked', 'todo'] as const).map((status) => {
            const c = statusConfig[status] ?? statusConfig['todo'];
            const count = byStatus[status] ?? 0;
            const Icon = c?.icon;
            return (
              <Card key={status}>
                <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
                  <CardTitle className='text-sm font-medium'>{c?.label ?? status}</CardTitle>
                  {Icon ? <Icon className='text-muted-foreground h-4 w-4' /> : null}
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <Skeleton className='h-8 w-12' />
                  ) : (
                    <>
                      <div className='text-2xl font-bold'>{count}</div>
                      <p className='text-muted-foreground text-xs'>
                        {total > 0 ? `${Math.round((count / total) * 100)}%` : '—'}
                      </p>
                    </>
                  )}
                </CardContent>
              </Card>
            );
          })}
          <Card>
            <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
              <CardTitle className='text-sm font-medium'>Critical / High</CardTitle>
              <TrendingUp className='text-muted-foreground h-4 w-4' />
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className='h-8 w-12' />
              ) : (
                <>
                  <div className='text-2xl font-bold'>{criticalHigh}</div>
                  <p className='text-muted-foreground text-xs'>needs attention</p>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Items table */}
      <div className='min-h-0 flex-1 px-6 pb-6'>
        <ItemsTableView projectId={projectId} view='monitoring' />
      </div>
    </div>
  );
}
