import { memo, useMemo } from 'react';

import { Skeleton } from '@tracertm/ui';

const LOADING_CARD_COUNT = 3;

export const ProjectsListLoadingState = memo(function ProjectsListLoadingState(): JSX.Element {
  const skeletonIndices = useMemo<number[]>(
    () => Array.from({ length: LOADING_CARD_COUNT }, (_, index) => index),
    [],
  );

  return (
    <div className='animate-pulse space-y-8 p-6'>
      <Skeleton className='h-10 w-48' />
      <div className='grid grid-cols-1 gap-6 md:grid-cols-3'>
        {skeletonIndices.map((index) => (
          <Skeleton key={index} className='h-64 rounded-[2rem]' />
        ))}
      </div>
    </div>
  );
});
