// Rich Node Pill - Block pill with embedded UI preview and interactive widget
// Uses React Flow for custom node rendering with rich content

import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import type { Item, LinkType } from "@tracertm/types";
import { Handle, Position, type NodeProps, NodeResizer, NodeToolbar, type Node } from "@xyflow/react";
import {
  AlertCircle,
  CheckCircle2,
  Circle,
  Clock,
  Code,
  Database,
  ExternalLink,
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
  Maximize2,
  Eye,
} from "lucide-react";
import { memo, useState, useCallback } from "react";
import { ENHANCED_TYPE_COLORS, STATUS_OPACITY } from "./types";

// Node data structure for React Flow
export interface RichNodeData {
  id: string;
  item: Item;
  type: string;
  status: string;
  label: string;
  description?: string | undefined;

  // UI preview
  uiPreview?: {
    screenshotUrl?: string;
    componentCode?: string;
    interactiveWidgetUrl?: string;
    thumbnailUrl?: string;
  } | undefined;

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

  // Callbacks
  onSelect?: ((id: string) => void) | undefined;
  onExpand?: ((id: string) => void) | undefined;
  onNavigate?: ((id: string) => void) | undefined;

  // Index signature for React Flow compatibility
  [key: string]: unknown;
}

// Icon mapping
const TYPE_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  requirement: FileText,
  feature: Zap,
  epic: GitBranch,
  user_story: FileText,
  story: FileText,
  api: Code,
  database: Database,
  code: Code,
  architecture: Layout,
  infrastructure: Monitor,
  wireframe: Image,
  ui_component: Layout,
  page: Monitor,
  component: Layout,
  test: TestTube2,
  test_case: TestTube2,
  security: Shield,
  vulnerability: AlertCircle,
  performance: Zap,
  monitoring: Monitor,
  task: Circle,
  bug: AlertCircle,
  journey: GitBranch,
};

const STATUS_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  done: CheckCircle2,
  completed: CheckCircle2,
  in_progress: Clock,
  todo: Circle,
  pending: Circle,
  blocked: XCircle,
  cancelled: XCircle,
};

