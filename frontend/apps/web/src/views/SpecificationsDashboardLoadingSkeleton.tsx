import { Skeleton } from '@tracertm/ui';

const SKELETON_KEYS = ['a', 'b', 'c', 'd'] as const;

export function SpecificationsDashboardLoadingSkeleton(): JSX.Element {
  return (
    <div className='mx-auto max-w-[1600px] animate-pulse space-y-8 p-6'>
      <Skeleton className='h-10 w-48' />
      <div className='grid gap-4 md:grid-cols-4'>
        {SKELETON_KEYS.map((key) => (
          <Skeleton key={key} className='h-32 rounded-xl' />
        ))}
      </div>
      <Skeleton className='h-96 w-full rounded-xl' />
    </div>
  );
}
