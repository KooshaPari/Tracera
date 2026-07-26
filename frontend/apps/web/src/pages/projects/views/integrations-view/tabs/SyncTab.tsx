import type { ReactElement } from 'react';

import type { SyncLog, SyncStatusSummary } from '@tracertm/types';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';
import StatusBadge from '@/pages/projects/views/integrations-view/components/StatusBadge';

interface SyncTabProps {
  syncStatus: SyncStatusSummary | undefined;
  isLoading: boolean;
}

const EMPTY_SYNC_LOGS: SyncLog[] = [];

function formatDateTime(value: string | undefined): string | undefined {
  if (value === undefined) {
    return undefined;
  }
  return new Date(value).toLocaleString();
}

function renderQueueStat({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: 'yellow' | 'blue' | 'green' | 'red';
}): ReactElement {
  return (
    <div className='rounded bg-gray-50 p-4 text-center dark:bg-gray-700'>
      <div className={`text-2xl font-bold text-${tone}-600`}>{value}</div>
      <div className='text-sm text-gray-500'>{label}</div>
    </div>
  );
}

function renderSyncQueueStats(queue: SyncStatusSummary['queue'] | undefined): ReactElement {
  const pending = queue?.pending ?? 0;
  const processing = queue?.processing ?? 0;
  const completed = queue?.completed ?? 0;
  const failed = queue?.failed ?? 0;

  return (
    <div className='rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800'>
      <h2 className='mb-4 text-lg font-semibold'>Sync Queue</h2>
      <div className='grid grid-cols-4 gap-4'>
        {renderQueueStat({ label: 'Pending', value: pending, tone: 'yellow' })}
        {renderQueueStat({ label: 'Processing', value: processing, tone: 'blue' })}
        {renderQueueStat({ label: 'Completed', value: completed, tone: 'green' })}
        {renderQueueStat({ label: 'Failed', value: failed, tone: 'red' })}
      </div>
    </div>
  );
}

function renderRecentSyncRow(sync: SyncLog): ReactElement {
  const startedAtText = formatDateTime(sync.startedAt);
  const failedCount = sync.itemsFailed;

  return (
    <div className='flex items-center justify-between rounded bg-gray-50 p-3 dark:bg-gray-700'>
      <div>
        <div className='font-medium'>
          {sync.provider} - {sync.eventType}
        </div>
        <div className='text-sm text-gray-500'>
          {sync.itemsProcessed} items processed
          {failedCount > 0 && `, ${failedCount} failed`}
        </div>
      </div>
      <div className='text-right'>
        <StatusBadge status={sync.status} />
        {startedAtText !== undefined && (
          <div className='mt-1 text-xs text-gray-400'>{startedAtText}</div>
        )}
      </div>
    </div>
  );
}

function renderRecentSyncsList(recentSyncs: SyncLog[]): ReactElement {
  if (recentSyncs.length === 0) {
    return (
      <div className='rounded-lg border border-gray-200 bg-white p-6 text-center text-gray-500 dark:border-gray-700 dark:bg-gray-800'>
        <h2 className='mb-4 text-left text-lg font-semibold text-gray-900 dark:text-white'>
          Recent Syncs
        </h2>
        <div className='py-4'>No recent syncs</div>
      </div>
    );
  }

  return (
    <div className='rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800'>
      <h2 className='mb-4 text-lg font-semibold'>Recent Syncs</h2>
      <div className='space-y-2'>
        {recentSyncs.map((sync) => (
          <div key={sync.id}>{renderRecentSyncRow(sync)}</div>
        ))}
      </div>
    </div>
  );
}

export default function SyncTab({ syncStatus, isLoading }: SyncTabProps): ReactElement {
  if (isLoading) {
    return (
      <div className='flex justify-center py-8'>
        <LoadingSpinner text='Loading sync status...' />
      </div>
    );
  }

  const recentSyncs = syncStatus?.recentSyncs ?? EMPTY_SYNC_LOGS;

  return (
    <div className='space-y-6'>
      {renderSyncQueueStats(syncStatus?.queue)}
      {renderRecentSyncsList(recentSyncs)}
    </div>
  );
}
