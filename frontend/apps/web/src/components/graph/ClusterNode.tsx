const MAX_CLUSTER_SIZE = 200;
/**
 * Cluster Node Component
 *
 * Specialized visualization for clustered nodes in large graphs.
 * Supports hierarchical expansion/collapse and visual cluster metrics.
 */

import type { NodeProps } from '@xyflow/react';

import { Handle, Position } from '@xyflow/react';
import { ChevronDown, ChevronRight, Layers, Maximize2, Minimize2, Network } from 'lucide-react';
import { memo, useCallback, useMemo } from 'react';

import type { Item, Link } from '@tracertm/types';

import { logger } from '@/lib/logger';
import { cn } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';

import type { ClusterNode as ClusterNodeType } from '../../lib/graphClustering';

import { getTypeColor } from './utils/typeStyles';

/**
 * Data structure for cluster node
 */
export interface ClusterNodeData {
  cluster: ClusterNodeType;
  items: Item[];
  links: Link[];
  isExpanded: boolean;
  level: number;
  onToggle: (clusterId: string) => void;
  onDrillDown?: (clusterId: string) => void;
  onItemSelect?: (itemId: string) => void;
  [key: string]: unknown;
}

/**
 * Type guard for ClusterNodeData
 */
function isClusterNodeData(data: unknown): data is ClusterNodeData {
  if (typeof data !== 'object' || data === null) {
    return false;
  }

  const obj = data as Record<string, unknown>;

  // Validate cluster property
  if (
    typeof obj['cluster'] !== 'object' ||
    obj['cluster'] === null ||
    typeof (obj['cluster'] as Record<string, unknown>)['id'] !== 'string'
  ) {
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
 * Calculate cluster visual size based on node count
 */
function getClusterSize(nodeCount: number): { width: number; height: number } {
  const baseSize = 80;
  const scaleFactor = Math.log10(nodeCount + 1) * 20;
  const size = Math.min(baseSize + scaleFactor, MAX_CLUSTER_SIZE);

  return { height: size, width: size };
}

/**
 * Collapsed cluster view
 */
function CollapsedClusterView({ data, onToggle }: { data: ClusterNodeData; onToggle: () => void }) {
  const { cluster } = data;
  const typeColor = getTypeColor(cluster.metadata.dominantType ?? 'unknown');
  const { width, height } = getClusterSize(cluster.size);

  // Calculate density metric (0-1)
  const density =
    cluster.metadata.internalEdges / Math.max((cluster.size * (cluster.size - 1)) / 2, 1);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onToggle();
      }
    },
    [onToggle],
  );

  return (
    <div
      role='button'
      tabIndex={0}
      className={cn(
        'rounded-lg border-2 bg-background/95 backdrop-blur-sm',
        'hover:shadow-xl hover:border-primary/60 transition-all cursor-pointer',
        'flex flex-col items-center justify-center gap-2 p-3',
        'relative',
      )}
      style={{
        borderColor: `${typeColor}40`,
        height,
        width,
      }}
      onClick={onToggle}
      onKeyDown={handleKeyDown}
    >
      {/* Level indicator */}
      <div className='absolute top-1 left-1'>
        <Badge
          variant='secondary'
          className='h-4 px-1 py-0 text-[10px]'
          style={{ backgroundColor: `${typeColor}20` }}
        >
          L{cluster.level}
        </Badge>
      </div>

      {/* Icon */}
      <div
        className='flex h-10 w-10 shrink-0 items-center justify-center rounded-full'
        style={{ backgroundColor: `${typeColor}25` }}
      >
        <Layers className='h-5 w-5' style={{ color: typeColor }} />
      </div>

      {/* Size badge */}
      <Badge className='font-bold text-white' style={{ backgroundColor: typeColor }}>
        {cluster.size}
      </Badge>

      {/* Type label */}
      <div
        className='max-w-full truncate px-1 text-center text-xs font-semibold'
        style={{ color: typeColor }}
      >
        {cluster.metadata.dominantType}
      </div>

      {/* Density indicator */}
      <div className='bg-muted h-1 w-full overflow-hidden rounded-full'>
        <div
          className='h-full transition-all'
          style={{
            backgroundColor: typeColor,
            width: `${density * 100}%`,
          }}
        />
      </div>

      {/* Expand icon */}
      <ChevronRight className='text-muted-foreground absolute right-1 bottom-1 h-3 w-3' />
    </div>
  );
}

