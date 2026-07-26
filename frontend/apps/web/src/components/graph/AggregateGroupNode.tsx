// Aggregate Group Node Component
// Renders aggregated items as a single expandable node
// Supports expanding/collapsing with animated transitions

import type { NodeProps } from '@xyflow/react';

import { Handle, Position } from '@xyflow/react';
import { ChevronDown, ChevronRight, Grid2X2, Maximize2, Minimize2 } from 'lucide-react';
import { memo, useCallback } from 'react';

import type { Item } from '@tracertm/types';

import { logger } from '@/lib/logger';
import { cn } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';

import type { AggregateGroup } from '../../utils/aggregation';

import { getTypeColor } from './utils/typeStyles';

/**
 * Data structure for aggregate group node
 */
export interface AggregateNodeData {
  group: AggregateGroup;
  items: Item[];
  isExpanded: boolean;
  onToggle: (groupId: string) => void;
  onItemSelect?: (itemId: string) => void;
}

/**
 * Type guard to validate AggregateNodeData structure
 */
function isAggregateNodeData(data: unknown): data is AggregateNodeData {
  if (typeof data !== 'object' || data === null) {
    return false;
  }

  const obj = data as Record<string, unknown>;

  // Validate group property
  if (
    typeof obj['group'] !== 'object' ||
    obj['group'] === null ||
    typeof (obj['group'] as Record<string, unknown>)['id'] !== 'string'
  ) {
    return false;
  }

  // Validate items array
  if (!Array.isArray(obj['items'])) {
    return false;
  }

  // Validate isExpanded boolean
  if (typeof obj['isExpanded'] !== 'boolean') {
    return false;
  }

  // Validate onToggle function
  if (typeof obj['onToggle'] !== 'function') {
    return false;
  }

  return true;
}

/**
 * Collapsed view of aggregate group
 */
function CollapsedGroupView({ data, onToggle }: { data: AggregateNodeData; onToggle: () => void }) {
  const typeColor = getTypeColor(data.group.type);

  return (
    <div
      className={cn(
        'px-4 py-3 rounded-lg border-2 bg-background',
        'hover:shadow-lg hover:border-primary/60 transition-all cursor-pointer',
        'flex items-center gap-3 min-w-[200px] max-w-[280px]',
      )}
      style={{ borderColor: `${typeColor}40` }}
      onClick={onToggle}
    >
      {/* Icon and type */}
      <div
        className='flex h-8 w-8 shrink-0 items-center justify-center rounded-md'
        style={{ backgroundColor: `${typeColor}20` }}
      >
        <Grid2X2 className='h-4 w-4' style={{ color: typeColor }} />
      </div>

      {/* Text content */}
      <div className='min-w-0 flex-1'>
        <div className='truncate text-sm font-semibold'>{data.group.type}</div>
        <div className='text-muted-foreground truncate text-xs'>{data.group.itemCount} items</div>
      </div>

      {/* Count badge */}
      <Badge className='shrink-0 text-white' style={{ backgroundColor: typeColor }}>
        {data.group.itemCount}
      </Badge>

      {/* Expand icon */}
      <ChevronRight className='text-muted-foreground h-4 w-4 shrink-0' />
    </div>
  );
}

/**
 * Preview/expanded view of aggregate group
 */
