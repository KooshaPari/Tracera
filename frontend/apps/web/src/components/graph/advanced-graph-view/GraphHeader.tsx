import { Network } from 'lucide-react';

import type { GraphPerspective } from '@/components/graph/types';

import { PERSPECTIVE_CONFIGS } from '@/components/graph/types';
import { Badge } from '@tracertm/ui/components/Badge';

interface GraphHeaderProps {
  connectionsCount: number;
  itemsCount: number;
  perspective: GraphPerspective;
}

export function GraphHeader({
  perspective,
  itemsCount,
  connectionsCount,
}: GraphHeaderProps): JSX.Element {
  const perspectiveConfig = PERSPECTIVE_CONFIGS.find((c) => c.id === perspective);

  return (
    <div className='flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between'>
      <div>
        <h1 className='flex items-center gap-2 text-3xl font-bold tracking-tight'>
          <Network className='h-8 w-8' />
          Traceability Graph
        </h1>
        <p className='text-muted-foreground mt-1'>
          {itemsCount} items \u00b7 {connectionsCount} connections
        </p>
      </div>

      <div className='flex items-center gap-3'>
        {perspective !== 'all' && (
          <Badge
            variant='outline'
            className='px-3 py-1'
            style={{
              backgroundColor: `${perspectiveConfig?.color}20`,
              borderColor: perspectiveConfig?.color,
            }}
          >
            {perspectiveConfig?.label}
          </Badge>
        )}
      </div>
    </div>
  );
}
