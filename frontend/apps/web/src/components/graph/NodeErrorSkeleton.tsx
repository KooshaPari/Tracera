// Graph node error skeleton — LOD-shaped (Phase 3, 2.2)
// Renders an error placeholder by lodLevel: dot → minimal pill → compact pill → full pill/card + retry

import type { Node, NodeProps } from '@xyflow/react';

import { Handle, Position } from '@xyflow/react';
import { AlertCircle } from 'lucide-react';
import { memo, useCallback } from 'react';

import { Button } from '@tracertm/ui/components/Button';

import { LODLevel } from './utils/lod';

export interface NodeErrorSkeletonData {
  id: string;
  lodLevel?: number | undefined;
  errorMessage?: string | undefined;
  onRetry?: ((id: string) => void) | undefined;
  [key: string]: unknown;
}

const NodeErrorSkeletonComponent = ({
  data,
}: NodeProps<Node<NodeErrorSkeletonData, 'nodeError'>>) => {
  const lod = (data.lodLevel ?? LODLevel.VeryClose) as LODLevel;
  const message =
    data.errorMessage ?? (typeof data['error'] === 'string' ? data['error'] : 'Error');
  const onRetryClick = useCallback(() => data.onRetry?.(data.id), [data]);

  return (
    <>
      <Handle
        type='target'
        position={Position.Left}
        className='!border-destructive/50 !-left-1 !h-2 !min-h-2 !w-2 !min-w-2 !border-2'
      />
      <LodErrorShape lod={lod} message={message} onRetryClick={onRetryClick} />
      <Handle
        type='source'
        position={Position.Right}
        className='!border-destructive/50 !-right-1 !h-2 !min-h-2 !w-2 !min-w-2 !border-2'
      />
    </>
  );
};

const LodErrorShapeFull = ({
  message,
  onRetryClick,
}: {
  message: string;
  onRetryClick?: (() => void) | undefined;
}) => (
  <div className='bg-destructive/10 border-destructive/30 text-destructive max-w-[160px] rounded-md border px-2 py-1.5 text-xs'>
    <div className='mb-1 flex items-center gap-1'>
      <AlertCircle className='h-3.5 w-3.5 shrink-0' />
      <span className='truncate font-medium'>Error</span>
    </div>
    <p className='text-muted-foreground mb-1 line-clamp-2 text-[10px]'>{message}</p>
    {onRetryClick && (
      <Button variant='outline' size='sm' className='h-5 px-1.5 text-[10px]' onClick={onRetryClick}>
        Retry
      </Button>
    )}
  </div>
);

const LodErrorShape = ({
  lod,
  message,
  onRetryClick,
}: {
  lod: LODLevel;
  message: string;
  onRetryClick?: (() => void) | undefined;
}) => {
  switch (lod) {
    case LODLevel.VeryFar: {
      return (
        <div className='bg-destructive/80 h-2 min-h-2 w-2 min-w-2 rounded-full' title={message} />
      );
    }
    case LODLevel.Far: {
      return <div className='bg-destructive/60 h-2 w-4 min-w-[8px] rounded' title={message} />;
    }
    case LODLevel.Medium: {
      return (
        <div
          className='bg-destructive/10 border-destructive/30 text-destructive flex items-center gap-0.5 rounded-md border px-1.5 py-0.5'
          title={message}
        >
          <AlertCircle className='h-3 w-3 shrink-0' />
          <span className='max-w-[60px] truncate text-[10px]'>Error</span>
        </div>
      );
    }
    case LODLevel.Close:
    case LODLevel.VeryClose:
    default: {
      return <LodErrorShapeFull message={message} onRetryClick={onRetryClick} />;
    }
  }
};

export const NodeErrorSkeleton = memo(NodeErrorSkeletonComponent);
