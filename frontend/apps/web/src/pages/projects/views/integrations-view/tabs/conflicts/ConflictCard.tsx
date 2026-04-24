import type { ReactElement } from 'react';

import { useCallback } from 'react';

import type { SyncConflict } from '@tracertm/types';

import { useResolveConflict } from '@/hooks/useIntegrations';
import StatusBadge from '@/pages/projects/views/integrations-view/components/StatusBadge';

const JSON_INDENT_SPACES = 2;

function formatDateTime(value: string | undefined): string | undefined {
  if (value === undefined) {
    return undefined;
  }
  return new Date(value).toLocaleString();
}

function conflictTitle(conflict: SyncConflict): string {
  let title = `${conflict.conflictType} conflict`;
  if (conflict.fieldName !== undefined && conflict.fieldName !== '') {
    title = `${title} - ${conflict.fieldName}`;
  }
  return title;
}

function renderConflictValue({
  label,
  value,
  modifiedAt,
  className,
}: {
  label: string;
  value: unknown;
  modifiedAt: string | undefined;
  className: string;
}): ReactElement {
  const modifiedAtText = formatDateTime(modifiedAt);

  return (
    <div className={className}>
      <div className='text-sm font-medium'>{label}</div>
      <div className='mt-1 font-mono text-sm'>
        {JSON.stringify(value, undefined, JSON_INDENT_SPACES)}
      </div>
      {modifiedAtText !== undefined && (
        <div className='mt-2 text-xs text-gray-500'>Modified: {modifiedAtText}</div>
      )}
    </div>
  );
}

interface ConflictCardProps {
  conflict: SyncConflict;
}

export default function ConflictCard({ conflict }: ConflictCardProps): ReactElement {
  const resolveConflict = useResolveConflict();

  const resolveLocal = useCallback(() => {
    resolveConflict.mutate({ conflictId: conflict.id, resolution: 'local' });
  }, [conflict.id, resolveConflict]);

  const resolveExternal = useCallback(() => {
    resolveConflict.mutate({ conflictId: conflict.id, resolution: 'external' });
  }, [conflict.id, resolveConflict]);

  const resolveSkip = useCallback(() => {
    resolveConflict.mutate({ conflictId: conflict.id, resolution: 'skip' });
  }, [conflict.id, resolveConflict]);

  return (
    <div className='rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800'>
      <div className='mb-4 flex items-center justify-between'>
        <div>
          <div className='font-medium'>{conflictTitle(conflict)}</div>
          <div className='text-sm text-gray-500'>Provider: {conflict.provider}</div>
        </div>
        <StatusBadge status={conflict.status} />
      </div>

      <div className='mb-4 grid grid-cols-2 gap-4'>
        {renderConflictValue({
          label: 'Local Value',
          value: conflict.localValue,
          modifiedAt: conflict.localModifiedAt,
          className: 'rounded bg-blue-50 p-3 dark:bg-blue-900/20',
        })}
        {renderConflictValue({
          label: 'External Value',
          value: conflict.externalValue,
          modifiedAt: conflict.externalModifiedAt,
          className: 'rounded bg-purple-50 p-3 dark:bg-purple-900/20',
        })}
      </div>

      <div className='flex space-x-2'>
        <button
          type='button'
          onClick={resolveLocal}
          disabled={resolveConflict.isPending}
          className='rounded bg-blue-100 px-3 py-1 text-sm text-blue-700 hover:bg-blue-200'
        >
          Use Local
        </button>
        <button
          type='button'
          onClick={resolveExternal}
          disabled={resolveConflict.isPending}
          className='rounded bg-purple-100 px-3 py-1 text-sm text-purple-700 hover:bg-purple-200'
        >
          Use External
        </button>
        <button
          type='button'
          onClick={resolveSkip}
          disabled={resolveConflict.isPending}
          className='rounded bg-gray-100 px-3 py-1 text-sm text-gray-700 hover:bg-gray-200'
        >
          Skip
        </button>
      </div>
    </div>
  );
}