function ExpandedGroupView({ data, onToggle }: { data: AggregateNodeData; onToggle: () => void }) {
  const typeColor = getTypeColor(data.group.type);

  return (
    <Card
      className='w-[360px] overflow-hidden border-2 shadow-xl'
      style={{ borderColor: typeColor }}
    >
      {/* Header */}
      <div
        className='border-b p-4'
        style={{
          background: `linear-gradient(to right, ${typeColor}15, ${typeColor}05)`,
        }}
      >
        <div className='mb-2 flex items-center justify-between'>
          <div className='flex min-w-0 flex-1 items-center gap-3'>
            <div
              className='flex h-10 w-10 shrink-0 items-center justify-center rounded-lg'
              style={{ backgroundColor: `${typeColor}25` }}
            >
              <Grid2X2 className='h-5 w-5' style={{ color: typeColor }} />
            </div>
            <div className='min-w-0'>
              <h3 className='truncate text-base font-bold capitalize'>{data.group.type}</h3>
              <Badge variant='outline' className='mt-1 text-[10px]'>
                Aggregated
              </Badge>
            </div>
          </div>
          <Button variant='ghost' size='sm' className='h-8 w-8 shrink-0 p-0' onClick={onToggle}>
            <Minimize2 className='h-4 w-4' />
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className='bg-muted/20 grid grid-cols-3 gap-2 border-b px-4 py-3'>
        <div className='text-center'>
          <div className='text-2xl font-bold' style={{ color: typeColor }}>
            {data.group.itemCount}
          </div>
          <div className='text-muted-foreground text-xs'>Items</div>
        </div>
        <div className='text-center'>
          <div className='text-2xl font-bold text-blue-500'>
            {data.group.commonDependencies.length}
          </div>
          <div className='text-muted-foreground text-xs'>Common deps</div>
        </div>
        <div className='text-center'>
          <div className='text-2xl font-bold text-green-500'>
            {data.group.commonDependents.length}
          </div>
          <div className='text-muted-foreground text-xs'>Dependents</div>
        </div>
      </div>

      {/* Items list */}
      <div className='max-h-[300px] overflow-y-auto'>
        <div className='space-y-2 p-3'>
          {data.items.slice(0, 15).map((item) => (
            <div
              key={item.id}
              className={cn(
                'p-2 rounded-md border bg-card text-sm hover:bg-accent transition-colors',
                'truncate cursor-pointer text-xs',
              )}
              onClick={() => data.onItemSelect?.(item.id)}
              title={item.title}
            >
              <div className='text-foreground truncate font-medium'>{item.title}</div>
              {item.description && (
                <div className='text-muted-foreground truncate text-[10px]'>{item.description}</div>
              )}
            </div>
          ))}
          {data.items.length > 15 && (
            <div className='text-muted-foreground p-2 text-center text-xs'>
              +{data.items.length - 15} more items
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className='bg-muted/30 flex gap-2 border-t p-3'>
        <Button variant='secondary' size='sm' className='flex-1 text-xs' onClick={onToggle}>
          <ChevronDown className='mr-1 h-3 w-3' />
          Collapse
        </Button>
        <Button variant='outline' size='sm' className='flex-1 text-xs'>
          <Maximize2 className='mr-1 h-3 w-3' />
          Drill down
        </Button>
      </div>
    </Card>
  );
}

/**
 * Aggregate group node component
 */
function AggregateGroupNodeComponent({ data: nodeData, selected }: NodeProps) {
  const handleToggle = useCallback(() => {
    if (isAggregateNodeData(nodeData)) {
      nodeData.onToggle(nodeData.group.id);
    }
  }, [nodeData]);

  if (!isAggregateNodeData(nodeData)) {
    logger.error('Invalid AggregateNodeData structure:', nodeData);
    return null;
  }

  const data = nodeData;

  return (
    <div
      className={cn(
        'relative transition-all',
        selected && 'ring-2 ring-primary ring-offset-2 rounded-lg',
      )}
    >
      {/* Connection handles */}
      <Handle
        type='target'
        position={Position.Left}
        className='!bg-primary !border-background !h-3 !w-3 !border-2'
      />
      <Handle
        type='source'
        position={Position.Right}
        className='!bg-primary !border-background !h-3 !w-3 !border-2'
      />

      {/* Render based on expansion state */}
      {data.isExpanded ? (
        <ExpandedGroupView data={data} onToggle={handleToggle} />
      ) : (
        <CollapsedGroupView data={data} onToggle={handleToggle} />
      )}
    </div>
  );
}

export const AggregateGroupNode = memo(AggregateGroupNodeComponent);
