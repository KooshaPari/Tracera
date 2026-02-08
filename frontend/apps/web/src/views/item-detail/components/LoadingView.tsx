import { Skeleton } from '@tracertm/ui';

export function LoadingView(): JSX.Element {
  return (
    <div className='w-full animate-pulse space-y-8 px-0 py-10'>
      <Skeleton className='h-8 w-48' />
      <div className='flex items-start justify-between'>
        <div className='flex-1 space-y-4'>
          <Skeleton className='h-12 w-3/4' />
          <Skeleton className='h-6 w-1/2' />
        </div>
        <Skeleton className='h-10 w-32' />
      </div>
      <Skeleton className='h-[400px] w-full' />
    </div>
  );
}