/**
 * Expanded cluster view with metrics and preview
 */
function ExpandedClusterView({ data, onToggle }: { data: ClusterNodeData; onToggle: () => void }) {
  const { cluster, items } = data;
  const typeColor = getTypeColor(cluster.metadata.dominantType ?? 'unknown');

  // Calculate additional metrics
  const totalEdges = cluster.metadata.internalEdges + cluster.metadata.externalEdges;
  const cohesion = totalEdges > 0 ? cluster.metadata.internalEdges / totalEdges : 0;

  // Get type distribution entries sorted by count
  const typeEntries = Object.entries(cluster.metadata.typeDistribution).toSorted(
    (a, b) => b[1] - a[1],
  );

  return (
    <Card
      className='w-[400px] overflow-hidden border-2 shadow-2xl'
      style={{ borderColor: typeColor }}
    >
      {/* Header */}
      <div
        className='border-b p-4'
        style={{
          background: `linear-gradient(135deg, ${typeColor}20, ${typeColor}05)`,
        }}
      >
        <div className='mb-3 flex items-center justify-between'>
          <div className='flex min-w-0 flex-1 items-center gap-3'>
            <div
              className='flex h-12 w-12 shrink-0 items-center justify-center rounded-xl'
              style={{ backgroundColor: `${typeColor}30` }}
            >
              <Network className='h-6 w-6' style={{ color: typeColor }} />
            </div>
            <div className='min-w-0'>
              <h3 className='text-base font-bold'>Cluster {cluster.id.split('-').pop()}</h3>
              <div className='mt-1 flex items-center gap-2'>
                <Badge variant='outline' className='text-[10px]'>
                  Level {cluster.level}
                </Badge>
                <Badge
                  variant='outline'
                  className='text-[10px]'
                  style={{ borderColor: typeColor, color: typeColor }}
                >
                  {cluster.metadata.dominantType}
                </Badge>
              </div>
            </div>
          </div>
          <Button variant='ghost' size='sm' className='h-8 w-8 shrink-0 p-0' onClick={onToggle}>
            <Minimize2 className='h-4 w-4' />
          </Button>
        </div>
      </div>

      {/* Metrics */}
      <div className='bg-muted/20 border-b px-4 py-3'>
        <div className='mb-3 grid grid-cols-4 gap-3'>
          <div className='text-center'>
            <div className='text-2xl font-bold' style={{ color: typeColor }}>
              {cluster.size}
            </div>
            <div className='text-muted-foreground text-[10px]'>Nodes</div>
          </div>
          <div className='text-center'>
            <div className='text-2xl font-bold text-green-500'>
              {cluster.metadata.internalEdges}
            </div>
            <div className='text-muted-foreground text-[10px]'>Internal</div>
          </div>
          <div className='text-center'>
            <div className='text-2xl font-bold text-orange-500'>
              {cluster.metadata.externalEdges}
            </div>
            <div className='text-muted-foreground text-[10px]'>External</div>
          </div>
          <div className='text-center'>
            <div className='text-2xl font-bold text-blue-500'>
              {cluster.metadata.avgDegree.toFixed(1)}
            </div>
            <div className='text-muted-foreground text-[10px]'>Avg Degree</div>
          </div>
        </div>

        {/* Cohesion bar */}
        <div className='space-y-1'>
          <div className='flex items-center justify-between text-[10px]'>
            <span className='text-muted-foreground'>Cohesion</span>
            <span className='font-semibold'>{(cohesion * 100).toFixed(0)}%</span>
          </div>
          <div className='bg-muted h-2 w-full overflow-hidden rounded-full'>
            <div
              className='h-full transition-all'
              style={{
                backgroundColor:
                  cohesion > 0.7 ? '#22c55e' : cohesion > 0.4 ? '#f59e0b' : '#ef4444',
                width: `${cohesion * 100}%`,
              }}
            />
          </div>
        </div>
      </div>

      {/* Type distribution */}
      <div className='border-b px-4 py-3'>
        <div className='text-muted-foreground mb-2 text-xs font-semibold'>Type Distribution</div>
        <div className='space-y-1.5'>
          {typeEntries.slice(0, 5).map(([type, count]) => {
            const percentage = (count / cluster.size) * 100;
            const color = getTypeColor(type);
            return (
              <div key={type} className='space-y-0.5'>
                <div className='flex items-center justify-between text-[11px]'>
                  <span className='capitalize'>{type.replaceAll('_', ' ')}</span>
                  <span className='font-semibold'>{count}</span>
                </div>
                <div className='bg-muted h-1.5 w-full overflow-hidden rounded-full'>
                  <div
                    className='h-full transition-all'
                    style={{
                      backgroundColor: color,
                      width: `${percentage}%`,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Item preview */}
      <div className='max-h-[200px] overflow-y-auto'>
        <div className='space-y-1.5 p-3'>
          <div className='text-muted-foreground mb-2 text-xs font-semibold'>
            Preview ({Math.min(10, items.length)} of {items.length})
          </div>
          {items.slice(0, 10).map((item) => (
            <div
              key={item.id}
              role='button'
              tabIndex={0}
              className={cn(
                'p-2 rounded-md border bg-card text-xs hover:bg-accent transition-colors',
                'cursor-pointer truncate',
              )}
              onClick={() => data.onItemSelect?.(item.id)}
              onKeyDown={(e) => {
                if ((e.key === 'Enter' || e.key === ' ') && data.onItemSelect) {
                  e.preventDefault();
                  data.onItemSelect(item.id);
                }
              }}
              title={item.title}
            >
              <div className='truncate font-medium'>{item.title}</div>
            </div>
          ))}
          {items.length > 10 && (
            <div className='text-muted-foreground p-2 text-center text-[10px]'>
              +{items.length - 10} more items
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className='bg-muted/30 flex gap-2 border-t p-3'>
        <Button variant='secondary' size='sm' className='flex-1 text-xs' onClick={onToggle}>
          <ChevronDown className='mr-1 h-3 w-3' />
          Collapse
        </Button>
        <Button
          variant='outline'
          size='sm'
          className='flex-1 text-xs'
          onClick={() => data.onDrillDown?.(cluster.id)}
        >
          <Maximize2 className='mr-1 h-3 w-3' />
          Drill Down
        </Button>
      </div>
    </Card>
  );
}

/**
 * Cluster node component
 */
function ClusterNodeComponent({ data: nodeData, selected }: NodeProps) {
  const handleToggle = useCallback(() => {
    if (isClusterNodeData(nodeData)) {
      nodeData.onToggle(nodeData.cluster.id);
    }
  }, [nodeData]);

  if (!isClusterNodeData(nodeData)) {
    logger.error('Invalid ClusterNodeData structure:', nodeData);
    return null;
  }

  const data = nodeData;

  // Calculate handle positions based on size
  useMemo(() => getClusterSize(data.cluster.size), [data.cluster.size]);

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
      <Handle
        type='target'
        position={Position.Top}
        className='!bg-primary !border-background !h-3 !w-3 !border-2'
      />
      <Handle
        type='source'
        position={Position.Bottom}
        className='!bg-primary !border-background !h-3 !w-3 !border-2'
      />

      {/* Render based on expansion state */}
      {data.isExpanded ? (
        <ExpandedClusterView data={data} onToggle={handleToggle} />
      ) : (
        <CollapsedClusterView data={data} onToggle={handleToggle} />
      )}
    </div>
  );
}

export const ClusterNode = memo(ClusterNodeComponent);
