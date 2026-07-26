import { Skeleton } from '@tracertm/ui/components/Skeleton';

function GraphViewLoadingState(): JSX.Element {
  return (
    <div className='flex h-full'>
      <div className='w-56 space-y-2 border-r p-4'>
        <Skeleton className='h-10 w-full' />
        <Skeleton className='h-10 w-full' />
        <Skeleton className='h-10 w-full' />
      </div>
      <div className='flex-1 space-y-4 p-6'>
        <Skeleton className='h-12 w-full' />
        <Skeleton className='h-[calc(100vh-200px)]' />
      </div>
    </div>
  );
}

export { GraphViewLoadingState };
