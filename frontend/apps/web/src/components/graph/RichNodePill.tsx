// Rich Node Pill - Block pill with embedded UI preview and interactive widget
// Uses React Flow for custom node rendering with rich content

import type { Node, NodeProps } from '@xyflow/react';

import { Handle, NodeResizer, NodeToolbar, Position } from '@xyflow/react';
import {
  AlertCircle,
  CheckCircle2,
  Circle,
  Clock,
  Code,
  Database,
  ExternalLink,
  Eye,
  FileText,
  GitBranch,
  Image,
  Layout,
  Link2,
  Maximize2,
  Monitor,
  Shield,
  TestTube2,
  XCircle,
  Zap,
} from 'lucide-react';
import { memo, useCallback, useState } from 'react';

import type { Item, LinkType } from '@tracertm/types';

import { logger } from '@/lib/logger';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

import { NodeActions } from './NodeActions';
import { NodeContextMenu } from './NodeContextMenu';
import { NodeQuickActions } from './NodeQuickActions';
import { ENHANCED_TYPE_COLORS, STATUS_OPACITY } from './types';

// Node data structure for React Flow
export interface RichNodeData {
  id: string;
  item: Item;
  type: string;
  status: string;
  label: string;
  description?: string | undefined;

  // UI preview
  uiPreview?:
    | {
        screenshotUrl?: string | undefined;
        componentCode?: string | undefined;
        interactiveWidgetUrl?: string | undefined;
        thumbnailUrl?: string | undefined;
      }
    | undefined;

  // Connection counts
  connections: {
    incoming: number;
    outgoing: number;
    total: number;
    byType?: Record<LinkType, number>;
  };

  // Visual state
  isExpanded?: boolean | undefined;
  showPreview?: boolean | undefined;

  /** 1.3: LOD level (from determineLODLevel) for loading/error skeleton selection */
  lodLevel?: number | undefined;

  // Callbacks
  onSelect?: ((id: string) => void) | undefined;
  onExpand?: ((id: string) => void) | undefined;
  onNavigate?: ((id: string) => void) | undefined;

  // Index signature for React Flow compatibility
  [key: string]: unknown;
}

// Icon mapping
const TYPE_ICONS: Record<
  string,
  React.ComponentType<{ className?: string; style?: React.CSSProperties }>
> = {
  api: Code,
  architecture: Layout,
  bug: AlertCircle,
  code: Code,
  component: Layout,
  database: Database,
  epic: GitBranch,
  feature: Zap,
  infrastructure: Monitor,
  journey: GitBranch,
  monitoring: Monitor,
  page: Monitor,
  performance: Zap,
  requirement: FileText,
  security: Shield,
  story: FileText,
  task: Circle,
  test: TestTube2,
  test_case: TestTube2,
  ui_component: Layout,
  user_story: FileText,
  vulnerability: AlertCircle,
  wireframe: Image,
};

const STATUS_ICONS: Record<
  string,
  React.ComponentType<{ className?: string; style?: React.CSSProperties }>
> = {
  blocked: XCircle,
  cancelled: XCircle,
  completed: CheckCircle2,
  done: CheckCircle2,
  in_progress: Clock,
  pending: Circle,
  todo: Circle,
};

/** A3 perf: memoized heavy content (preview image + widget iframe) so it does not re-render on pan/zoom. */
const RichNodePillPreviewBlock = memo(function RichNodePillPreviewBlock({
  previewUrl,
  widgetUrl,
  label,
  hasWidget,
  showWidget,
  onToggleWidget,
}: {
  previewUrl: string | undefined;
  widgetUrl: string | undefined;
  label: string;
  hasWidget: boolean;
  showWidget: boolean;
  onToggleWidget: (e: React.MouseEvent) => void;
}) {
  if (!previewUrl && !hasWidget) {
    return null;
  }
  return (
    <>
      {previewUrl && (
        <div className='bg-muted/50 relative border-b'>
          <img
            src={previewUrl}
            alt={`Preview of ${label}`}
            className='h-24 w-full object-cover object-top'
            loading='lazy'
          />
          {hasWidget && (
            <Button
              variant='secondary'
              size='sm'
              className='bg-background/80 absolute right-2 bottom-2 h-6 px-2 text-[10px] backdrop-blur-sm'
              onClick={onToggleWidget}
            >
              <Eye className='mr-1 h-3 w-3' />
              Interactive
            </Button>
          )}
        </div>
      )}
      {showWidget && widgetUrl && (
        <div className='relative border-b bg-white'>
          <iframe
            src={widgetUrl}
            title={`Widget: ${label}`}
            className='h-40 w-full border-0'
            sandbox='allow-scripts allow-same-origin'
          />
          <Button
            variant='ghost'
            size='sm'
            className='absolute top-1 right-1 h-5 w-5 p-0'
            onClick={onToggleWidget}
          >
            <XCircle className='h-4 w-4' />
          </Button>
        </div>
      )}
    </>
  );
});

