import { memo } from 'react';

import { Progress } from '@tracertm/ui/components/Progress';

interface LoadingProgressProps {
  loaded: number;
  total: number;
  label?: string;
}

export const LoadingProgress = memo(function LoadingProgress({
  loaded,
  total,
  label = 'Loading graph data',
}: LoadingProgressProps) {
  const PERCENT_MULTIPLIER = 100;
  const progress = total > 0 ? (loaded / total) * PERCENT_MULTIPLIER : 0;

  return (
    <div className='bg-card absolute top-4 right-4 z-50 min-w-[200px] rounded-lg border p-4 shadow-lg'>
      <div className='space-y-2'>
        <div className='flex items-center justify-between text-sm'>
          <span className='text-muted-foreground'>{label}</span>
          <span className='font-medium'>{Math.round(progress)}%</span>
        </div>
        <Progress value={progress} className='h-2' />
        <div className='text-muted-foreground text-xs'>
          {loaded.toLocaleString()} / {total.toLocaleString()} nodes
        </div>
      </div>
    </div>
  );
});
