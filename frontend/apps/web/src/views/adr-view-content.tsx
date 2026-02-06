/* eslint-disable react/jsx-filename-extension */

import type React from 'react';

import type { ADR } from '@tracertm/types';

import { ADRCard } from '@/components/specifications/adr/ADRCard';
import { ADRTimeline } from '@/components/specifications/adr/ADRTimeline';

interface ADRViewContentProps {
  adrs: ADR[];
  viewMode: 'list' | 'timeline';
}

const ADRViewContent = ({ adrs, viewMode }: ADRViewContentProps): React.ReactElement => {
  if (viewMode === 'list') {
    return (
      <div className='grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3'>
        {adrs.map((adr) => (
          <ADRCard key={adr.id} adr={adr} />
        ))}
      </div>
    );
  }

  return <ADRTimeline adrs={adrs} />;
};

// eslint-disable-next-line import/no-default-export
export default ADRViewContent;
