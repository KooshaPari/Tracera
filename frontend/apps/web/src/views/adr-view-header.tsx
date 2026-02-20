import type React from 'react';

import { History, LayoutList, Plus } from 'lucide-react';
import { useCallback } from 'react';

import { Button, Tabs, TabsList, TabsTrigger } from '@tracertm/ui';

interface ADRViewHeaderProps {
  onCreate: () => void;
  onViewChange: (nextView: 'list' | 'timeline') => void;
  viewMode: 'list' | 'timeline';
}

const ADRViewHeader = ({
  onCreate,
  onViewChange,
  viewMode,
}: ADRViewHeaderProps): React.ReactElement => {
  const handleValueChange = useCallback(
    (nextValue: string) => {
      if (nextValue === 'list') {
        onViewChange('list');
        return;
      }

      if (nextValue === 'timeline') {
        onViewChange('timeline');
      }
    },
    [onViewChange],
  );

  return (
    <div className='flex items-center justify-between'>
      <div>
        <h1 className='text-2xl font-bold'>Architecture Decisions</h1>
        <p className='text-muted-foreground'>Log and track architectural choices (MADR 4.0).</p>
      </div>
      <div className='flex gap-2'>
        <Tabs value={viewMode} onValueChange={handleValueChange}>
          <TabsList>
            <TabsTrigger value='list'>
              <LayoutList className='h-4 w-4' />
            </TabsTrigger>
            <TabsTrigger value='timeline'>
              <History className='h-4 w-4' />
            </TabsTrigger>
          </TabsList>
        </Tabs>
        <Button onClick={onCreate}>
          <Plus className='mr-2 h-4 w-4' />
          New ADR
        </Button>
      </div>
    </div>
  );
};

export default ADRViewHeader;
