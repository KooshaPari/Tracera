import type { ReactElement } from 'react';

import { useCallback } from 'react';

import type { IntegrationMapping } from '@tracertm/types';

import { useTriggerSync } from '@/hooks/useIntegrations';
import StatusBadge from '@/pages/projects/views/integrations-view/components/StatusBadge';

const ID_PREVIEW_LENGTH = 8;

function directionSymbol(direction: string | undefined): string {
  if (direction === 'bidirectional') {
    return '<->';
  }
  return '->';
}

function externalLabel({
  externalId,
  externalKey,
}: {
  externalId: string;
  externalKey: string | undefined;
}): string {
  if (externalKey !== undefined && externalKey !== '') {
    return externalKey;
  }
  return externalId;
}

interface MappingRowProps {
  mapping: IntegrationMapping;
}

export default function MappingRow({ mapping }: MappingRowProps): ReactElement {
  const triggerSync = useTriggerSync();
  const {
    direction,
    externalId,
    externalKey,
    externalType,
    externalUrl,
    id,
    localItemId,
    localItemType,
    provider,
    status,
  } = mapping;

  const handleSync = useCallback(() => {
    triggerSync.mutate({ direction: 'pull', mappingId: id });
  }, [id, triggerSync]);

  const localIdPreview = `${localItemId.slice(0, ID_PREVIEW_LENGTH)}...`;

  return (
    <div className='rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800'>
      <div className='flex items-center justify-between'>
        <div>
          <div className='flex items-center space-x-2'>
            <span className='font-medium'>{localItemType}</span>
            <span className='text-gray-400'>{directionSymbol(direction)}</span>
            <span className='font-medium capitalize'>
              {provider} {externalType}
            </span>
          </div>
          <div className='mt-1 text-sm text-gray-500'>
            Local: {localIdPreview} | External: {externalLabel({ externalId, externalKey })}
          </div>
          {externalUrl !== undefined && externalUrl !== '' && (
            <a
              href={externalUrl}
              target='_blank'
              rel='noopener noreferrer'
              className='text-sm text-blue-500 hover:underline'
            >
              View external
            </a>
          )}
        </div>
        <div className='flex items-center space-x-2'>
          <StatusBadge status={status} />
          <button
            type='button'
            onClick={handleSync}
            disabled={triggerSync.isPending}
            className='rounded bg-green-100 px-3 py-1 text-sm text-green-700 hover:bg-green-200'
          >
            Sync
          </button>
        </div>
      </div>
    </div>
  );
}