function RichNodePillComponent({ data, selected }: NodeProps<Node<RichNodeData, 'richPill'>>) {
  const [isHovered, setIsHovered] = useState(false);
  const [showWidget, setShowWidget] = useState(false);
  const [showActions, setShowActions] = useState(false);

  const bgColor = ENHANCED_TYPE_COLORS[data.type] ?? '#64748b';
  const opacity = STATUS_OPACITY[data.status] ?? 1;
  const TypeIcon = TYPE_ICONS[data.type] ?? FileText;
  const StatusIcon = STATUS_ICONS[data.status] ?? Circle;

  const hasPreview =
    Boolean(data.uiPreview?.screenshotUrl) || Boolean(data.uiPreview?.thumbnailUrl);
  const hasWidget = Boolean(data.uiPreview?.interactiveWidgetUrl);
  const isExpanded = data.isExpanded ?? (hasPreview && isHovered);

  const handleClick = useCallback(() => {
    data.onSelect?.(data.id);
  }, [data]);

  const handleExpand = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      data.onExpand?.(data.id);
    },
    [data],
  );

  const handleNavigate = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      data.onNavigate?.(data.id);
    },
    [data],
  );

  const toggleWidget = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      setShowWidget(!showWidget);
    },
    [showWidget],
  );

  return (
    <NodeContextMenu
      nodeId={data.id}
      nodeType={data.type}
      onCopyId={async (id) => navigator.clipboard.writeText(id)}
      onDuplicate={(id) => {
        logger.info('Duplicate:', id);
      }}
      onDelete={(id) => {
        logger.info('Delete:', id);
      }}
      onViewDetails={(id) => data.onNavigate?.(id)}
    >
      <TooltipProvider>
        {/* Node Resizer for expandable preview */}
        <NodeResizer
          minWidth={180}
          minHeight={hasPreview ? 160 : 80}
          maxWidth={400}
          maxHeight={500}
          isVisible={selected}
        />

        {/* Toolbar on selection */}
        <NodeToolbar isVisible={selected} position={Position.Top}>
          <div className='bg-background flex gap-1 rounded-lg border p-1 shadow-lg'>
            <Button variant='ghost' size='sm' className='h-7 px-2' onClick={handleNavigate}>
              <ExternalLink className='mr-1 h-3.5 w-3.5' />
              Open
            </Button>
            {hasPreview && (
              <Button variant='ghost' size='sm' className='h-7 px-2' onClick={handleExpand}>
                <Maximize2 className='mr-1 h-3.5 w-3.5' />
                Expand
              </Button>
            )}
            {hasWidget && (
              <Button variant='ghost' size='sm' className='h-7 px-2' onClick={toggleWidget}>
                <Eye className='mr-1 h-3.5 w-3.5' />
                {showWidget ? 'Hide' : 'Preview'}
              </Button>
            )}
          </div>
        </NodeToolbar>

        {/* Input handle */}
        <Handle
          type='target'
          position={Position.Left}
          className='!bg-background !h-3 !w-3 !border-2'
          style={{ borderColor: bgColor }}
        />

        {/* Main pill container */}
        <Card
          className={`group relative cursor-pointer overflow-hidden transition-all duration-200 ${selected ? 'ring-offset-background ring-2 ring-white ring-offset-2' : ''} ${isHovered ? 'scale-[1.02] shadow-lg' : 'shadow-md'} `}
          style={{
            maxWidth: isExpanded ? 350 : 220,
            minWidth: 180,
            opacity,
          }}
          onMouseEnter={() => {
            setIsHovered(true);
            setShowActions(true);
          }}
          onMouseLeave={() => {
            setIsHovered(false);
            setShowActions(false);
          }}
          onClick={handleClick}
        >
          {/* Color accent bar */}
          <div className='absolute top-0 right-0 left-0 h-1' style={{ backgroundColor: bgColor }} />

          {/* Action buttons on hover */}
          {showActions && (
            <div className='bg-background/80 absolute top-2 right-2 z-10 rounded-md p-1 opacity-0 backdrop-blur-sm transition-opacity group-hover:opacity-100'>
              <NodeActions
                nodeId={data.id}
                isExpanded={data.isExpanded ?? false}
                onExpand={(id) => data.onExpand?.(id)}
                onNavigate={(id) => data.onNavigate?.(id)}
                onShowMenu={() => {}}
              />
            </div>
          )}

          {/* UI Preview + Widget (A3: memoized so heavy content does not re-render on pan/zoom) */}
          {(hasPreview && (isExpanded || data.showPreview)) || (showWidget && hasWidget) ? (
            <RichNodePillPreviewBlock
              previewUrl={
                hasPreview && (isExpanded || data.showPreview)
                  ? (data.uiPreview?.thumbnailUrl ?? data.uiPreview?.screenshotUrl)
                  : undefined
              }
              widgetUrl={data.uiPreview?.interactiveWidgetUrl}
              label={data.label}
              hasWidget={hasWidget}
              showWidget={showWidget}
              onToggleWidget={toggleWidget}
            />
          ) : null}

          {/* Content section */}
          <div className='p-3 pt-3.5'>
            {/* Header: Icon + Type badge */}
            <div className='mb-2 flex items-center gap-2'>
              <div
                className='flex-shrink-0 rounded p-1.5'
                style={{ backgroundColor: `${bgColor}20` }}
              >
                <TypeIcon className='h-4 w-4' style={{ color: bgColor }} />
              </div>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Badge
                    variant='outline'
                    className='h-5 px-1.5 text-[10px]'
                    style={{
                      backgroundColor: `${bgColor}15`,
                      borderColor: `${bgColor}40`,
                      color: bgColor,
                    }}
                  >
                    {data.type.replaceAll('_', ' ')}
                  </Badge>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{data.type.replaceAll('_', ' ')}</p>
                </TooltipContent>
              </Tooltip>

              {/* Status badge */}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Badge variant='secondary' className='ml-auto h-5 px-1 text-[10px]'>
                    <StatusIcon className='mr-0.5 h-3 w-3' />
                    {data.status}
                  </Badge>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Status: {data.status}</p>
                </TooltipContent>
              </Tooltip>
            </div>

            {/* Title */}
            <h4 className='mb-2 line-clamp-2 text-sm leading-tight font-semibold'>{data.label}</h4>

            {/* Description (if expanded) */}
            {isExpanded && data.description && (
              <p className='text-muted-foreground mb-2 line-clamp-2 text-xs'>{data.description}</p>
            )}

            {/* Footer: Connection counts */}
            <div className='text-muted-foreground flex items-center gap-3 text-[10px]'>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className='flex items-center gap-0.5'>
                    <Link2 className='h-3 w-3' />
                    {data.connections.total}
                  </span>
                </TooltipTrigger>
                <TooltipContent>
                  <p>
                    {data.connections.incoming} incoming, {data.connections.outgoing} outgoing
                  </p>
                </TooltipContent>
              </Tooltip>

              {hasPreview && !isExpanded && (
                <span className='flex items-center gap-0.5 text-pink-500'>
                  <Image className='h-3 w-3' />
                  Preview
                </span>
              )}

              {hasWidget && (
                <span className='flex items-center gap-0.5 text-blue-500'>
                  <Code className='h-3 w-3' />
                  Widget
                </span>
              )}
            </div>

            {/* Quick actions bar at bottom (shown on hover) */}
            {showActions && (
              <div className='mt-2 border-t pt-2 opacity-0 transition-opacity group-hover:opacity-100'>
                <NodeQuickActions
                  nodeId={data.id}
                  onAddLink={(id, target) => {
                    logger.info('Link:', id, target);
                  }}
                  onAddTag={(id, tag) => {
                    logger.info('Tag:', id, tag);
                  }}
                  onEditNote={(id, note) => {
                    logger.info('Note:', id, note);
                  }}
                />
              </div>
            )}
          </div>
        </Card>

        {/* Output handle */}
        <Handle
          type='source'
          position={Position.Right}
          className='!bg-background !h-3 !w-3 !border-2'
          style={{ borderColor: bgColor }}
        />
      </TooltipProvider>
    </NodeContextMenu>
  );
}

export const RichNodePill = memo(RichNodePillComponent);
