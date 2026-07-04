import type { ReactElement } from 'react';

import type { SyncConflict } from '@tracertm/types';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';
import ConflictCard from '@/pages/projects/views/integrations-view/tabs/conflicts/ConflictCard';

interface ConflictsTabProps {
  conflicts: SyncConflict[];
  isLoading: boolean;
}

export default function ConflictsTab({ conflicts, isLoading }: ConflictsTabProps): ReactElement {
  if (isLoading) {
    return (
      <div className='flex justify-center py-8'>
        <LoadingSpinner text='Loading conflicts...' />
      </div>
    );
  }

  if (conflicts.length === 0) {
    return (
      <div className='py-12 text-center text-gray-500'>
        No pending conflicts. All syncs are in harmony.
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      {conflicts.map((conflict) => (
        <ConflictCard key={conflict.id} conflict={conflict} />
      ))}
    </div>
  );
}
