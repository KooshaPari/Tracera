// Flow Graph View - React Flow based graph with rich custom nodes
// Provides block pill nodes with embedded previews and interactive widgets

import type { Edge, Node, NodeTypes } from '@xyflow/react';

import {
  Background,
  BackgroundVariant,
  Controls,
  MarkerType,
  MiniMap,
  Panel,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from '@xyflow/react';
import {
  Layers,
  LayoutGrid,
  Maximize2,
  Network,
  PanelRight,
  PanelRightClose,
  RotateCcw,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import type { Item, Link, LinkType } from '@tracertm/types';

import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';

import '@xyflow/react/dist/style.css';
import { Separator } from '@tracertm/ui/components/Separator';
import { Skeleton } from '@tracertm/ui/components/Skeleton';

import type { RichNodeData } from './RichNodePill';
import type { EnhancedNodeData, GraphPerspective } from './types';

import { NodeDetailPanel } from './NodeDetailPanel';
import { QAEnhancedNode } from './nodes/QAEnhancedNode';
import { PerspectiveSelector } from './PerspectiveSelector';
import { RichNodePill } from './RichNodePill';
import {
  ENHANCED_TYPE_COLORS,
  LINK_STYLES,
  PERSPECTIVE_CONFIGS,
  TYPE_TO_PERSPECTIVE,
} from './types';
import { UIComponentTree } from './UIComponentTree';

// Custom node types - using as assertion for React Flow compatibility
const nodeTypes: NodeTypes = {
  qaEnhanced: QAEnhancedNode as any,
  richPill: RichNodePill, // Type compatibility workaround for React Flow
};

interface FlowGraphViewProps {
  items: Item[];
  links: Link[];
  isLoading?: boolean | undefined;
  projectId?: string | undefined;
  onNavigateToItem?: ((itemId: string) => void) | undefined;
}

// Layout algorithms
type LayoutType = 'force' | 'hierarchical' | 'radial' | 'grid';

function FlowGraphViewInner({
  items,
  links,
  isLoading = false,
  onNavigateToItem,
}: FlowGraphViewProps) {
  const [perspective, setPerspective] = useState<GraphPerspective>('all');
  const [layout, setLayout] = useState<LayoutType>('force');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [showDetailPanel, setShowDetailPanel] = useState(true);
  const [showUITree, setShowUITree] = useState(false);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  const { zoomIn, zoomOut } = useReactFlow();

  // Build enhanced node data
  const enhancedNodes = useMemo((): EnhancedNodeData[] => {
    const itemMap = new Map(items.map((item) => [item.id, item]));

    const incomingCount = new Map<string, number>();
    const outgoingCount = new Map<string, number>();
    const connectionsByType = new Map<string, Record<LinkType, number>>();

    for (const link of links) {
      incomingCount.set(link.targetId, (incomingCount.get(link.targetId) ?? 0) + 1);
      outgoingCount.set(link.sourceId, (outgoingCount.get(link.sourceId) ?? 0) + 1);

      if (!connectionsByType.has(link.targetId)) {
        connectionsByType.set(link.targetId, {} as Record<LinkType, number>);
      }
      const targetTypes = connectionsByType.get(link.targetId)!;
      targetTypes[link.type] = (targetTypes[link.type] || 0) + 1;

      if (!connectionsByType.has(link.sourceId)) {
        connectionsByType.set(link.sourceId, {} as Record<LinkType, number>);
      }
      const sourceTypes = connectionsByType.get(link.sourceId)!;
      sourceTypes[link.type] = (sourceTypes[link.type] || 0) + 1;
    }

    return items.map((item) => {
      const itemType = (item.type || item.view || 'item').toLowerCase();
      const perspectives = TYPE_TO_PERSPECTIVE[itemType] ?? ['all'];
      const incoming = incomingCount.get(item.id) ?? 0;
      const outgoing = outgoingCount.get(item.id) ?? 0;

      const hasChildren = items.some((i) => i.parentId === item.id);

      let depth = 0;
      let currentId = item.parentId;
      while (currentId && depth < 10) {
        depth += 1;
        const parent = itemMap.get(currentId);
        currentId = parent?.parentId;
      }

      return {
        connections: {
          byType: connectionsByType.get(item.id) ?? ({} as Record<LinkType, number>),
          incoming,
          outgoing,
          total: incoming + outgoing,
        },
        depth,
        hasChildren,
        id: item.id,
        item,
        label: item.title || 'Untitled',
        parentId: item.parentId,
        perspective: perspectives,
        status: item.status,
        type: itemType,
        uiPreview: item.metadata?.['screenshotUrl']
          ? {
              componentCode: item.metadata['code'] as string | undefined,
              interactiveWidgetUrl: item.metadata['interactiveUrl'] as string | undefined,
              screenshotUrl: item.metadata['screenshotUrl'] as string,
              thumbnailUrl: item.metadata['thumbnailUrl'] as string | undefined,
            }
          : undefined,
      } as EnhancedNodeData;
    });
  }, [items, links]);

  // Filter nodes by perspective
  const filteredNodes = useMemo(() => {
    if (perspective === 'all') {
      return enhancedNodes;
    }

    const config = PERSPECTIVE_CONFIGS.find((c) => c.id === perspective);
    if (!config || config.includeTypes.length === 0) {
      return enhancedNodes;
    }

    return enhancedNodes.filter((node) => {
      const nodeType = node.type.toLowerCase();
      return (
        config.includeTypes.some((t) => nodeType.includes(t) || t.includes(nodeType)) ||
        node.perspective.includes(perspective)
      );
    });
  }, [enhancedNodes, perspective]);

  // Filter links
  const filteredLinks = useMemo(() => {
    const nodeIds = new Set(filteredNodes.map((n) => n.id));
    return links.filter((link) => nodeIds.has(link.sourceId) && nodeIds.has(link.targetId));
  }, [links, filteredNodes]);

  // Count by perspective
  const perspectiveCounts = useMemo(() => {
    const counts: Record<GraphPerspective, number> = {
      all: enhancedNodes.length,
      business: 0,
      performance: 0,
      product: 0,
      security: 0,
      technical: 0,
      ui: 0,
    };

    for (const node of enhancedNodes) {
      for (const p of node.perspective) {
        if (p !== 'all') {
          counts[p] = (counts[p] ?? 0) + 1;
        }
      }
    }

    return counts;
  }, [enhancedNodes]);

  // Create node data from enhanced node
  const createNodeData = useCallback(
    (node: EnhancedNodeData): RichNodeData => {
      const data: RichNodeData = {
        connections: node.connections,
        description: node.item.description ?? undefined,
        id: node.id,
        isExpanded: expandedNodes.has(node.id),
        item: node.item,
        label: node.label,
        onExpand: (id) => {
          setExpandedNodes((prev) => {
            const next = new Set(prev);
            if (next.has(id)) {
              next.delete(id);
            } else {
              next.add(id);
            }
            return next;
          });
        },
        onNavigate: onNavigateToItem ?? undefined,
        onSelect: setSelectedNodeId,
        showPreview: perspective === 'ui',
        status: node.status,
        type: node.type,
        uiPreview: node.uiPreview ?? undefined,
      };
      return data;
    },
    [expandedNodes, perspective, onNavigateToItem],
  );

  // Layout calculation
  const calculateLayout = useCallback(
    (nodes: EnhancedNodeData[], layoutType: LayoutType): Node<RichNodeData>[] => {
      const nodeWidth = 200;
      const nodeHeight = 120;
      const padding = 50;

      switch (layoutType) {
        case 'hierarchical': {
          // Group by depth, then arrange
          const byDepth = new Map<number, EnhancedNodeData[]>();
          for (const node of nodes) {
            const depth = node.depth || 0;
            if (!byDepth.has(depth)) {
              byDepth.set(depth, []);
            }
            byDepth.get(depth)!.push(node);
          }

          const result: Node<RichNodeData>[] = [];
          let maxRowWidth = 0;

          byDepth.forEach((depthNodes, _depth) => {
            maxRowWidth = Math.max(maxRowWidth, depthNodes.length);
          });

          byDepth.forEach((depthNodes, depth) => {
            const y = depth * (nodeHeight + padding * 2);
            const totalWidth = depthNodes.length * (nodeWidth + padding);
            const startX = (maxRowWidth * (nodeWidth + padding) - totalWidth) / 2;

            depthNodes.forEach((node, index) => {
              result.push({
                data: createNodeData(node),
                id: node.id,
                position: { x: startX + index * (nodeWidth + padding), y },
                type: 'richPill',
              });
            });
          });

          return result;
        }

        case 'radial': {
          // Arrange in concentric circles by depth
          const byDepth = new Map<number, EnhancedNodeData[]>();
          for (const node of nodes) {
            const depth = node.depth || 0;
            if (!byDepth.has(depth)) {
              byDepth.set(depth, []);
            }
            byDepth.get(depth)!.push(node);
          }

          const result: Node<RichNodeData>[] = [];
          const centerX = 500;
          const centerY = 400;

          byDepth.forEach((depthNodes, depth) => {
            const radius = (depth + 1) * (nodeWidth + padding);
            const angleStep = (2 * Math.PI) / depthNodes.length;

            depthNodes.forEach((node, index) => {
              const angle = index * angleStep - Math.PI / 2;
              result.push({
                data: createNodeData(node),
                id: node.id,
                position: {
                  x: centerX + radius * Math.cos(angle) - nodeWidth / 2,
                  y: centerY + radius * Math.sin(angle) - nodeHeight / 2,
                },
                type: 'richPill',
              });
            });
          });

          return result;
        }

        case 'grid': {
          // Simple grid layout
          const cols = Math.ceil(Math.sqrt(nodes.length));
          return nodes.map((node, index) => ({
            data: createNodeData(node),
            id: node.id,
            position: {
              x: (index % cols) * (nodeWidth + padding),
              y: Math.floor(index / cols) * (nodeHeight + padding),
            },
            type: 'richPill',
          }));
        }
        default: {
          // Force-directed simulation (simplified)
          const cols = Math.ceil(Math.sqrt(nodes.length));
          return nodes.map((node, index) => {
            // Add some randomness for force-like initial placement
            const baseX = (index % cols) * (nodeWidth + padding * 2);
            const baseY = Math.floor(index / cols) * (nodeHeight + padding * 2);
            const jitter = 20;

            return {
              data: createNodeData(node),
              id: node.id,
              position: {
                x: baseX + (Math.random() - 0.5) * jitter,
                y: baseY + (Math.random() - 0.5) * jitter,
              },
              type: 'richPill',
            };
          });
        }
      }
    },
    [createNodeData],
  );

  // Convert to React Flow nodes and edges
  const initialNodes = useMemo(
    () => calculateLayout(filteredNodes, layout),
    [filteredNodes, layout, calculateLayout],
  );

  const initialEdges = useMemo((): Edge[] => {
    const defaultStyle = { arrow: false, color: '#64748b', dashed: true };
    return filteredLinks.map((link) => {
      const linkStyle = LINK_STYLES[link.type] ?? defaultStyle;
      const edge: Edge = {
        animated: link.type === 'depends_on' || link.type === 'blocks',
        id: link.id,
        label: link.type.replaceAll('_', ' '),
        labelBgPadding: [4, 2] as [number, number],
        labelBgStyle: { fill: 'rgba(26, 26, 46, 0.9)' },
        labelStyle: { fill: linkStyle.color, fontSize: 10 },
        source: link.sourceId,
        style: {
          stroke: linkStyle.color,
          strokeWidth: 2,
          ...(linkStyle.dashed && { strokeDasharray: '5,5' }),
        },
        target: link.targetId,
        type: 'smoothstep',
      };
      if (linkStyle.arrow) {
        edge.markerEnd = {
          color: linkStyle.color,
          type: MarkerType.ArrowClosed,
        };
      }
      return edge;
    });
  }, [filteredLinks]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes as Node[]);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const layoutInputSignature = useMemo(() => {
    const nodeIds = filteredNodes.map((node) => node.id).join('|');
    const linkIds = filteredLinks.map((link) => link.id).join('|');
    return `${layout}|${nodeIds}|${linkIds}`;
  }, [filteredNodes, filteredLinks, layout]);
  const edgesSignature = useMemo(
    () =>
      filteredLinks
        .map((edge) => `${edge.id}:${edge.sourceId}->${edge.targetId}:${edge.type}`)
        .join('|'),
    [filteredLinks],
  );
  const prevNodesSignature = useRef<string>('');
  const prevEdgesSignature = useRef<string>('');

  // Update nodes when data changes
  useEffect(() => {
    if (layoutInputSignature && layoutInputSignature !== prevNodesSignature.current) {
      prevNodesSignature.current = layoutInputSignature;
      setNodes(calculateLayout(filteredNodes, layout) as Node[]);
    }
  }, [filteredNodes, layout, calculateLayout, setNodes, layoutInputSignature]);

  useEffect(() => {
    if (edgesSignature && edgesSignature !== prevEdgesSignature.current) {
      prevEdgesSignature.current = edgesSignature;
      setEdges(initialEdges);
    }
  }, [initialEdges, setEdges, edgesSignature]);

  // Selected node data
  const selectedNode = useMemo(() => {
    if (!selectedNodeId) {
      return null;
    }
    return filteredNodes.find((n) => n.id === selectedNodeId) ?? null;
  }, [filteredNodes, selectedNodeId]);

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
  const handlePerspectiveChange = (newPerspective: GraphPerspective) => {
    setPerspective(newPerspective);
    setSelectedNodeId(null);
    setShowUITree(newPerspective === 'ui');

    const config = PERSPECTIVE_CONFIGS.find((c) => c.id === newPerspective);
    if (config?.layoutPreference === 'breadthfirst') {
      setLayout('hierarchical');
    } else if (config?.layoutPreference === 'elk') {
      setLayout('hierarchical');
    } else if (config?.layoutPreference === 'circle') {
      setLayout('radial');
    } else {
      setLayout('force');
    }
  };

  const handleFit = () => {};
  const handleReset = () => {
    setPerspective('all');
    setLayout('force');
    setSelectedNodeId(null);
    setShowUITree(false);
    setExpandedNodes(new Set());
  };

  const handleFocusNode = (nodeId: string) => {
    setSelectedNodeId(nodeId);
    // Find the node and center on it
    const node = nodes.find((n) => n.id === nodeId);
    if (node) {
      undefined;
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className='space-y-6'>
        <Skeleton className='h-12 w-full' />
        <Skeleton className='h-14 w-full' />
        <Skeleton className='h-[calc(100vh-300px)]' />
      </div>
    );
  }

  // Empty state
  if (items.length === 0) {
    return (
      <div className='space-y-6'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Traceability Graph</h1>
          <p className='text-muted-foreground mt-2'>
            Multi-perspective visualization with rich node previews
          </p>
        </div>
        <Card className='p-12'>
          <div className='text-center'>
            <Network className='text-muted-foreground mx-auto mb-4 h-16 w-16' />
            <p className='text-muted-foreground'>No items to visualize</p>
            <p className='text-muted-foreground mt-1 text-sm'>
              Create items and links to see the traceability graph
            </p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      {/* Header */}
      <div className='flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between'>
        <div>
          <h1 className='flex items-center gap-2 text-3xl font-bold tracking-tight'>
            <Network className='h-8 w-8' />
            Traceability Graph
          </h1>
          <p className='text-muted-foreground mt-1'>
            {filteredNodes.length} items · {filteredLinks.length} connections
          </p>
        </div>

        {perspective !== 'all' && (
          <Badge
            variant='outline'
            className='px-3 py-1'
            style={{
              backgroundColor: `${PERSPECTIVE_CONFIGS.find((c) => c.id === perspective)?.color}20`,
              borderColor: PERSPECTIVE_CONFIGS.find((c) => c.id === perspective)?.color,
            }}
          >
            {PERSPECTIVE_CONFIGS.find((c) => c.id === perspective)?.label}
          </Badge>
        )}
      </div>

      {/* Perspective Selector */}
      <PerspectiveSelector
        currentPerspective={perspective}
        onPerspectiveChange={handlePerspectiveChange}
        itemCounts={perspectiveCounts}
      />

      {/* Controls */}
      <Card className='p-3'>
        <div className='flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between'>
          <div className='flex flex-wrap items-center gap-2'>
            {/* Layout selector */}
            <Select
              value={layout}
              onValueChange={(v) => {
                setLayout(v as LayoutType);
              }}
            >
              <SelectTrigger className='h-9 w-[160px]' aria-label='Graph layout selection'>
                <Layers className='mr-2 h-4 w-4' aria-hidden='true' />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='force'>Force-directed</SelectItem>
                <SelectItem value='hierarchical'>Hierarchical</SelectItem>
                <SelectItem value='radial'>Radial</SelectItem>
                <SelectItem value='grid'>Grid</SelectItem>
              </SelectContent>
            </Select>

            <Separator orientation='vertical' className='h-6' aria-hidden='true' />

            {/* UI Tree toggle */}
            <Button
              variant={showUITree ? 'default' : 'outline'}
              size='sm'
              onClick={() => {
                setShowUITree(!showUITree);
              }}
              className='h-9'
            >
              <LayoutGrid className='mr-2 h-4 w-4' />
              UI Library
            </Button>

            {/* Detail panel toggle */}
            <Button
              variant='ghost'
              size='sm'
              onClick={() => {
                setShowDetailPanel(!showDetailPanel);
              }}
              className='h-9'
            >
              {showDetailPanel ? (
                <PanelRightClose className='h-4 w-4' />
              ) : (
                <PanelRight className='h-4 w-4' />
              )}
            </Button>
          </div>

          <div className='flex items-center gap-2'>
            <div className='flex items-center gap-1 rounded-md border p-1'>
              <Button
                variant='ghost'
                size='sm'
                onClick={async () => zoomIn()}
                className='h-7 w-7 p-0'
                aria-label='Zoom in'
                title='Zoom in (Ctrl/Cmd + Plus)'
              >
                <ZoomIn className='h-4 w-4' aria-hidden='true' />
              </Button>
              <Button
                variant='ghost'
                size='sm'
                onClick={async () => zoomOut()}
                className='h-7 w-7 p-0'
                aria-label='Zoom out'
                title='Zoom out (Ctrl/Cmd + Minus)'
              >
                <ZoomOut className='h-4 w-4' aria-hidden='true' />
              </Button>
              <Button
                variant='ghost'
                size='sm'
                onClick={handleFit}
                className='h-7 w-7 p-0'
                aria-label='Fit view to content'
                title='Fit all nodes in view'
              >
                <Maximize2 className='h-4 w-4' aria-hidden='true' />
              </Button>
              <Button
                variant='ghost'
                size='sm'
                onClick={handleReset}
                className='h-7 w-7 p-0'
                aria-label='Reset graph view'
                title='Reset to default view'
              >
                <RotateCcw className='h-4 w-4' aria-hidden='true' />
              </Button>
            </div>
          </div>
        </div>
      </Card>

      {/* Main content area */}
      <div className='flex gap-4' style={{ height: 'calc(100vh - 340px)' }}>
        {/* UI Component Tree (left panel) */}
        {showUITree && (
          <div className='w-80 shrink-0'>
            <UIComponentTree
              items={items}
              links={links}
              onSelectItem={handleFocusNode}
              selectedItemId={selectedNodeId}
            />
          </div>
        )}

        {/* Graph Container (center) */}
        <Card className='flex-1 overflow-hidden p-0'>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
            minZoom={0.1}
            maxZoom={2}
            proOptions={{ hideAttribution: true }}
            className='bg-background'
          >
            <Background variant={BackgroundVariant.Dots} gap={20} size={1} color='#374151' />
            <Controls showInteractive={false} />
            <MiniMap
              nodeColor={(node) => {
                const nodeType = (node.data as RichNodeData | undefined)?.type;
                return nodeType ? (ENHANCED_TYPE_COLORS[nodeType] ?? '#64748b') : '#64748b';
              }}
              maskColor='rgba(0, 0, 0, 0.7)'
              className='!bg-card !border-border'
            />
            <Panel position='bottom-left' className='!m-2'>
              <div className='bg-card/90 flex flex-wrap gap-2 rounded-lg border p-2 text-[10px] backdrop-blur-sm'>
                {Object.entries(ENHANCED_TYPE_COLORS)
                  .filter(([type]) => filteredNodes.some((n) => n.type === type))
                  .slice(0, 8)
                  .map(([type, color]) => (
                    <div key={type} className='flex items-center gap-1'>
                      <div className='h-2.5 w-5 rounded' style={{ backgroundColor: color }} />
                      <span className='capitalize'>{type.replaceAll('_', ' ')}</span>
                    </div>
                  ))}
              </div>
            </Panel>
          </ReactFlow>
        </Card>

        {/* Node Detail Panel (right) */}
        {showDetailPanel && selectedNode && (
          <NodeDetailPanel
            node={selectedNode}
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

// Wrapper with ReactFlowProvider
export function FlowGraphView(props: FlowGraphViewProps) {
  return (
    <ReactFlowProvider>
      <FlowGraphViewInner {...props} />
    </ReactFlowProvider>
  );
}
