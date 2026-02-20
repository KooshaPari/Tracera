import type { ReactElement } from 'react';

import type { MappingFormState } from '@/pages/projects/views/integrations-view/tabs/mappings/useMappingFormState';

import MappingControls from '@/pages/projects/views/integrations-view/tabs/mappings/MappingControls';
import MappingSources from '@/pages/projects/views/integrations-view/tabs/mappings/MappingSources';

interface MappingFormProps {
  formState: MappingFormState;
}

function renderError(message: string | undefined): ReactElement | undefined {
  if (message === undefined) {
    return undefined;
  }
  if (message === '') {
    return undefined;
  }
  return <div className='text-sm text-red-600'>{message}</div>;
}

export default function MappingForm({ formState }: MappingFormProps): ReactElement {
  return (
    <div className='space-y-4 rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800'>
      <div>
        <h2 className='text-lg font-semibold'>Link external repo/project</h2>
        <p className='text-sm text-gray-500'>
          Attach this project to an external repository or planning system to enable sync.
        </p>
      </div>
      <MappingControls formState={formState} />
      {renderError(formState.errorMessage)}
      <MappingSources formState={formState} />
    </div>
  );
}
