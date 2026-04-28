// Rich Graph Node Component - Block Pill Style with UI Preview

import {
  AlertCircle,
  CheckCircle2,
  Circle,
  Clock,
  Code,
  Database,
  FileText,
  GitBranch,
  Image,
  Layout,
  Link2,
  Monitor,
  Shield,
  TestTube2,
  XCircle,
  Zap,
} from 'lucide-react';
import { memo } from 'react';

import { Badge } from '@tracertm/ui/components/Badge';
import { Card } from '@tracertm/ui/components/Card';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

import type { EnhancedNodeData } from './types';

import { ENHANCED_TYPE_COLORS, STATUS_OPACITY } from './types';

interface GraphNodePillProps {
  node: EnhancedNodeData;
  isSelected: boolean;
  isHighlighted: boolean;
  onSelect: (nodeId: string) => void;
  onExpand: (nodeId: string) => void;
  showPreview: boolean;
}

// Icon mapping for item types
const TYPE_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  api: Code,
  architecture: Layout,
  audit: Shield,
  bug: AlertCircle,
  code: Code,
  component: Layout,
  database: Database,
  epic: GitBranch,
  feature: Zap,
  infrastructure: Monitor,
  journey: GitBranch,
  metric: Zap,
  monitoring: Monitor,
  page: Monitor,
  performance: Zap,
  requirement: FileText,
  security: Shield,
  story: FileText,
  task: Circle,
  test: TestTube2,
  test_case: TestTube2,
  test_suite: TestTube2,
  ui_component: Layout,
  user_story: FileText,
  vulnerability: AlertCircle,
  wireframe: Image,
};

// Status icons
const STATUS_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  blocked: XCircle,
  cancelled: XCircle,
  completed: CheckCircle2,
  done: CheckCircle2,
  in_progress: Clock,
  pending: Circle,
  todo: Circle,
};

function GraphNodePillComponent({
  node,
  isSelected,
  isHighlighted,
  onSelect,
  onExpand,
  showPreview,
}: GraphNodePillProps) {
  const TypeIcon = TYPE_ICONS[node.type] ?? Circle;
  const StatusIcon = STATUS_ICONS[node.status] ?? Circle;
  const bgColor = ENHANCED_TYPE_COLORS[node.type] ?? '#64748b';
  const opacity = STATUS_OPACITY[node.status] ?? 1;

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSelect(node.id);
  };

  const handleDoubleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onExpand(node.id);
  };

  return (
    <TooltipProvider>
      <Tooltip delayDuration={300}>
        <TooltipTrigger asChild>
          <div
            onClick={handleClick}
            onDoubleClick={handleDoubleClick}
            className={`relative cursor-pointer transition-all duration-200 ease-out ${isSelected ? 'z-20 scale-105' : 'z-10 hover:scale-102'} ${isHighlighted ? 'ring-offset-background ring-2 ring-white ring-offset-2' : ''} `}
            style={{ opacity }}
          >
            {/* Main Pill Container */}
            <Card
              className={`overflow-hidden border-2 transition-all duration-200 ${isSelected ? 'shadow-primary/20 shadow-lg' : 'shadow-md'} `}
              style={{
                borderColor: isSelected ? '#fff' : bgColor,
                minWidth: showPreview && node.uiPreview?.screenshotUrl ? '180px' : '140px',
              }}
            >
              {/* UI Preview Section (if applicable) */}
              {showPreview && node.uiPreview?.screenshotUrl && (
                <div
                  className='h-24 border-b bg-cover bg-center bg-no-repeat'
                  style={{
                    backgroundImage: `url(${node.uiPreview.screenshotUrl})`,
                    borderColor: bgColor,
                  }}
                >
                  {/* Interactive overlay indicator */}
                  {node.uiPreview.interactiveWidgetUrl && (
                    <div className='absolute top-1 right-1 flex items-center gap-1 rounded bg-black/60 px-1.5 py-0.5 text-[10px] text-white'>
                      <Monitor className='h-3 w-3' />
                      Interactive
                    </div>
                  )}
                </div>
              )}

              {/* Node Content */}
              <div
                className='p-2.5'
                style={{
                  backgroundColor: `${bgColor}15`,
                }}
              >
                {/* Header: Type Icon + Title */}
                <div className='flex items-start gap-2'>
                  <div className='shrink-0 rounded-md p-1.5' style={{ backgroundColor: bgColor }}>
                    <TypeIcon className='h-3.5 w-3.5 text-white' />
                  </div>
                  <div className='min-w-0 flex-1'>
                    <p className='text-foreground line-clamp-2 text-xs leading-tight font-semibold'>
                      {node.label}
                    </p>
                  </div>
                </div>

                {/* Status & Connections Row */}
                <div className='mt-2 flex items-center justify-between gap-2'>
                  <Badge
                    variant='secondary'
                    className='flex h-5 items-center gap-1 px-1.5 py-0 text-[10px]'
                    style={{
                      backgroundColor: `${bgColor}25`,
                      color: bgColor,
                    }}
                  >
                    <StatusIcon className='h-2.5 w-2.5' />
                    {node.status}
                  </Badge>

                  {/* Connection count */}
                  {node.connections.total > 0 && (
                    <div className='text-muted-foreground flex items-center gap-1 text-[10px]'>
                      <Link2 className='h-3 w-3' />
                      <span>{node.connections.total}</span>
                    </div>
                  )}
                </div>

                {/* Type indicator bar */}
                <div className='mt-2 h-1 rounded-full' style={{ backgroundColor: bgColor }} />
              </div>
            </Card>

            {/* Children indicator */}
            {node.hasChildren && (
              <div
                className='absolute -bottom-1 left-1/2 h-1 w-4 -translate-x-1/2 rounded-full'
                style={{ backgroundColor: bgColor }}
              />
            )}
          </div>
        </TooltipTrigger>
        <TooltipContent side='right' className='max-w-xs'>
          <div className='space-y-2'>
            <div className='flex items-center gap-2'>
              <div className='rounded p-1' style={{ backgroundColor: bgColor }}>
                <TypeIcon className='h-3 w-3 text-white' />
              </div>
              <span className='font-medium'>{node.type}</span>
            </div>
            <p className='text-sm'>{node.item.description ?? 'No description'}</p>
            {node.item.owner && (
              <p className='text-muted-foreground text-xs'>Owner: {node.item.owner}</p>
            )}
            <div className='text-muted-foreground text-xs'>
              {node.connections.incoming} incoming, {node.connections.outgoing} outgoing
            </div>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

export const GraphNodePill = memo(GraphNodePillComponent);
