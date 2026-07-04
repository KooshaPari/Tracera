import type { ReactElement } from 'react';

import type { IntegrationMapping } from '@tracertm/types';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';
import MappingForm from '@/pages/projects/views/integrations-view/tabs/mappings/MappingForm';
import MappingList from '@/pages/projects/views/integrations-view/tabs/mappings/MappingList';
import { useMappingFormState } from '@/pages/projects/views/integrations-view/tabs/mappings/useMappingFormState';

interface MappingsTabProps {
  mappings: IntegrationMapping[];
  isLoading: boolean;
  projectId: string;
}

export default function MappingsTab({
  mappings,
  isLoading,
  projectId,
}: MappingsTabProps): ReactElement {
  const formState = useMappingFormState(projectId);

  if (isLoading) {
    return (
      <div className='flex justify-center py-8'>
        <LoadingSpinner text='Loading mappings...' />
      </div>
    );
  }

  return (
    <div className='space-y-6'>
      <MappingForm formState={formState} />
      <MappingList mappings={mappings} />
    </div>
  );
}