function RichNodePillComponent({ data, selected }: NodeProps<Node<RichNodeData, "richPill">>) {
  const [isHovered, setIsHovered] = useState(false);
  const [showWidget, setShowWidget] = useState(false);

  const bgColor = ENHANCED_TYPE_COLORS[data.type] || "#64748b";
  const opacity = STATUS_OPACITY[data.status] || 1;
  const TypeIcon = TYPE_ICONS[data.type] || FileText;
  const StatusIcon = STATUS_ICONS[data.status] || Circle;

  const hasPreview = !!data.uiPreview?.screenshotUrl || !!data.uiPreview?.thumbnailUrl;
  const hasWidget = !!data.uiPreview?.interactiveWidgetUrl;
  const isExpanded = data.isExpanded || (hasPreview && isHovered);

  const handleClick = useCallback(() => {
    data.onSelect?.(data.id);
  }, [data]);

  const handleExpand = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    data.onExpand?.(data.id);
  }, [data]);

  const handleNavigate = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    data.onNavigate?.(data.id);
  }, [data]);

  const toggleWidget = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    setShowWidget(!showWidget);
  }, [showWidget]);

  return (
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
        <div className="flex gap-1 bg-background border rounded-lg shadow-lg p-1">
          <Button variant="ghost" size="sm" className="h-7 px-2" onClick={handleNavigate}>
            <ExternalLink className="h-3.5 w-3.5 mr-1" />
            Open
          </Button>
          {hasPreview && (
            <Button variant="ghost" size="sm" className="h-7 px-2" onClick={handleExpand}>
              <Maximize2 className="h-3.5 w-3.5 mr-1" />
              Expand
            </Button>
          )}
          {hasWidget && (
            <Button variant="ghost" size="sm" className="h-7 px-2" onClick={toggleWidget}>
              <Eye className="h-3.5 w-3.5 mr-1" />
              {showWidget ? "Hide" : "Preview"}
            </Button>
          )}
        </div>
      </NodeToolbar>

      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-background !border-2"
        style={{ borderColor: bgColor }}
      />

      {/* Main pill container */}
      <Card
        className={`
          relative overflow-hidden transition-all duration-200 cursor-pointer
          ${selected ? "ring-2 ring-white ring-offset-2 ring-offset-background" : ""}
          ${isHovered ? "shadow-lg scale-[1.02]" : "shadow-md"}
        `}
        style={{
          opacity,
          minWidth: 180,
          maxWidth: isExpanded ? 350 : 220,
        }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={handleClick}
      >
        {/* Color accent bar */}
        <div
          className="absolute top-0 left-0 right-0 h-1"
          style={{ backgroundColor: bgColor }}
        />

        {/* UI Preview Section (inner block) */}
        {hasPreview && (isExpanded || data.showPreview) && (
          <div className="relative bg-muted/50 border-b">
            <img
              src={data.uiPreview?.thumbnailUrl || data.uiPreview?.screenshotUrl}
              alt={`Preview of ${data.label}`}
              className="w-full h-24 object-cover object-top"
              loading="lazy"
            />
            {hasWidget && (
              <Button
                variant="secondary"
                size="sm"
                className="absolute bottom-2 right-2 h-6 px-2 text-[10px] bg-background/80 backdrop-blur-sm"
                onClick={toggleWidget}
              >
                <Eye className="h-3 w-3 mr-1" />
                Interactive
              </Button>
            )}
          </div>
        )}

        {/* Interactive Widget Iframe */}
        {showWidget && hasWidget && (
          <div className="relative bg-white border-b">
            <iframe
              src={data.uiPreview?.interactiveWidgetUrl}
              title={`Widget: ${data.label}`}
              className="w-full h-40 border-0"
              sandbox="allow-scripts allow-same-origin"
            />
            <Button
              variant="ghost"
              size="sm"
              className="absolute top-1 right-1 h-5 w-5 p-0"
              onClick={toggleWidget}
            >
              <XCircle className="h-4 w-4" />
            </Button>
          </div>
        )}

        {/* Content section */}
        <div className="p-3 pt-3.5">
          {/* Header: Icon + Type badge */}
          <div className="flex items-center gap-2 mb-2">
            <div
              className="flex-shrink-0 rounded p-1.5"
              style={{ backgroundColor: `${bgColor}20` }}
            >
              <TypeIcon className="h-4 w-4" style={{ color: bgColor }} />
            </div>

            <Tooltip>
              <TooltipTrigger asChild>
                <Badge
                  variant="outline"
                  className="text-[10px] px-1.5 h-5"
                  style={{
                    backgroundColor: `${bgColor}15`,
                    color: bgColor,
                    borderColor: `${bgColor}40`,
                  }}
                >
                  {data.type.replace(/_/g, " ")}
                </Badge>
              </TooltipTrigger>
              <TooltipContent>
                <p>{data.type.replace(/_/g, " ")}</p>
              </TooltipContent>
            </Tooltip>

            {/* Status badge */}
            <Tooltip>
              <TooltipTrigger asChild>
                <Badge
                  variant="secondary"
                  className="text-[10px] px-1 h-5 ml-auto"
                >
                  <StatusIcon className="h-3 w-3 mr-0.5" />
                  {data.status}
                </Badge>
              </TooltipTrigger>
              <TooltipContent>
                <p>Status: {data.status}</p>
              </TooltipContent>
            </Tooltip>
          </div>

          {/* Title */}
          <h4 className="font-semibold text-sm leading-tight line-clamp-2 mb-2">
            {data.label}
          </h4>

          {/* Description (if expanded) */}
          {isExpanded && data.description && (
            <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
              {data.description}
            </p>
          )}

          {/* Footer: Connection counts */}
          <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="flex items-center gap-0.5">
                  <Link2 className="h-3 w-3" />
                  {data.connections.total}
                </span>
              </TooltipTrigger>
              <TooltipContent>
                <p>{data.connections.incoming} incoming, {data.connections.outgoing} outgoing</p>
              </TooltipContent>
            </Tooltip>

            {hasPreview && !isExpanded && (
              <span className="flex items-center gap-0.5 text-pink-500">
                <Image className="h-3 w-3" />
                Preview
              </span>
            )}

            {hasWidget && (
              <span className="flex items-center gap-0.5 text-blue-500">
                <Code className="h-3 w-3" />
                Widget
              </span>
            )}
          </div>
        </div>
      </Card>

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-background !border-2"
        style={{ borderColor: bgColor }}
      />
    </TooltipProvider>
  );
}

export const RichNodePill = memo(RichNodePillComponent);
