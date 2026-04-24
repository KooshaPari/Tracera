/**
 * Clustered Graph View
 *
 * Large-scale graph visualization using hierarchical clustering.
 * Automatically clusters 100k+ nodes into manageable super-nodes.
 */

import type { Edge, Node, NodeTypes } from '@xyflow/react';

import {
  Background,
  BackgroundVariant,
  Controls,
  MarkerType,
  Panel,
  ReactFlow,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from '@xyflow/react';
import {
  Activity,
  Layers,
  Maximize2,
  Minimize2,
  PanelRight,
  PanelRightClose,
  RotateCcw,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import type { Item, Link } from '@tracertm/types';

import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';

import '@xyflow/react/dist/style.css';
import { Card } from '@tracertm/ui/components/Card';
import { Separator } from '@tracertm/ui/components/Separator';

import type { ClusteringAlgorithm } from '../../hooks/useClustering';
import type { ClusterNode as _ClusterNodeType } from '../../lib/graphClustering';
import type { ClusterNodeData } from './ClusterNode';
import type { LayoutType } from './layouts/useDagLayout';
import type { RichNodeData } from './RichNodePill';
import type { EnhancedNodeData } from './types';

import { useClusterEdges, useClustering } from '../../hooks/useClustering';
import { ClusterNode } from './ClusterNode';
import { LayoutSelector } from './layouts/LayoutSelector';
import { useDagLayout } from './layouts/useDagLayout';
import { NodeDetailPanel } from './NodeDetailPanel';
import { RichNodePill } from './RichNodePill';

const customNodeTypes = {
  clusterNode: ClusterNode,
  richPill: RichNodePill,
} as const satisfies NodeTypes;

interface ClusteredGraphViewProps {
  items: Item[];
  links: Link[];
  onNavigateToItem?: ((itemId: string) => void) | undefined;
  showControls?: boolean | undefined;
  autoFit?: boolean | undefined;
  clusteringAlgorithm?: ClusteringAlgorithm;
  targetClusters?: number;
}

/**
 * Clustered graph view for 100k+ nodes
 */
export function ClusteredGraphView({
  items,
  links,
  onNavigateToItem,
  showControls = true,
  autoFit = true,
  clusteringAlgorithm = 'adaptive',
  targetClusters = 500,
}: ClusteredGraphViewProps) {
  const [layout, setLayout] = useState<LayoutType>('flow-chart');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [showDetailPanel, setShowDetailPanel] = useState(true);

  const { fitView, zoomIn, zoomOut } = useReactFlow();

  // Use clustering hook
  const {
    clustering,
    visibleClusters,
    visibleItems,
    toggleCluster,
    expandAll,
    collapseAll,
    drillDownToCluster,
    compressionRatio,
    clusterCount,
    quality,
    isProcessing,
  } = useClustering(items, links, {
    algorithm: clusteringAlgorithm,
    targetClusters,
  });

  // Get cluster edges
  const clusterEdges = useClusterEdges(clustering, links, 0);

  // Combine visible items and clusters for layout
  const nodesForLayout = useMemo((): Node[] => {
    const nodes: Node[] = [];

    // Add cluster nodes
    for (const cluster of visibleClusters) {
      const clusterItems = items.filter((item) => cluster.itemIds.has(item.id));

      nodes.push({
        data: {
          cluster,
          isExpanded: false,
          items: clusterItems,
          level: cluster.level,
          links: links.filter(
            (link) => cluster.itemIds.has(link.sourceId) || cluster.itemIds.has(link.targetId),
          ),
          onDrillDown: drillDownToCluster,
          onItemSelect: setSelectedNodeId,
          onToggle: toggleCluster,
        } as unknown as Record<string, unknown>,
        id: cluster.id,
        position: { x: 0, y: 0 },
        type: 'clusterNode',
      });
    }

    // Add individual item nodes
    for (const item of visibleItems) {
      nodes.push({
        data: {
          id: item.id,
          item,
          label: item.title || 'Untitled',
          onSelect: setSelectedNodeId,
          status: item.status,
          type: item.type || 'item',
        } as RichNodeData,
        id: item.id,
        position: { x: 0, y: 0 },
        type: 'richPill',
      });
    }

    return nodes;
  }, [visibleClusters, visibleItems, items, links, toggleCluster, drillDownToCluster]);

  // Create edges
  const edgesForLayout = useMemo((): {
    id: string;
    source: string;
    target: string;
  }[] => {
    const edges: { id: string; source: string; target: string }[] = [];

    // Add cluster edges
    for (const clusterEdge of clusterEdges) {
      edges.push({
        id: `cluster-edge-${clusterEdge.source}-${clusterEdge.target}`,
        source: clusterEdge.source,
        target: clusterEdge.target,
      });
    }

    // Add item edges (only for visible items)
    const visibleItemIds = new Set(visibleItems.map((i) => i.id));
    for (const link of links) {
      if (visibleItemIds.has(link.sourceId) && visibleItemIds.has(link.targetId)) {
        edges.push({
          id: link.id,
          source: link.sourceId,
          target: link.targetId,
        });
      }
    }

    return edges;
  }, [clusterEdges, visibleItems, links]);

  // Apply layout
  const { nodes: laidoutNodes } = useDagLayout(nodesForLayout, edgesForLayout, layout, {
    marginX: 50,
    marginY: 50,
    nodeHeight: 120,
    nodeSep: 80,
    nodeWidth: 200,
    rankSep: 120,
  });

  // Create final edges with styling
  const initialEdges = useMemo(
    (): Edge[] =>
      edgesForLayout.map((edge) => {
        // Find if this is a cluster edge
        const clusterEdge = clusterEdges.find(
          (ce) =>
            (ce.source === edge.source && ce.target === edge.target) ||
            (ce.source === edge.target && ce.target === edge.source),
        );

        if (clusterEdge) {
          // Style cluster edges differently
          return {
            animated: false,
            id: edge.id,
            label: `${clusterEdge.weight}`,
            labelBgPadding: [4, 2] as [number, number],
            labelBgStyle: { fill: 'rgba(26, 26, 46, 0.9)' },
            labelStyle: { fill: '#8b5cf6', fontSize: 10, fontWeight: 'bold' },
            markerEnd: {
              color: '#8b5cf6',
              type: MarkerType.ArrowClosed,
            },
            source: edge.source,
            style: {
              stroke: '#8b5cf6',
              strokeWidth: Math.min(clusterEdge.weight / 10, 5),
            },
            target: edge.target,
            type: 'smoothstep',
          } as Edge;
        }

        // Regular item edge
        return {
          animated: false,
          id: edge.id,
          markerEnd: {
            color: '#64748b',
            type: MarkerType.ArrowClosed,
          },
          source: edge.source,
          style: {
            stroke: '#64748b',
            strokeWidth: 1,
          },
          target: edge.target,
          type: 'smoothstep',
        } as Edge;
      }),
    [edgesForLayout, clusterEdges],
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(laidoutNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes when layout changes
  useEffect(() => {
    setNodes(laidoutNodes);
  }, [laidoutNodes, setNodes]);

  useEffect(() => {
    setEdges(initialEdges);
  }, [initialEdges, setEdges]);

  // Auto-fit on initial load
  useEffect(() => {
    if (autoFit && nodes.length > 0) {
      const timer = setTimeout(() => {}, 100);
      return () => {
        clearTimeout(timer);
      };
    }
    return;
  }, [autoFit, fitView, nodes.length]);

  // Selected node data
  const selectedNode = useMemo(() => {
    if (!selectedNodeId) {
      return null;
    }
    return items.find((i) => i.id === selectedNodeId) ?? null;
  }, [items, selectedNodeId]);

  // Links for selected node
  const { incomingLinks, outgoingLinks, relatedItems } = useMemo(() => {
    if (!selectedNodeId) {
      return { incomingLinks: [], outgoingLinks: [], relatedItems: [] };
    }

    const incoming = links.filter((l) => l.targetId === selectedNodeId);
    const outgoing = links.filter((l) => l.sourceId === selectedNodeId);
    const relatedIds = new Set([
      ...incoming.map((l) => l.sourceId),
      ...outgoing.map((l) => l.targetId),
    ]);

    return {
      incomingLinks: incoming,
      outgoingLinks: outgoing,
      relatedItems: items.filter((i) => relatedIds.has(i.id)),
    };
  }, [selectedNodeId, links, items]);

  // Handlers
  const handleFit = () => {};
  const handleReset = () => {
    setLayout('flow-chart');
    setSelectedNodeId(null);
    collapseAll();
  };

  const handleFocusNode = (nodeId: string) => {
    setSelectedNodeId(nodeId);
    const node = nodes.find((n) => n.id === nodeId);
    if (node) {
      undefined;
    }
  };

  return (
    <div className='flex h-full flex-col'>
      {/* Controls */}
      {showControls && (
        <Card className='mb-3 p-2'>
          <div className='flex items-center justify-between gap-3'>
            <div className='flex items-center gap-2'>
              <LayoutSelector
                value={layout}
                onChange={setLayout}
                variant='select'
                className='h-8 w-[200px]'
              />

              <Separator orientation='vertical' className='h-6' />

              <Button variant='ghost' size='sm' onClick={expandAll} className='h-8 text-xs'>
                <Maximize2 className='mr-1 h-3 w-3' />
                Expand All
              </Button>

              <Button variant='ghost' size='sm' onClick={collapseAll} className='h-8 text-xs'>
                <Minimize2 className='mr-1 h-3 w-3' />
                Collapse All
              </Button>

              <Separator orientation='vertical' className='h-6' />

              <Button
                variant='ghost'
                size='sm'
                onClick={() => {
                  setShowDetailPanel(!showDetailPanel);
                }}
                className='h-8'
              >
                {showDetailPanel ? (
                  <PanelRightClose className='h-4 w-4' />
                ) : (
                  <PanelRight className='h-4 w-4' />
                )}
              </Button>
            </div>

            <div className='flex items-center gap-2'>
              {/* Clustering metrics */}
              {clustering && (
                <div className='text-muted-foreground flex items-center gap-3 text-xs'>
                  <div className='flex items-center gap-1'>
                    <Layers className='h-3 w-3' />
                    <span>
                      {clusterCount} clusters ({compressionRatio.toFixed(1)}x compression)
                    </span>
                  </div>
                  {quality && (
                    <Badge variant='outline' className='text-[10px]'>
                      Q: {quality.modularity.toFixed(3)}
                    </Badge>
                  )}
                </div>
              )}

              {isProcessing && (
                <div className='text-muted-foreground flex items-center gap-2 text-xs'>
                  <Activity className='h-3 w-3 animate-spin' />
                  <span>Clustering...</span>
                </div>
              )}

              <Separator orientation='vertical' className='h-6' />

              <div className='flex items-center gap-1 rounded-md border p-0.5'>
                <Button
                  variant='ghost'
                  size='sm'
                  onClick={async () => zoomIn()}
                  className='h-7 w-7 p-0'
                >
                  <ZoomIn className='h-4 w-4' />
                </Button>
                <Button
                  variant='ghost'
                  size='sm'
                  onClick={async () => zoomOut()}
                  className='h-7 w-7 p-0'
                >
                  <ZoomOut className='h-4 w-4' />
                </Button>
                <Button variant='ghost' size='sm' onClick={handleFit} className='h-7 w-7 p-0'>
                  <Maximize2 className='h-4 w-4' />
                </Button>
                <Button variant='ghost' size='sm' onClick={handleReset} className='h-7 w-7 p-0'>
                  <RotateCcw className='h-4 w-4' />
                </Button>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Graph area */}
      <div className='flex flex-1 gap-3'>
        <Card className='flex-1 overflow-hidden p-0'>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={customNodeTypes}
            fitView={autoFit}
            minZoom={0.1}
            maxZoom={2}
            proOptions={{ hideAttribution: true }}
            className='bg-background'
          >
            <Background variant={BackgroundVariant.Dots} gap={20} size={1} color='#374151' />
            <Controls showInteractive={false} />
            <Panel position='top-right' className='!m-2'>
              <Badge variant='secondary' className='text-xs'>
                {items.length} total · {nodes.length} visible
              </Badge>
            </Panel>
          </ReactFlow>
        </Card>

        {/* Node Detail Panel */}
        {showDetailPanel && selectedNode && (
          <NodeDetailPanel
            node={
              {
                connections: {
                  byType: {},
                  incoming: incomingLinks.length,
                  outgoing: outgoingLinks.length,
                  total: incomingLinks.length + outgoingLinks.length,
                },
                depth: 0,
                hasChildren: false,
                id: selectedNode.id,
                item: selectedNode,
                label: selectedNode.title || 'Untitled',
                perspective: [],
                status: selectedNode.status,
                type: selectedNode.type || 'item',
              } as unknown as EnhancedNodeData
            }
            relatedItems={relatedItems}
            incomingLinks={incomingLinks}
            outgoingLinks={outgoingLinks}
            onClose={() => {
              setSelectedNodeId(null);
            }}
            onNavigateToItem={onNavigateToItem ?? (() => {})}
            onFocusNode={handleFocusNode}
          />
        )}
      </div>
    </div>
  );
}
