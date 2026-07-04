// Graph node loading skeleton — LOD-shaped (Phase 3, 2.1)
// Renders a loading placeholder by lodLevel: dot → minimal pill → compact pill → full pill → full node shape

import type { Node, NodeProps } from '@xyflow/react';

import { Handle, Position } from '@xyflow/react';
import { memo } from 'react';

import { Skeleton } from '@tracertm/ui/components/Skeleton';

import { LODLevel } from './utils/lod';

export interface NodeLoadingSkeletonData {
  id: string;
  lodLevel?: number;
  [key: string]: unknown;
}

const NodeLoadingSkeletonComponent = ({
  data,
}: NodeProps<Node<NodeLoadingSkeletonData, 'nodeLoading'>>) => {
  const lod = (data.lodLevel ?? LODLevel.VeryClose) as LODLevel;

  return (
    <>
      <Handle
        type='target'
        position={Position.Left}
        className='!border-muted-foreground/30 !-left-1 !h-2 !min-h-2 !w-2 !min-w-2 !border-2'
      />
      <LodLoadingShape lod={lod} />
      <Handle
        type='source'
        position={Position.Right}
        className='!border-muted-foreground/30 !-right-1 !h-2 !min-h-2 !w-2 !min-w-2 !border-2'
      />
    </>
  );
};

const LodLoadingShape = ({ lod }: { lod: LODLevel }) => {
  switch (lod) {
    case LODLevel.VeryFar: {
      return <Skeleton className='h-2 min-h-2 w-2 min-w-2 rounded-full' />;
    }
    case LODLevel.Far: {
      return <Skeleton className='h-2 w-4 min-w-[8px] rounded' />;
    }
    case LODLevel.Medium: {
      return <Skeleton className='h-5 w-16 rounded-md' />;
    }
    case LODLevel.Close: {
      return <Skeleton className='h-6 w-24 rounded-md' />;
    }
    case LODLevel.VeryClose:
    default: {
      return <Skeleton className='h-[72px] w-[180px] min-w-[180px] rounded-lg' />;
    }
  }
};

export const NodeLoadingSkeleton = memo(NodeLoadingSkeletonComponent);
