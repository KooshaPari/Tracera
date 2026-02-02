import { memo, useState } from 'react';
import type { Node, Edge } from '@xyflow/react';
import { FlowGraphViewInner } from './FlowGraphViewInner';
import { SigmaGraphView } from './SigmaGraphView';
import { RichNodeDetailPanel } from './sigma/RichNodeDetailPanel';
import { useHybridGraph, type HybridGraphConfig } from '@/hooks/useHybridGraph';
import { Badge } from '@/components/ui/badge';
import { Zap, Layers } from 'lucide-react';

interface HybridGraphViewProps {
  nodes: Node[];
  edges: Edge[];
  onNodeClick?: (nodeId: string) => void;
  onNodeExpand?: (nodeId: string) => void;
  onNodeNavigate?: (nodeId: string) => void;
  config?: HybridGraphConfig;
  className?: string;
}

export const HybridGraphView = memo(function HybridGraphView({
  nodes,
  edges,
  onNodeClick,
  onNodeExpand,
  onNodeNavigate,
  config,
  className = '',
}: HybridGraphViewProps) {
  const {
    useWebGL,
    nodeCount,
    graphologyGraph,
    setSelectedNodeId,
  } = useHybridGraph(nodes, edges, config);

  const [detailPanelNode, setDetailPanelNode] = useState<any>(null);

  // Handle node click
  const handleNodeClick = (nodeId: string) => {
    setSelectedNodeId(nodeId);

    // In WebGL mode, open detail panel
    if (useWebGL) {
      const node = nodes.find(n => n.id === nodeId);
      if (node) {
        setDetailPanelNode({
          id: node.id,
          label: node.data?.label || node.id,
          type: node.type || 'default',
          data: node.data || {},
        });
      }
    }

    // Call parent handler
    if (onNodeClick) onNodeClick(nodeId);
  };

  // Handle node double-click (expand in WebGL mode)
  const handleNodeDoubleClick = (nodeId: string) => {
    if (onNodeExpand) onNodeExpand(nodeId);
  };

  return (
    <div className={`relative h-full w-full ${className}`}>
      {/* Performance mode indicator */}
      <div className="absolute top-4 right-4 z-10 flex items-center gap-2">
        <Badge
          variant={useWebGL ? 'default' : 'secondary'}
          className="text-xs font-medium"
        >
          {useWebGL ? (
            <>
              <Zap className="h-3 w-3 mr-1" />
              WebGL Mode
            </>
          ) : (
            <>
              <Layers className="h-3 w-3 mr-1" />
              ReactFlow Mode
            </>
          )}
        </Badge>
        <Badge variant="outline" className="text-xs">
          {nodeCount.toLocaleString()} nodes
        </Badge>
      </div>

      {/* Render graph based on mode */}
      {useWebGL && graphologyGraph ? (
        // WebGL mode (>10k nodes)
        <SigmaGraphView
          graph={graphologyGraph}
          onNodeClick={handleNodeClick}
          onNodeDoubleClick={handleNodeDoubleClick}
          className="h-full w-full"
        />
      ) : (
        // ReactFlow mode (<10k nodes)
        <FlowGraphViewInner
          nodes={nodes}
          edges={edges}
          onNodeSelect={handleNodeClick}
        />
      )}

      {/* Rich node detail panel (WebGL mode only) */}
      {useWebGL && detailPanelNode && (
        <RichNodeDetailPanel
          node={detailPanelNode}
          onClose={() => setDetailPanelNode(null)}
          onExpand={onNodeExpand}
          onNavigate={onNodeNavigate}
        />
      )}

      {/* Threshold warning (near threshold) */}
      {!useWebGL && nodeCount > 8000 && (
        <div className="absolute bottom-4 left-4 z-10">
          <Badge variant="warning" className="text-xs">
            Approaching 10k node threshold - WebGL mode will activate automatically
          </Badge>
        </div>
      )}
    </div>
  );
});
