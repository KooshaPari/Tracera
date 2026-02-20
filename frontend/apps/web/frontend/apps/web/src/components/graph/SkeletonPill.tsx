import type { Node, NodeProps } from '@xyflow/react';

import { memo } from 'react';

export interface SkeletonPillData extends Record<string, unknown> {
  distance?: 'near' | 'medium' | 'far';
  state?: 'loading' | 'error';
}

export const SkeletonPill = memo(function SkeletonPill({
  data,
}: NodeProps<Node<SkeletonPillData>>) {
  const typedData = data;
  const distance = typedData.distance ?? 'near';
  const state = typedData.state ?? 'loading';

  if (state === 'error') {
    return (
      <div className='border-destructive bg-destructive/10 rounded-lg border px-3 py-2'>
        <span className='text-destructive text-xs'>Failed to load</span>
      </div>
    );
  }

  // Distance-based detail level for loading state
  if (distance === 'near') {
    return (
      <div className='bg-card animate-pulse rounded-lg border px-4 py-3'>
        <div className='bg-muted mb-2 h-4 w-24 rounded' />
        <div className='bg-muted/60 h-3 w-16 rounded' />
      </div>
    );
  } else if (distance === 'medium') {
    return (
      <div className='bg-card animate-pulse rounded-lg border px-3 py-2'>
        <div className='bg-muted h-3 w-20 rounded' />
      </div>
    );
  }
  // Far distance - minimal skeleton
  return <div className='bg-muted h-4 w-4 animate-pulse rounded-full' />;
});
