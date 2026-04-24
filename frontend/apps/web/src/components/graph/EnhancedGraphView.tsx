// Enhanced Graph View - Multi-perspective traceability visualization
// Features: Multiple views, rich node pills, Storybook-like UI view

import cytoscape, {
  Core,
  CytoscapeOptions,
  EdgeSingular,
  EventObject,
  LayoutOptions,
  NodeSingular,
} from 'cytoscape';
import {
  Download,
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
import { CSSProperties, memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';

import type { Item, LayoutType, Link, LinkType } from '@tracertm/types';

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
import { Separator } from '@tracertm/ui/components/Separator';
import { Skeleton } from '@tracertm/ui/components/Skeleton';

import { NodeDetailPanel } from './NodeDetailPanel';
import { PerspectiveSelector } from './PerspectiveSelector';
import {
  ENHANCED_TYPE_COLORS,
  EnhancedNodeData,
  GraphPerspective,
  LINK_STYLES,
  PERSPECTIVE_CONFIGS,
  PerspectiveConfig,
  STATUS_OPACITY,
  TYPE_TO_PERSPECTIVE,
} from './types';
import { UIComponentTree } from './UIComponentTree';

const MAX_PARENT_DEPTH = 10;
const BREADTHFIRST_PADDING = 50;
const BREADTHFIRST_SPACING_FACTOR = 1.5;
const COSE_EDGE_ELASTICITY = 100;
const COSE_GRAVITY = 0.25;
const COSE_IDEAL_EDGE_LENGTH = 100;
const COSE_NODE_REPULSION = 8000;
const NODE_MIN_WIDTH = 100;
const NODE_MAX_WIDTH = 180;
const NODE_LABEL_MULTIPLIER = 6;
const NODE_HORIZONTAL_PADDING = 40;
const FIT_PADDING = 50;
const ZOOM_STEP = 1.3;
const FOCUS_ZOOM = 1.5;
const BORDER_WIDTH_HIGHLIGHT = 3;
const DEFAULT_NODE_COLOR = '#64748b';
const DEFAULT_EDGE_COLOR = '#94a3b8';
const GRAPH_CONTAINER_HEIGHT = 'calc(100vh - 340px)';

const NOOP_NAVIGATE_TO_ITEM = (_itemId: string): void => {};

interface CytoscapeNodeData {
  id: string;
  label: string;
  type: string;
  status: string;
  connectionCount: number;
  nodeWidth: number;
  backgroundColor: string;
  backgroundOpacity: number;
  borderColor: string;
}

interface CytoscapeEdgeData {
  id: string;
  source: string;
  target: string;
  type: string;
  label: string;
  lineColor: string;
  arrowColor: string;
  arrowShape: 'triangle' | 'none';
  lineStyle: 'dashed' | 'solid';
}

function toNonEmptyString(value: unknown): string | undefined {
  if (typeof value !== 'string') {
    return undefined;
  }
  return value.length > 0 ? value : undefined;
}

function getLinkTypeCountMap(): Record<LinkType, number> {
  return {} as Record<LinkType, number>;
}

function getNodeColor(type: string): string {
  return ENHANCED_TYPE_COLORS[type] ?? DEFAULT_NODE_COLOR;
}

function getNodeOpacity(status: string): number {
  return STATUS_OPACITY[status] ?? 1;
}

function getPerspectiveConfig(activePerspective: GraphPerspective): PerspectiveConfig | undefined {
  return PERSPECTIVE_CONFIGS.find((configEntry) => configEntry.id === activePerspective);
}

function getNodeDepth(item: Item, itemMap: Map<string, Item>): number {
  let depth = 0;
  let currentId: string | undefined = item.parentId;
  while (typeof currentId === 'string' && currentId.length > 0 && depth < MAX_PARENT_DEPTH) {
    depth += 1;
    const parent = itemMap.get(currentId);
    currentId = parent?.parentId;
  }
  return depth;
}

function buildNodeUIPreview(item: Item): EnhancedNodeData['uiPreview'] {
  const screenshotUrl = toNonEmptyString(item.metadata?.['screenshotUrl']);
  if (screenshotUrl === undefined) {
    return;
  }

  const componentCode = toNonEmptyString(item.metadata?.['code']);
  const interactiveWidgetUrl = toNonEmptyString(item.metadata?.['interactiveUrl']);
  const uiPreview: NonNullable<EnhancedNodeData['uiPreview']> = { screenshotUrl };

  if (componentCode !== undefined) {
    uiPreview.componentCode = componentCode;
  }
  if (interactiveWidgetUrl !== undefined) {
    uiPreview.interactiveWidgetUrl = interactiveWidgetUrl;
  }

  return uiPreview;
}

function createCytoscapeNode(node: EnhancedNodeData): { data: CytoscapeNodeData } {
  return {
    data: {
      connectionCount: node.connections.total,
      backgroundColor: getNodeColor(node.type),
      backgroundOpacity: getNodeOpacity(node.status),
      borderColor: getNodeColor(node.type),
      id: node.id,
      label: node.label,
      nodeWidth: Math.max(
        NODE_MIN_WIDTH,
        Math.min(
          NODE_MAX_WIDTH,
          node.label.length * NODE_LABEL_MULTIPLIER + NODE_HORIZONTAL_PADDING,
        ),
      ),
      status: node.status,
      type: node.type,
    },
  };
}

function createCytoscapeEdge(link: Link): { data: CytoscapeEdgeData } {
  return {
    data: {
      arrowColor: LINK_STYLES[link.type]?.color ?? DEFAULT_EDGE_COLOR,
      arrowShape: LINK_STYLES[link.type]?.arrow === true ? 'triangle' : 'none',
      id: link.id,
      label: link.type.replaceAll('_', ' '),
      lineColor: LINK_STYLES[link.type]?.color ?? DEFAULT_EDGE_COLOR,
      lineStyle: LINK_STYLES[link.type]?.dashed === true ? 'dashed' : 'solid',
      source: link.sourceId,
      target: link.targetId,
      type: link.type,
    },
  };
}

function getGraphLayoutOptions(layout: LayoutType): LayoutOptions {
  return {
    name: layout === 'elk' ? 'breadthfirst' : layout,
    animate: true,
    animationDuration: 500,
    ...(layout === 'breadthfirst' || layout === 'elk'
      ? {
          directed: true,
          padding: BREADTHFIRST_PADDING,
          spacingFactor: BREADTHFIRST_SPACING_FACTOR,
        }
      : {}),
    ...(layout === 'cose'
      ? {
          edgeElasticity: COSE_EDGE_ELASTICITY,
          gravity: COSE_GRAVITY,
          idealEdgeLength: COSE_IDEAL_EDGE_LENGTH,
          nodeRepulsion: COSE_NODE_REPULSION,
        }
      : {}),
  };
}

function getGraphStyles(perspectiveColor: string | undefined): CytoscapeOptions['style'] {
  return [
    {
      selector: 'node',
      style: {
        shape: 'round-rectangle',
        width: (node: NodeSingular): number => node.data('nodeWidth') as number,
        height: 50,
        'background-color': 'data(backgroundColor)',
        'background-opacity': (node: NodeSingular): number =>
          node.data('backgroundOpacity') as number,
        label: 'data(label)',
        color: '#fff',
        'text-outline-color': 'data(borderColor)',
        'text-outline-width': 2,
        'font-size': 11,
        'font-weight': 'bold',
        'text-valign': 'center',
        'text-halign': 'center',
        'text-wrap': 'ellipsis',
        'text-max-width': 140 as unknown as string,
        'border-width': 2,
        'border-color': 'data(borderColor)',
        'border-opacity': 0.3,
      },
    },
    {
      selector: 'edge',
      style: {
        width: 2,
        'line-color': 'data(lineColor)',
        'target-arrow-color': 'data(arrowColor)',
        'target-arrow-shape': (edge: EdgeSingular): CytoscapeEdgeData['arrowShape'] =>
          edge.data('arrowShape') as CytoscapeEdgeData['arrowShape'],
        'line-style': (edge: EdgeSingular): CytoscapeEdgeData['lineStyle'] =>
          edge.data('lineStyle') as CytoscapeEdgeData['lineStyle'],
        'curve-style': 'bezier',
        opacity: 0.6,
        label: 'data(label)',
        'font-size': 9,
        'text-rotation': 'autorotate',
        'text-margin-y': -10,
        color: '#94a3b8',
        'text-background-color': '#1a1a2e',
        'text-background-opacity': 0.8,
        'text-background-padding': '2px',
      },
    },
    {
      selector: 'node:selected',
      style: {
        'border-color': '#fff',
        'border-opacity': 1,
        'border-width': 4,
        'overlay-color': '#fff',
        'overlay-opacity': 0.1,
      },
    },
    {
      selector: 'edge:selected',
      style: {
        opacity: 1,
        width: 4,
      },
    },
    {
      selector: 'node.highlighted',
      style: {
        'border-color': perspectiveColor ?? '#fff',
        'border-opacity': 1,
        'border-width': BORDER_WIDTH_HIGHLIGHT,
      },
    },
    {
      selector: 'edge.highlighted',
      style: {
        opacity: 1,
        width: 3,
      },
    },
    {
      selector: 'node.faded',
      style: {
        opacity: 0.3,
      },
    },
    {
      selector: 'edge.faded',
      style: {
        opacity: 0.15,
      },
    },
  ];
}

interface EnhancedGraphViewProps {
  items: Item[];
  links: Link[];
  isLoading?: boolean | undefined;
  projectId?: string | undefined;
  onNavigateToItem?: ((itemId: string) => void) | undefined;
}

function EnhancedGraphViewComponent({
  items,
  links,
  isLoading = false,
  onNavigateToItem,
}: EnhancedGraphViewProps): JSX.Element {
  // State
  const [perspective, setPerspective] = useState<GraphPerspective>('all');
  const [layout, setLayout] = useState<LayoutType>('cose');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [showDetailPanel, setShowDetailPanel] = useState(true);
  const [showUITree, setShowUITree] = useState(false);

  // Refs
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  // Build enhanced node data with perspective info
  const enhancedNodes = useMemo((): EnhancedNodeData[] => {
    const itemMap = new Map(items.map((item) => [item.id, item]));

    // Count connections for each item
    const incomingCount = new Map<string, number>();
    const outgoingCount = new Map<string, number>();
    const connectionsByType = new Map<string, Record<LinkType, number>>();

    for (const link of links) {
      // Incoming
      incomingCount.set(link.targetId, (incomingCount.get(link.targetId) ?? 0) + 1);
      // Outgoing
      outgoingCount.set(link.sourceId, (outgoingCount.get(link.sourceId) ?? 0) + 1);

      // By type
      if (!connectionsByType.has(link.targetId)) {
        connectionsByType.set(link.targetId, getLinkTypeCountMap());
      }
      const targetTypes = connectionsByType.get(link.targetId);
      if (targetTypes !== undefined) {
        targetTypes[link.type] = (targetTypes[link.type] ?? 0) + 1;
      }

      if (!connectionsByType.has(link.sourceId)) {
        connectionsByType.set(link.sourceId, getLinkTypeCountMap());
      }
      const sourceTypes = connectionsByType.get(link.sourceId);
      if (sourceTypes !== undefined) {
        sourceTypes[link.type] = (sourceTypes[link.type] ?? 0) + 1;
      }
    }

    return items.map((item): EnhancedNodeData => {
      const itemType = (
        toNonEmptyString(item.type) ??
        toNonEmptyString(item.view) ??
        'item'
      ).toLowerCase();
      const incoming = incomingCount.get(item.id) ?? 0;
      const outgoing = outgoingCount.get(item.id) ?? 0;
      const uiPreview = buildNodeUIPreview(item);

      return {
        connections: {
          byType: connectionsByType.get(item.id) ?? getLinkTypeCountMap(),
          incoming,
          outgoing,
          total: incoming + outgoing,
        },
        depth: getNodeDepth(item, itemMap),
        hasChildren: items.some((itemEntry) => itemEntry.parentId === item.id),
        id: item.id,
        item,
        label: toNonEmptyString(item.title) ?? 'Untitled',
        ...(item.parentId === undefined ? {} : { parentId: item.parentId }),
        perspective: TYPE_TO_PERSPECTIVE[itemType] ?? ['all'],
        status: item.status,
        type: itemType,
        ...(uiPreview === undefined ? {} : { uiPreview }),
      };
    });
  }, [items, links]);

  // Filter nodes by perspective
  const filteredNodes = useMemo((): EnhancedNodeData[] => {
    if (perspective === 'all') {
      return enhancedNodes;
    }

    const config = getPerspectiveConfig(perspective);
    if (!config || config.includeTypes.length === 0) {
      return enhancedNodes;
    }

    return enhancedNodes.filter((node): boolean => {
      const nodeType = node.type.toLowerCase();
      // Check if type is in includeTypes or if node has this perspective
      return (
        config.includeTypes.some(
          (includedType): boolean =>
            nodeType.includes(includedType) || includedType.includes(nodeType),
        ) || node.perspective.includes(perspective)
      );
    });
  }, [enhancedNodes, perspective]);

  // Filter links to only include those between filtered nodes
  const filteredLinks = useMemo((): Link[] => {
    const nodeIds = new Set(filteredNodes.map((nodeEntry) => nodeEntry.id));
    return links.filter((link) => nodeIds.has(link.sourceId) && nodeIds.has(link.targetId));
  }, [links, filteredNodes]);

  // Count items by perspective for the selector
  const perspectiveCounts = useMemo((): Record<GraphPerspective, number> => {
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
      for (const nodePerspective of node.perspective) {
        if (nodePerspective !== 'all') {
          counts[nodePerspective] = (counts[nodePerspective] ?? 0) + 1;
        }
      }
    }

    return counts;
  }, [enhancedNodes]);

  // Selected node data
  const selectedNode = useMemo((): EnhancedNodeData | null => {
    if (selectedNodeId === null || selectedNodeId.length === 0) {
      return null;
    }
    return filteredNodes.find((nodeEntry) => nodeEntry.id === selectedNodeId) ?? null;
  }, [filteredNodes, selectedNodeId]);

  // Links for selected node
  const { incomingLinks, outgoingLinks, relatedItems } = useMemo((): {
    incomingLinks: Link[];
    outgoingLinks: Link[];
    relatedItems: Item[];
  } => {
    if (selectedNodeId === null || selectedNodeId.length === 0) {
      return { incomingLinks: [], outgoingLinks: [], relatedItems: [] };
    }

    const incoming = links.filter((linkEntry) => linkEntry.targetId === selectedNodeId);
    const outgoing = links.filter((linkEntry) => linkEntry.sourceId === selectedNodeId);

    const relatedIds = new Set([
      ...incoming.map((linkEntry) => linkEntry.sourceId),
      ...outgoing.map((linkEntry) => linkEntry.targetId),
    ]);

    return {
      incomingLinks: incoming,
      outgoingLinks: outgoing,
      relatedItems: items.filter((itemEntry) => relatedIds.has(itemEntry.id)),
    };
  }, [selectedNodeId, links, items]);

  // Initialize Cytoscape
  const initCytoscape = useCallback((): void => {
    if (containerRef.current === null || filteredNodes.length === 0) {
      return;
    }

    // Destroy existing instance
    if (cyRef.current !== null) {
      cyRef.current.destroy();
    }

    const cytoscapeNodes = filteredNodes.map((node) => createCytoscapeNode(node));
    const cytoscapeEdges = filteredLinks.map((link) => createCytoscapeEdge(link));
    const perspectiveColor = getPerspectiveConfig(perspective)?.color;

    const cyInstance = cytoscape({
      container: containerRef.current,
      elements: [...cytoscapeNodes, ...cytoscapeEdges],
      layout: getGraphLayoutOptions(layout),
      maxZoom: 4,
      minZoom: 0.1,
      style: getGraphStyles(perspectiveColor),
      wheelSensitivity: 0.3,
    } as cytoscape.CytoscapeOptions);
    cyRef.current = cyInstance;

    // Event handlers
    cyInstance.on('tap', 'node', (event: EventObject): void => {
      const tappedNode = event.target as NodeSingular;
      const nodeId = tappedNode.id();
      setSelectedNodeId(nodeId);
      setShowDetailPanel(true);

      // Highlight connected nodes and edges
      const neighborhood = tappedNode.closedNeighborhood();
      cyInstance.elements().addClass('faded');
      neighborhood.removeClass('faded');
      neighborhood.addClass('highlighted');
    });

    cyInstance.on('tap', (event: EventObject): void => {
      if (event.target === cyInstance) {
        setSelectedNodeId(null);
        cyInstance.elements().removeClass('faded highlighted');
      }
    });

    // Fit to viewport
    cyInstance.fit(undefined, FIT_PADDING);
  }, [filteredNodes, filteredLinks, layout, perspective]);

  // Effect to initialize/reinitialize cytoscape
  useEffect((): (() => void) => {
    initCytoscape();
    return (): void => {
      cyRef.current?.destroy();
    };
  }, [initCytoscape]);

  const activePerspectiveConfig = useMemo(
    (): PerspectiveConfig | undefined => getPerspectiveConfig(perspective),
    [perspective],
  );

  const activePerspectiveBadgeStyle = useMemo<CSSProperties | undefined>(
    () =>
      activePerspectiveConfig === undefined
        ? {}
        : {
            backgroundColor: `${activePerspectiveConfig.color}20`,
            borderColor: activePerspectiveConfig.color,
          },
    [activePerspectiveConfig],
  );

  const graphContainerStyle = useMemo<CSSProperties>(
    () => ({ height: GRAPH_CONTAINER_HEIGHT }),
    [],
  );

  const legendTypeItems = useMemo(
    (): { colorStyle: CSSProperties; displayType: string; type: string }[] =>
      Object.entries(ENHANCED_TYPE_COLORS)
        .filter(([type]) => filteredNodes.some((nodeEntry) => nodeEntry.type === type))
        .slice(0, 10)
        .map(([type, color]) => ({
          colorStyle: { backgroundColor: color } as CSSProperties,
          displayType: type.replaceAll('_', ' '),
          type,
        })),
    [filteredNodes],
  );

  const legendLinkItems = useMemo(
    (): { lineStyle: CSSProperties; type: string }[] =>
      Object.entries(LINK_STYLES)
        .slice(0, 5)
        .map(([type, style]) => ({
          lineStyle: {
            backgroundColor: style.color,
            borderStyle: style.dashed ? 'dashed' : 'solid',
          } as CSSProperties,
          type,
        })),
    [],
  );

  // Handle layout change
  const handleLayoutChange = useCallback((newLayout: LayoutType): void => {
    setLayout(newLayout);
  }, []);

  const handleLayoutSelect = useCallback(
    (selectedLayoutValue: string): void => {
      handleLayoutChange(selectedLayoutValue as LayoutType);
    },
    [handleLayoutChange],
  );

  // Handle perspective change
  const handlePerspectiveChange = useCallback((newPerspective: GraphPerspective): void => {
    setPerspective(newPerspective);
    setSelectedNodeId(null);

    // Auto-show UI tree for UI perspective
    setShowUITree(newPerspective === 'ui');

    // Update layout preference
    const config = getPerspectiveConfig(newPerspective);
    if (config?.layoutPreference !== undefined) {
      setLayout(config.layoutPreference);
    }
  }, []);

  // Zoom controls
  const handleZoomIn = useCallback((): void => {
    const cyInstance = cyRef.current;
    if (cyInstance === null) {
      return;
    }
    cyInstance.zoom(cyInstance.zoom() * ZOOM_STEP);
  }, []);

  const handleZoomOut = useCallback((): void => {
    const cyInstance = cyRef.current;
    if (cyInstance === null) {
      return;
    }
    cyInstance.zoom(cyInstance.zoom() / ZOOM_STEP);
  }, []);

  const clearHighlightState = useCallback((): void => {
    cyRef.current?.elements().removeClass('faded highlighted');
  }, []);

  const handleFit = useCallback((): void => {
    cyRef.current?.fit(undefined, FIT_PADDING);
    cyRef.current?.elements().removeClass('faded highlighted');
  }, []);

  const handleReset = useCallback((): void => {
    setPerspective('all');
    setLayout('cose');
    setSelectedNodeId(null);
    setShowUITree(false);
    clearHighlightState();
  }, [clearHighlightState]);

  // Export
  const handleExport = useCallback((): void => {
    if (cyRef.current === null) {
      return;
    }
    const png = cyRef.current.png({ bg: '#1a1a2e', full: true, scale: 2 });
    const link = document.createElement('a');
    link.download = `graph-${perspective}-${new Date().toISOString()}.png`;
    link.href = png;
    link.click();
  }, [perspective]);

  // Focus on specific node
  const handleFocusNode = useCallback((nodeId: string): void => {
    const node = cyRef.current?.getElementById(nodeId);
    if (node !== undefined && node.length > 0) {
      setSelectedNodeId(nodeId);

      // Center on node
      cyRef.current?.animate({
        center: { eles: node },
        duration: 300,
        zoom: FOCUS_ZOOM,
      });

      // Highlight
      cyRef.current?.elements().addClass('faded');
      const neighborhood = node.closedNeighborhood();
      neighborhood.removeClass('faded');
      neighborhood.addClass('highlighted');
    }
  }, []);

  const handleToggleUITree = useCallback((): void => {
    setShowUITree((currentValue) => !currentValue);
  }, []);

  const handleToggleDetailPanel = useCallback((): void => {
    setShowDetailPanel((currentValue) => !currentValue);
  }, []);

  const handleCloseNodeDetailPanel = useCallback((): void => {
    setSelectedNodeId(null);
    clearHighlightState();
  }, [clearHighlightState]);

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
            Multi-perspective visualization of item relationships
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
            {filteredNodes.length} items \u00b7 {filteredLinks.length} connections
          </p>
        </div>

        {/* Quick stats */}
        <div className='flex items-center gap-3'>
          {perspective !== 'all' && (
            <Badge variant='outline' className='px-3 py-1' style={activePerspectiveBadgeStyle}>
              {activePerspectiveConfig?.label}
            </Badge>
          )}
        </div>
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
            <Select value={layout} onValueChange={handleLayoutSelect}>
              <SelectTrigger className='h-9 w-[160px]'>
                <Layers className='mr-2 h-4 w-4' />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='cose'>Force-directed</SelectItem>
                <SelectItem value='breadthfirst'>Hierarchical</SelectItem>
                <SelectItem value='circle'>Circular</SelectItem>
                <SelectItem value='elk'>Directed Graph</SelectItem>
              </SelectContent>
            </Select>

            <Separator orientation='vertical' className='h-6' />

            {/* UI Tree toggle (for UI perspective) */}
            <Button
              variant={showUITree ? 'default' : 'outline'}
              size='sm'
              onClick={handleToggleUITree}
              className='h-9'
            >
              <LayoutGrid className='mr-2 h-4 w-4' />
              UI Library
            </Button>

            {/* Detail panel toggle */}
            <Button variant='ghost' size='sm' onClick={handleToggleDetailPanel} className='h-9'>
              {showDetailPanel ? (
                <PanelRightClose className='h-4 w-4' />
              ) : (
                <PanelRight className='h-4 w-4' />
              )}
            </Button>
          </div>

          <div className='flex items-center gap-2'>
            {/* Zoom controls */}
            <div className='flex items-center gap-1 rounded-md border p-1'>
              <Button variant='ghost' size='sm' onClick={handleZoomIn} className='h-7 w-7 p-0'>
                <ZoomIn className='h-4 w-4' />
              </Button>
              <Button variant='ghost' size='sm' onClick={handleZoomOut} className='h-7 w-7 p-0'>
                <ZoomOut className='h-4 w-4' />
              </Button>
              <Button variant='ghost' size='sm' onClick={handleFit} className='h-7 w-7 p-0'>
                <Maximize2 className='h-4 w-4' />
              </Button>
              <Button variant='ghost' size='sm' onClick={handleReset} className='h-7 w-7 p-0'>
                <RotateCcw className='h-4 w-4' />
              </Button>
            </div>

            <Button variant='outline' size='sm' onClick={handleExport} className='h-9'>
              <Download className='mr-2 h-4 w-4' />
              Export
            </Button>
          </div>
        </div>
      </Card>

      {/* Main content area */}
      <div className='flex gap-4' style={graphContainerStyle}>
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
          <div ref={containerRef} className='bg-background h-full w-full' />
        </Card>

        {/* Node Detail Panel (right) */}
        {showDetailPanel && selectedNode !== null && (
          <NodeDetailPanel
            node={selectedNode}
            relatedItems={relatedItems}
            incomingLinks={incomingLinks}
            outgoingLinks={outgoingLinks}
            onClose={handleCloseNodeDetailPanel}
            onNavigateToItem={onNavigateToItem ?? NOOP_NAVIGATE_TO_ITEM}
            onFocusNode={handleFocusNode}
          />
        )}
      </div>

      {/* Legend */}
      <Card className='p-3'>
        <div className='flex flex-wrap items-center gap-4 text-xs'>
          <span className='text-muted-foreground font-medium'>Types:</span>
          {legendTypeItems.map((entry) => (
            <div key={entry.type} className='flex items-center gap-1.5'>
              <div className='h-3 w-6 rounded' style={entry.colorStyle} />
              <span className='capitalize'>{entry.displayType}</span>
            </div>
          ))}

          <Separator orientation='vertical' className='h-4' />

          <span className='text-muted-foreground font-medium'>Links:</span>
          {legendLinkItems.map((entry) => (
            <div key={entry.type} className='flex items-center gap-1.5'>
              <div className='h-0.5 w-6' style={entry.lineStyle} />
              <span>{entry.type.replaceAll('_', ' ')}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

export const EnhancedGraphView = memo(EnhancedGraphViewComponent);
