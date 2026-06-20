// Expandable Node - Rich interactive node with progressive disclosure
// Supports: collapsed → preview → panel → full page expansion

import type { NodeProps } from '@xyflow/react';

import { Handle, Position } from '@xyflow/react';
import {
  Bot,
  ChevronRight,
  Edit3,
  ExternalLink,
  Eye,
  Layers,
  Link2,
  Maximize2,
  Minimize2,
  MoreHorizontal,
  X,
  Zap,
} from 'lucide-react';
import { memo, useCallback, useState } from 'react';

import type { Item } from '@tracertm/types';

import { logger } from '@/lib/logger';
import { cn } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { ScrollArea } from '@tracertm/ui/components/ScrollArea';
import { Separator } from '@tracertm/ui/components/Separator';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

import { getTypeColor, getTypeIcon } from '../utils/typeStyles';

// ============================================================================
// TYPES
// ============================================================================

export type NodeExpansionState = 'collapsed' | 'preview' | 'panel';

export interface ExpandableNodeData {
  item: Item;
  label: string;
  type: string;
  description?: string | undefined;
  status?: string | undefined;
  priority?: string | undefined;

  // Hierarchy info
  depth?: number | undefined;
  hasChildren?: boolean | undefined;
  childCount?: number | undefined;
  parentId?: string | undefined;
  path?: string[] | undefined;

  // Preview/visual
  thumbnailUrl?: string | undefined;
  previewComponent?: string | undefined;

  // Relationships
  incomingLinks?: number | undefined;
  outgoingLinks?: number | undefined;

  // Edit capability
  canEdit?: boolean | undefined;
  editType?: 'instant' | 'agent_required' | 'manual' | undefined;

  // State
  expansionState?: NodeExpansionState | undefined;
  isSelected?: boolean | undefined;

  // Callbacks
  onExpand?: ((nodeId: string, state: NodeExpansionState) => void) | undefined;
  onNavigate?: ((nodeId: string) => void) | undefined;
  onEdit?: ((nodeId: string) => void) | undefined;
  onViewFullPage?: ((nodeId: string) => void) | undefined;
}

// ============================================================================
// COLLAPSED NODE VIEW
// ============================================================================

interface CollapsedNodeProps {
  data: ExpandableNodeData;
  onExpand: () => void;
}

