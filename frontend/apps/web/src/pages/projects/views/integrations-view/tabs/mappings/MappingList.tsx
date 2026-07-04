import type { ReactElement } from 'react';

import type { IntegrationMapping } from '@tracertm/types';

import MappingRow from '@/pages/projects/views/integrations-view/tabs/mappings/MappingRow';

interface MappingListProps {
  mappings: IntegrationMapping[];
}

export default function MappingList({ mappings }: MappingListProps): ReactElement {
  if (mappings.length === 0) {
    return (
      <div className='py-12 text-center text-gray-500'>
        No mappings configured. Link a repo or project to enable sync.
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      {mappings.map((mapping) => (
        <MappingRow key={mapping.id} mapping={mapping} />
      ))}
    </div>
  );
}
