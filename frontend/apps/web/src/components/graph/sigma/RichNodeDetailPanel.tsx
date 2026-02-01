import { memo } from 'react';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

interface GraphNode {
  id: string;
  label: string;
  type: string;
  data: {
    image?: string;
    progress?: number;
    status?: string;
    description?: string;
    tags?: string[];
    [key: string]: any;
  };
}

interface RichNodeDetailPanelProps {
  node: GraphNode | null;
  onClose: () => void;
  onExpand?: (nodeId: string) => void;
  onNavigate?: (nodeId: string) => void;
}

export const RichNodeDetailPanel = memo(function RichNodeDetailPanel({
  node,
  onClose,
  onExpand,
  onNavigate,
}: RichNodeDetailPanelProps) {
  if (!node) return null;

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-card border-l shadow-lg z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex-1">
          <h3 className="font-semibold text-lg truncate">{node.label}</h3>
          <Badge variant="secondary" className="mt-1">
            {node.type}
          </Badge>
        </div>
        <Button
          size="sm"
          variant="ghost"
          onClick={onClose}
          className="h-8 w-8 p-0"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4 space-y-4">
          {/* Embedded image (full rich content) */}
          {node.data.image && (
            <div className="rounded-lg overflow-hidden border">
              <img
                src={node.data.image}
                alt={node.label}
                className="w-full h-auto"
              />
            </div>
          )}

          {/* Progress bar (full rich content) */}
          {node.data.progress !== undefined && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Progress</span>
                <span className="text-sm font-medium">{node.data.progress}%</span>
              </div>
              <Progress value={node.data.progress} className="h-2" />
            </div>
          )}

          {/* Status */}
          {node.data.status && (
            <div>
              <span className="text-sm text-muted-foreground">Status</span>
              <div className="mt-1">
                <Badge>{node.data.status}</Badge>
              </div>
            </div>
          )}

          {/* Description */}
          {node.data.description && (
            <div>
              <span className="text-sm text-muted-foreground">Description</span>
              <p className="mt-1 text-sm">{node.data.description}</p>
            </div>
          )}

          {/* Tags */}
          {node.data.tags && node.data.tags.length > 0 && (
            <div>
              <span className="text-sm text-muted-foreground">Tags</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {node.data.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Interactive buttons (full rich content) */}
          <div className="flex gap-2 pt-4 border-t">
            {onExpand && (
              <Button size="sm" onClick={() => onExpand(node.id)} className="flex-1">
                Expand
              </Button>
            )}
            {onNavigate && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => onNavigate(node.id)}
                className="flex-1"
              >
                Navigate
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});