function CollapsedNodeView({ data, onExpand }: CollapsedNodeProps) {
  const TypeIcon = getTypeIcon(data.type);
  const typeColor = getTypeColor(data.type);

  return (
    <TooltipProvider>
      <Tooltip delayDuration={300}>
        <TooltipTrigger asChild>
          <div
            className={cn(
              'flex items-center gap-2 px-3 py-2 rounded-lg border-2 bg-background',
              'hover:shadow-md hover:border-primary/50 transition-all cursor-pointer',
              'min-w-[140px] max-w-[200px]',
            )}
            style={{ borderColor: `${typeColor}40` }}
            onClick={onExpand}
          >
            <div
              className='flex h-6 w-6 shrink-0 items-center justify-center rounded-md'
              style={{ backgroundColor: `${typeColor}20` }}
            >
              <TypeIcon className='h-3.5 w-3.5' style={{ color: typeColor }} />
            </div>
            <span className='flex-1 truncate text-sm font-medium'>{data.label}</span>
            {data.childCount && data.childCount > 0 && (
              <Badge variant='secondary' className='h-5 shrink-0 px-1.5 text-[10px]'>
                {data.childCount}
              </Badge>
            )}
            <ChevronRight className='text-muted-foreground h-4 w-4 shrink-0' />
          </div>
        </TooltipTrigger>
        <TooltipContent side='right' className='max-w-[280px]'>
          <div className='space-y-2'>
            <div className='flex items-center gap-2'>
              <TypeIcon className='h-4 w-4' style={{ color: typeColor }} />
              <span className='font-semibold'>{data.label}</span>
            </div>
            <Badge variant='outline' className='text-xs'>
              {data.type}
            </Badge>
            {data.description && (
              <p className='text-muted-foreground line-clamp-2 text-xs'>{data.description}</p>
            )}
            <div className='text-muted-foreground flex items-center gap-3 text-xs'>
              {data.childCount !== undefined && data.childCount > 0 && (
                <span className='flex items-center gap-1'>
                  <Layers className='h-3 w-3' /> {data.childCount} children
                </span>
              )}
              {(data.incomingLinks ?? data.outgoingLinks) && (
                <span className='flex items-center gap-1'>
                  <Link2 className='h-3 w-3' />{' '}
                  {(data.incomingLinks ?? 0) + (data.outgoingLinks ?? 0)} links
                </span>
              )}
            </div>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

// ============================================================================
// PREVIEW NODE VIEW
// ============================================================================

interface PreviewNodeProps {
  data: ExpandableNodeData;
  onCollapse: () => void;
  onExpandMore: () => void;
  onViewFullPage: () => void;
}

function PreviewNodeView({ data, onCollapse, onExpandMore, onViewFullPage }: PreviewNodeProps) {
  const TypeIcon = getTypeIcon(data.type);
  const typeColor = getTypeColor(data.type);

  return (
    <Card
      className='w-[280px] overflow-hidden border-2 shadow-lg'
      style={{ borderColor: `${typeColor}60` }}
    >
      {/* Header */}
      <div className='bg-muted/30 border-b p-3'>
        <div className='flex items-center justify-between'>
          <div className='flex min-w-0 items-center gap-2'>
            <div
              className='flex h-7 w-7 shrink-0 items-center justify-center rounded-md'
              style={{ backgroundColor: `${typeColor}20` }}
            >
              <TypeIcon className='h-4 w-4' style={{ color: typeColor }} />
            </div>
            <div className='min-w-0'>
              <h4 className='truncate text-sm font-semibold'>{data.label}</h4>
              <Badge variant='outline' className='mt-0.5 text-[10px]'>
                {data.type}
              </Badge>
            </div>
          </div>
          <div className='flex shrink-0 items-center gap-1'>
            <Button
              variant='ghost'
              size='sm'
              className='h-7 w-7 p-0'
              onClick={onExpandMore}
              title='Expand to panel'
            >
              <Maximize2 className='h-3.5 w-3.5' />
            </Button>
            <Button
              variant='ghost'
              size='sm'
              className='h-7 w-7 p-0'
              onClick={onCollapse}
              title='Collapse'
            >
              <X className='h-3.5 w-3.5' />
            </Button>
          </div>
        </div>
      </div>

      {/* Preview image/thumbnail */}
      {data.thumbnailUrl && (
        <div className='bg-muted/50 relative h-24 overflow-hidden'>
          <img src={data.thumbnailUrl} alt={data.label} className='h-full w-full object-cover' />
          <div className='from-background/80 absolute inset-0 bg-gradient-to-t to-transparent' />
        </div>
      )}

      {/* Content */}
      <div className='space-y-2 p-3'>
        {data.description && (
          <p className='text-muted-foreground line-clamp-2 text-xs'>{data.description}</p>
        )}

        {/* Stats row */}
        <div className='text-muted-foreground flex items-center gap-3 text-xs'>
          {data.status && (
            <Badge variant='secondary' className='text-[10px]'>
              {data.status}
            </Badge>
          )}
          {data.childCount !== undefined && data.childCount > 0 && (
            <span className='flex items-center gap-1'>
              <Layers className='h-3 w-3' /> {data.childCount}
            </span>
          )}
          {(data.incomingLinks !== undefined || data.outgoingLinks !== undefined) && (
            <span className='flex items-center gap-1'>
              <Link2 className='h-3 w-3' /> {(data.incomingLinks ?? 0) + (data.outgoingLinks ?? 0)}
            </span>
          )}
        </div>

        {/* Actions */}
        <div className='flex items-center gap-2 pt-1'>
          <Button
            variant='outline'
            size='sm'
            className='h-7 flex-1 text-xs'
            onClick={onViewFullPage}
          >
            <ExternalLink className='mr-1 h-3 w-3' />
            Open
          </Button>
          {data.hasChildren && (
            <Button variant='secondary' size='sm' className='h-7 text-xs' onClick={onExpandMore}>
              <Eye className='mr-1 h-3 w-3' />
              Drill down
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}

// ============================================================================
// PANEL NODE VIEW (CONTROL PANEL)
// ============================================================================

interface PanelNodeProps {
  data: ExpandableNodeData;
  onCollapse: () => void;
  onMinimize: () => void;
  onViewFullPage: () => void;
  onEdit: () => void;
}

function PanelNodeView({ data, onCollapse, onMinimize, onViewFullPage, onEdit }: PanelNodeProps) {
  const TypeIcon = getTypeIcon(data.type);
  const typeColor = getTypeColor(data.type);

  return (
    <Card
      className='w-[360px] overflow-hidden border-2 shadow-xl'
      style={{ borderColor: typeColor }}
    >
      {/* Header with gradient */}
      <div
        className='border-b p-4'
        style={{
          background: `linear-gradient(to right, ${typeColor}10, ${typeColor}05)`,
        }}
      >
        <div className='mb-2 flex items-center justify-between'>
          <div className='flex items-center gap-3'>
            <div
              className='flex h-10 w-10 items-center justify-center rounded-lg'
              style={{
                backgroundColor: `${typeColor}20`,
                border: `2px solid ${typeColor}40`,
              }}
            >
              <TypeIcon className='h-5 w-5' style={{ color: typeColor }} />
            </div>
            <div>
              <h3 className='text-base font-bold'>{data.label}</h3>
              <div className='mt-0.5 flex items-center gap-2'>
                <Badge
                  style={{
                    backgroundColor: `${typeColor}20`,
                    color: typeColor,
                  }}
                >
                  {data.type}
                </Badge>
                {data.status && (
                  <Badge variant='outline' className='text-xs'>
                    {data.status}
                  </Badge>
                )}
              </div>
            </div>
          </div>
          <div className='flex items-center gap-1'>
            <Button variant='ghost' size='sm' className='h-8 w-8 p-0' onClick={onMinimize}>
              <Minimize2 className='h-4 w-4' />
            </Button>
            <Button variant='ghost' size='sm' className='h-8 w-8 p-0' onClick={onCollapse}>
              <X className='h-4 w-4' />
            </Button>
          </div>
        </div>

        {/* Breadcrumb path */}
        {data.path && data.path.length > 0 && (
          <div className='text-muted-foreground flex items-center gap-1 overflow-x-auto text-xs'>
            {data.path.slice(-3).map((segment, i) => (
              <span key={segment} className='flex items-center gap-1'>
                {i > 0 && <ChevronRight className='h-3 w-3' />}
                <span className='max-w-[80px] truncate'>{segment}</span>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Preview area */}
      {data.thumbnailUrl ? (
        <div className='bg-muted/30 relative h-32 overflow-hidden'>
          <img src={data.thumbnailUrl} alt={data.label} className='h-full w-full object-cover' />
          <Button
            variant='secondary'
            size='sm'
            className='absolute right-2 bottom-2 h-7'
            onClick={onViewFullPage}
          >
            <Maximize2 className='mr-1 h-3 w-3' />
            Full view
          </Button>
        </div>
      ) : (
        <div className='bg-muted/30 flex h-20 items-center justify-center'>
          <TypeIcon className='text-muted-foreground/30 h-8 w-8' />
        </div>
      )}

      {/* Content */}
      <ScrollArea className='h-[200px]'>
        <div className='space-y-4 p-4'>
          {/* Description */}
          {data.description && (
            <div>
              <h4 className='text-muted-foreground mb-1 text-xs font-semibold tracking-wide uppercase'>
                Description
              </h4>
              <p className='text-sm'>{data.description}</p>
            </div>
          )}

          <Separator />

          {/* Stats grid */}
          <div className='grid grid-cols-2 gap-3'>
            <div className='bg-muted/30 rounded-lg p-2.5'>
              <div className='text-muted-foreground mb-1 flex items-center gap-1.5 text-xs'>
                <Layers className='h-3.5 w-3.5' />
                Children
              </div>
              <div className='text-lg font-bold'>{data.childCount ?? 0}</div>
            </div>
            <div className='bg-muted/30 rounded-lg p-2.5'>
              <div className='text-muted-foreground mb-1 flex items-center gap-1.5 text-xs'>
                <Link2 className='h-3.5 w-3.5' />
                Links
              </div>
              <div className='text-lg font-bold'>
                {(data.incomingLinks ?? 0) + (data.outgoingLinks ?? 0)}
              </div>
            </div>
          </div>

          {/* Hierarchy info */}
          {data.depth !== undefined && (
            <div className='flex items-center justify-between text-sm'>
              <span className='text-muted-foreground'>Depth level</span>
              <Badge variant='outline'>{data.depth}</Badge>
            </div>
          )}

          {/* Edit capability */}
          {data.canEdit && (
            <div className='bg-primary/5 border-primary/20 rounded-lg border p-3'>
              <div className='mb-2 flex items-center gap-2'>
                {data.editType === 'instant' ? (
                  <Zap className='text-primary h-4 w-4' />
                ) : data.editType === 'agent_required' ? (
                  <Bot className='text-primary h-4 w-4' />
                ) : (
                  <Edit3 className='text-primary h-4 w-4' />
                )}
                <span className='text-sm font-medium'>
                  {data.editType === 'instant'
                    ? 'Instant edit available'
                    : data.editType === 'agent_required'
                      ? 'Agent-assisted edit'
                      : 'Manual edit'}
                </span>
              </div>
              <p className='text-muted-foreground text-xs'>
                {data.editType === 'instant'
                  ? 'Changes apply immediately via automation'
                  : data.editType === 'agent_required'
                    ? 'An AI agent will help implement changes'
                    : 'Edit manually in the full editor'}
              </p>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Actions footer */}
      <div className='bg-muted/20 flex items-center gap-2 border-t p-3'>
        <Button variant='default' size='sm' className='flex-1' onClick={onViewFullPage}>
          <ExternalLink className='mr-1.5 h-4 w-4' />
          Open full page
        </Button>
        {data.canEdit && (
          <Button variant='secondary' size='sm' onClick={onEdit}>
            {data.editType === 'instant' ? (
              <Zap className='h-4 w-4' />
            ) : data.editType === 'agent_required' ? (
              <Bot className='h-4 w-4' />
            ) : (
              <Edit3 className='h-4 w-4' />
            )}
          </Button>
        )}
        <Button variant='ghost' size='sm' className='h-9 w-9 p-0'>
          <MoreHorizontal className='h-4 w-4' />
        </Button>
      </div>
    </Card>
  );
}

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Type guard to validate ExpandableNodeData structure
 */
function isExpandableNodeData(data: unknown): data is ExpandableNodeData {
  if (typeof data !== 'object' || data === null) {
    return false;
  }

  const obj = data as Record<string, unknown>;

  // Required properties
  const { item } = obj;
  if (
    typeof item !== 'object' ||
    item === null ||
    typeof (item as Record<string, unknown>)['id'] !== 'string'
  ) {
    return false;
  }

  if (typeof obj['label'] !== 'string') {
    return false;
  }

  if (typeof obj['type'] !== 'string') {
    return false;
  }

  return true;
}

// ============================================================================
// MAIN EXPANDABLE NODE
// ============================================================================

function ExpandableNodeInner({ data, selected }: { data: ExpandableNodeData; selected: boolean }) {
  const [expansionState, setExpansionState] = useState<NodeExpansionState>(
    data.expansionState ?? 'collapsed',
  );

  const handleExpand = useCallback(() => {
    setExpansionState('preview');
    data.onExpand?.(data.item.id, 'preview');
  }, [data]);

  const handleExpandMore = useCallback(() => {
    setExpansionState('panel');
    data.onExpand?.(data.item.id, 'panel');
  }, [data]);

  const handleCollapse = useCallback(() => {
    setExpansionState('collapsed');
    data.onExpand?.(data.item.id, 'collapsed');
  }, [data]);

  const handleMinimize = useCallback(() => {
    setExpansionState('preview');
    data.onExpand?.(data.item.id, 'preview');
  }, [data]);

  const handleViewFullPage = useCallback(() => {
    data.onViewFullPage?.(data.item.id);
  }, [data]);

  const handleEdit = useCallback(() => {
    data.onEdit?.(data.item.id);
  }, [data]);

  return (
    <div className={cn('relative', selected && 'ring-2 ring-primary ring-offset-2 rounded-lg')}>
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
      {expansionState === 'collapsed' && <CollapsedNodeView data={data} onExpand={handleExpand} />}

      {expansionState === 'preview' && (
        <PreviewNodeView
          data={data}
          onCollapse={handleCollapse}
          onExpandMore={handleExpandMore}
          onViewFullPage={handleViewFullPage}
        />
      )}

      {expansionState === 'panel' && (
        <PanelNodeView
          data={data}
          onCollapse={handleCollapse}
          onMinimize={handleMinimize}
          onViewFullPage={handleViewFullPage}
          onEdit={handleEdit}
        />
      )}
    </div>
  );
}

function ExpandableNodeComponent({ data: nodeData, selected }: NodeProps) {
  if (!isExpandableNodeData(nodeData)) {
    logger.error('Invalid ExpandableNodeData structure:', nodeData);
    return null;
  }
  return <ExpandableNodeInner data={nodeData} selected={selected} />;
}

export const ExpandableNode = memo(ExpandableNodeComponent);
