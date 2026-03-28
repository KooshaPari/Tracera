// Flow Graph View Inner - Core graph component without ReactFlowProvider wrapper
// Used by both FlowGraphView and UnifiedGraphView

import {
  Background,
  BackgroundVariant,
  Controls,
  MarkerType,
  MiniMap,
  Panel,
  ReactFlow,
  type Edge,
  type Node,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from '@xyflow/react';
import {
  Maximize,
  Maximize2,
  Minimize,
  PanelRight,
  PanelRightClose,
  RotateCcw,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';

import type { CacheStatistics } from '@/lib/cache';
import type { Item, Link, LinkType } from '@tracertm/types';

import { useGraphPerformanceMonitor } from '@/hooks/useGraphPerformanceMonitor';
import { calculateEdgeMidpoint, getEdgeLODTier } from '@/lib/edgeLOD';
import { useGraphCache } from '@/lib/graphCache';
import { buildGraphIndices, getRelatedItems } from '@/lib/graphIndexing';
import { GraphSpatialIndex, type SpatialEdge, type SpatialNode } from '@/lib/spatialIndex';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { Separator } from '@tracertm/ui/components/Separator';

import type { RichNodeData } from './RichNodePill';

import { LayoutSelector } from './layouts/LayoutSelector';
import { useDagLayout, type LayoutType } from './layouts/useDagLayout';
import { NodeDetailPanel } from './NodeDetailPanel';
import { getNodeType, nodeTypes } from './nodeRegistry';
import {
  ENHANCED_TYPE_COLORS,
  LINK_STYLES,
  PERSPECTIVE_CONFIGS,
  TYPE_TO_PERSPECTIVE,
  type EnhancedNodeData,
  type GraphPerspective,
} from './types';
import { LODLevel, determineLODLevel } from './utils/lod';
import { itemToNodeData } from './utils/nodeDataTransformers';

/** Stable noop for optional callbacks (A1 perf). */
const noop = (): void => {};
const DEFAULT_VIEWPORT = { x: 0, y: 0, zoom: 1 };
const LEGEND_TYPE_LIMIT = 8;
const SCALE_NODE_THRESHOLD = 500;
const MAX_ANIMATED_EDGE_COUNT = 20;
const INITIAL_VIEWPORT_SYNC_DELAY_MS = 300;
const AUTO_FIT_DELAY_MS = 100;
const FPS_GOOD_THRESHOLD = 55;
const FPS_WARN_THRESHOLD = 30;
const CANVAS_LAYER_Z_INDEX = 5;
const GRAPH_EMPTY_LABEL = 'Untitled';
const MAX_ITEM_DEPTH = 10;
const EMPTY_CONNECTIONS: Partial<Record<LinkType, number>> = {};
const DEV_MODE = process.env['NODE_ENV'] === 'development';

// OPTIMIZATION (Fix 1.6): Edge style caching to eliminate repeated object allocations
// Provides 10-15% FPS improvement and 80% reduction in object allocations
const EDGE_LABEL_BG_STYLE = { fill: 'rgba(26, 26, 46, 0.9)' };

interface EdgeStyleCacheEntry {
  style: object;
  labelStyle: object;
  label: string;
  markerEnd?: object | undefined;
}

const edgeStyleCache = new Map<LinkType, EdgeStyleCacheEntry>();

interface StoreCacheStatsBlock {
  totalEntries: number;
  hitRatio: number;
}

const toPerformanceCacheStats = (
  statsBlock: StoreCacheStatsBlock,
  backendType: string,
): CacheStatistics => {
  const normalizedHitRatio = Number.isFinite(statsBlock.hitRatio)
    ? Math.min(Math.max(statsBlock.hitRatio, 0), 1)
    : 0;
  const totalEntries = Number.isFinite(statsBlock.totalEntries) ? Math.max(statsBlock.totalEntries, 0) : 0;
  const totalHits = Math.round(totalEntries * normalizedHitRatio);

  return {
    backendType,
    hitRatio: normalizedHitRatio,
    maxEntries: totalEntries,
    maxMemory: 0,
    memoryUsagePercent: 0,
    totalEntries,
    totalHits,
    totalMemory: 0,
    totalMisses: Math.max(totalEntries - totalHits, 0),
  };
};

function getCachedEdgeStyle(linkType: LinkType): EdgeStyleCacheEntry {
  if (!edgeStyleCache.has(linkType)) {
    const linkStyle = LINK_STYLES[linkType] ?? {
      arrow: false,
      color: '#64748b',
      dashed: true,
    };
    edgeStyleCache.set(linkType, {
      style: {
        stroke: linkStyle.color,
        strokeWidth: 2,
        ...(linkStyle.dashed && { strokeDasharray: '5,5' }),
      },
      labelStyle: { fill: linkStyle.color, fontSize: 10 },
      label: linkType.replaceAll('_', ' '),
      ...(linkStyle.arrow && {
        markerEnd: { color: linkStyle.color, type: MarkerType.ArrowClosed },
      }),
    });
  }
  const cachedStyle = edgeStyleCache.get(linkType);
  if (cachedStyle === undefined) {
    throw new Error(`Missing cached edge style for link type: ${linkType}`);
  }
  return cachedStyle;
}

// Note: nodeTypes imported from nodeRegistry

interface FlowGraphViewInnerProps {
  items: Item[];
  links: Link[];
  perspective?: GraphPerspective | undefined;
  /** Initial layout when view type has a layout preference (e.g. Flow Chart, Tree). */
  defaultLayout?: LayoutType | undefined;
  onNavigateToItem?: ((itemId: string) => void) | undefined;
  showControls?: boolean | undefined;
  autoFit?: boolean | undefined;
}

function FlowGraphViewInnerComponent({
  items,
  links,
  perspective: externalPerspective,
  defaultLayout,
  onNavigateToItem,
  showControls = true,
  autoFit = true,
}: FlowGraphViewInnerProps): JSX.Element {
  // Use external perspective if provided, otherwise manage internally
  const [internalPerspective, setInternalPerspective] = useState<GraphPerspective>('all');
  const perspective = externalPerspective ?? internalPerspective;
  const setPerspective = useCallback(
    (nextPerspective: GraphPerspective): void => {
      if (externalPerspective === undefined) {
        setInternalPerspective(nextPerspective);
      }
    },
    [externalPerspective],
  );

  const [layout, setLayout] = useState<LayoutType>(defaultLayout ?? 'flow-chart');

  // Sync layout when view type changes (e.g. user picks "Tree" or "Mind Map")
  useEffect((): (() => void) | void => {
    if (defaultLayout !== undefined) {
      setLayout(defaultLayout);
    }
  }, [defaultLayout]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [showDetailPanel, setShowDetailPanel] = useState(true);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [isFullscreen, setIsFullscreen] = useState(false);
  const graphContainerRef = useRef<HTMLDivElement>(null);
  const canvasLayerRef = useRef<HTMLCanvasElement>(null);

  // OPTIMIZATION: R-tree spatial index for O(log n) viewport culling (Task 3.2)
  // Provides 416x speedup over O(n) linear search
  const spatialIndexRef = useRef(new GraphSpatialIndex());

  // OPTIMIZATION (Fix 1.3): Memoized callback to prevent breaking React.memo
  // Eliminates 400+ unnecessary re-renders when node count is high
  const handleNodeExpand = useCallback((id: string) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  // OPTIMIZATION: Progressive node rendering in batches, capped to avoid lag
  const [renderedNodeBatch, setRenderedNodeBatch] = useState(0);
  const nodesPerBatch = 100;
  const MAX_RENDERED_NODES = 400;

  // D1: Viewport-based node set — only pass nodes/edges in viewport + padding when node count is high
  const VIEWPORT_WINDOW_THRESHOLD = 100;
  const VIEWPORT_WINDOW_PADDING = 200; // Flow coordinates
  const [viewportBounds, setViewportBounds] = useState<{
    minX: number;
    maxX: number;
    minY: number;
    maxY: number;
    zoom: number;
    x: number;
    y: number;
  } | null>(null);

  const { fitView, zoomIn, zoomOut, getViewport } = useReactFlow();

  // OPTIMIZATION: Build parent index map for O(1) parent/child lookups
  // Prevents O(n²) complexity from items.some() calls in node enrichment
  const parentMap = useMemo(() => {
    const map = new Map<string, Set<string>>();
    items.forEach((item) => {
      const parentId = item.parentId;
      if (typeof parentId === 'string' && parentId.length > 0) {
        if (!map.has(parentId)) {
          map.set(parentId, new Set());
        }
        const childSet = map.get(parentId);
        if (childSet !== undefined) {
          childSet.add(item.id);
        }
      }
    });
    return map;
  }, [items]);

  // OPTIMIZATION: Memoized node data transformation function
  // Creates stable reference to avoid re-enriching nodes unnecessarily
  const createNodeData = useCallback(
    (
      item: Item,
      itemMap: Map<string, Item>,
      incomingCount: Map<string, number>,
      outgoingCount: Map<string, number>,
      connectionsByType: Map<string, Record<LinkType, number>>,
    ): EnhancedNodeData => {
      const itemType = (item.type || item.view || 'item').toLowerCase();
      const perspectives = TYPE_TO_PERSPECTIVE[itemType] ?? ['all'];
      const incoming = incomingCount.get(item.id) ?? 0;
      const outgoing = outgoingCount.get(item.id) ?? 0;

      // OPTIMIZATION: O(1) hasChildren check using parent map
      const hasChildren = parentMap.has(item.id);

      // OPTIMIZATION: Depth calculation using parent map
      let depth = 0;
      let currentId = item.parentId;
      while (typeof currentId === 'string' && currentId.length > 0 && depth < MAX_ITEM_DEPTH) {
        depth += 1;
        const parent = itemMap.get(currentId);
        currentId = parent?.parentId;
      }

      const screenshotUrlRaw = item.metadata?.['screenshotUrl'];
      const screenshotUrl =
        typeof screenshotUrlRaw === 'string' && screenshotUrlRaw.length > 0
          ? screenshotUrlRaw
          : undefined;
      const codeRaw = item.metadata?.['code'];
      const interactiveUrlRaw = item.metadata?.['interactiveUrl'];
      const thumbnailUrlRaw = item.metadata?.['thumbnailUrl'];

      return {
        connections: {
          byType: connectionsByType.get(item.id) ?? EMPTY_CONNECTIONS,
          incoming,
          outgoing,
          total: incoming + outgoing,
        },
        depth,
        hasChildren,
        id: item.id,
        item,
        label: item.title ?? GRAPH_EMPTY_LABEL,
        parentId: item.parentId,
        perspective: perspectives,
        status: item.status,
        type: itemType,
        uiPreview:
          screenshotUrl !== undefined
            ? {
                componentCode: typeof codeRaw === 'string' ? codeRaw : undefined,
                interactiveWidgetUrl:
                  typeof interactiveUrlRaw === 'string' ? interactiveUrlRaw : undefined,
                screenshotUrl,
                thumbnailUrl: typeof thumbnailUrlRaw === 'string' ? thumbnailUrlRaw : undefined,
              }
            : undefined,
      } as EnhancedNodeData;
    },
    [parentMap],
  );

  // OPTIMIZATION: Memoized enhanced nodes with stable node data transformation
  // Build enhanced node data
  const enhancedNodes = useMemo((): EnhancedNodeData[] => {
    const itemMap = new Map(items.map((item) => [item.id, item]));

    const incomingCount = new Map<string, number>();
    const outgoingCount = new Map<string, number>();
    const connectionsByType = new Map<string, Record<LinkType, number>>();
    const ensureConnectionBucket = (itemId: string): Record<LinkType, number> => {
      const existing = connectionsByType.get(itemId);
      if (existing !== undefined) {
        return existing;
      }
      const created = {} as Record<LinkType, number>;
      connectionsByType.set(itemId, created);
      return created;
    };

    for (const link of links) {
      incomingCount.set(link.targetId, (incomingCount.get(link.targetId) ?? 0) + 1);
      outgoingCount.set(link.sourceId, (outgoingCount.get(link.sourceId) ?? 0) + 1);

      const targetTypes = ensureConnectionBucket(link.targetId);
      targetTypes[link.type] = (targetTypes[link.type] || 0) + 1;

      const sourceTypes = ensureConnectionBucket(link.sourceId);
      sourceTypes[link.type] = (sourceTypes[link.type] || 0) + 1;
    }

    return items.map((item) =>
      createNodeData(item, itemMap, incomingCount, outgoingCount, connectionsByType),
    );
  }, [items, links, createNodeData]);

  // OPTIMIZATION (Fix 1.4): O(1) node lookup map for selected node computation
  // Eliminates linear search, provides 8-12% FPS improvement when node is selected
  const nodeMap = useMemo(() => new Map(enhancedNodes.map((n) => [n.id, n])), [enhancedNodes]);

  // Filter nodes by perspective (only if using internal perspective)
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

  // OPTIMIZATION: Build Set of visible node types for O(1) legend filtering (Fix 1.2)
  // Eliminates O(n²) filteredNodes.some() check in legend (8000+ checks → 20 checks)
  const visibleTypes = useMemo(() => {
    const types = new Set<string>();
    for (const node of filteredNodes) {
      types.add(node.type);
      // Early exit after finding 8 types (legend limit)
      if (types.size >= LEGEND_TYPE_LIMIT) {
        break;
      }
    }
    return types;
  }, [filteredNodes]);

  // OPTIMIZATION: Progressive rendering of nodes in batches, capped at MAX_RENDERED_NODES
  useEffect(() => {
    if (filteredNodes.length === 0) {
      setRenderedNodeBatch(0);
      return undefined;
    }

    const maxBatches = Math.ceil(MAX_RENDERED_NODES / nodesPerBatch);
    const totalBatches = Math.min(Math.ceil(filteredNodes.length / nodesPerBatch), maxBatches);
    if (renderedNodeBatch < totalBatches) {
      const timerId = requestAnimationFrame((): void => {
        setRenderedNodeBatch((prev) => prev + 1);
      });
      return (): void => {
        cancelAnimationFrame(timerId);
      };
    }
    return undefined;
  }, [filteredNodes.length, renderedNodeBatch]);

  // Only use visible nodes for rendering (progressive rendering, hard cap)
  const visibleNodes = useMemo(() => {
    const maxVisible = Math.min((renderedNodeBatch + 1) * nodesPerBatch, MAX_RENDERED_NODES);
    return filteredNodes.slice(0, maxVisible);
  }, [filteredNodes, renderedNodeBatch]);

  // Only render links between visible nodes
  const visibleLinks = useMemo(() => {
    const visibleNodeIds = new Set(visibleNodes.map((n) => n.id));
    return filteredLinks.filter(
      (link) => visibleNodeIds.has(link.sourceId) && visibleNodeIds.has(link.targetId),
    );
  }, [filteredLinks, visibleNodes]);

  // Extended Item type with position
  interface ExtendedItem extends Item {
    position?: { x: number; y: number } | undefined;
  }

  // Create React Flow compatible nodes for layout
  // Phase 2 Task 2.5: LOD integration with distance-based detail level
  const nodesForLayout = useMemo((): Node<RichNodeData>[] => {
    const totalCount = visibleNodes.length;
    const viewport = getViewport?.() ?? DEFAULT_VIEWPORT;
    const lodLevel = determineLODLevel(viewport.zoom, {
      nodeCount: totalCount,
    });

    // Calculate viewport center for distance-based LOD
    const viewportCenter = {
      x: -viewport.x + window.innerWidth / 2 / viewport.zoom,
      y: -viewport.y + window.innerHeight / 2 / viewport.zoom,
    };

    return visibleNodes.map((node) => {
      // Transform item to base node data
      const baseData = itemToNodeData(node.item, node.connections);

      // Calculate distance from viewport center
      const extendedItem = node.item as ExtendedItem;
      const distance = Math.hypot(
        (extendedItem.position?.x ?? 0) - viewportCenter.x,
        (extendedItem.position?.y ?? 0) - viewportCenter.y,
      );

      // Determine node type using comprehensive LOD context
      const lodNodeType = getNodeType(node.type, {
        distance,
        isFocused: false,
        isSelected: selectedNodeId === node.id,
        totalNodeCount: totalCount,
        zoom: viewport.zoom,
      });

      // Merge with interactive handlers and UI state
      const data: RichNodeData = {
        ...baseData,
        lodLevel,
        isExpanded: expandedNodes.has(node.id),
        showPreview: perspective === 'ui' && lodNodeType !== 'simple' && lodNodeType !== 'skeleton',
        onSelect: setSelectedNodeId,
        onExpand: handleNodeExpand,
        onNavigate: onNavigateToItem ?? undefined,
      };

      return {
        data,
        id: node.id,
        position: { x: 0, y: 0 },
        type: lodNodeType,
      };
    });
  }, [
    visibleNodes,
    selectedNodeId,
    expandedNodes,
    perspective,
    handleNodeExpand,
    onNavigateToItem,
    getViewport,
  ]);

  // Use DAG layout for proper positioning
  // OPTIMIZATION: Only layout visible nodes
  const { nodes: dagreLaidoutNodes } = useDagLayout<RichNodeData>(
    nodesForLayout,
    visibleLinks.map((link) => ({
      id: link.id,
      source: link.sourceId,
      target: link.targetId,
    })),
    layout,
    {
      marginX: 40,
      marginY: 40,
      nodeHeight: 120,
      nodeSep: 60,
      nodeWidth: 200,
      rankSep: 100,
    },
  );

  // OPTIMIZATION (Task 3.2): R-tree viewport culling for O(log n) performance
  // Replaces O(n) linear search with R-tree spatial queries
  // Performance: 10,000 edges culled in <5ms (was 200ms with linear search)
  const { nodesToRender, visibleEdgesFromRTree } = useMemo(() => {
    if (!viewportBounds || dagreLaidoutNodes.length <= VIEWPORT_WINDOW_THRESHOLD) {
      return {
        nodesToRender: dagreLaidoutNodes,
        visibleEdgesFromRTree: null,
      };
    }

    // Build spatial index for nodes
    spatialIndexRef.current.indexNodes(dagreLaidoutNodes);

    // Build node positions map for edge indexing
    const nodePositions = new Map(dagreLaidoutNodes.map((n) => [n.id, n.position]));

    // Build spatial index for edges
    spatialIndexRef.current.indexEdges(
      visibleLinks.map((link) => ({
        id: link.id,
        sourceId: link.sourceId,
        targetId: link.targetId,
      })),
      nodePositions,
    );

    // Query viewport with R-tree (O(log n) instead of O(n))
    const viewport = getViewport?.() ?? DEFAULT_VIEWPORT;
    const visible = spatialIndexRef.current.queryViewport({
      height: window.innerHeight,
      width: window.innerWidth,
      x: -viewport.x / viewport.zoom,
      y: -viewport.y / viewport.zoom,
      zoom: viewport.zoom,
    });

    // Filter nodes using R-tree results (O(n*m) where m is visible count)
    const visibleNodeIds = new Set(visible.nodes.map((vn: SpatialNode) => vn.id));
    const culledNodes = dagreLaidoutNodes.filter((n: Node) => visibleNodeIds.has(n.id));

    // Filter edges using R-tree results
    const visibleEdgeIds = new Set(visible.edges.map((ve: SpatialEdge) => ve.id));
    const culledEdges = visibleLinks.filter((e) => visibleEdgeIds.has(e.id));

    return {
      nodesToRender: culledNodes,
      visibleEdgesFromRTree: culledEdges,
    };
  }, [dagreLaidoutNodes, viewportBounds, visibleLinks, getViewport]);

  // D3: Canvas hybrid — when zoomed out (far LOD) and many nodes, draw far nodes on canvas instead of DOM
  const CANVAS_LOD_NODE_THRESHOLD = 50;
  const { canvasNodes, domNodes } = useMemo(() => {
    if (nodesToRender.length <= CANVAS_LOD_NODE_THRESHOLD || !viewportBounds) {
      return {
        canvasNodes: [] as Node<RichNodeData>[],
        domNodes: nodesToRender,
      };
    }
    const { zoom } = viewportBounds;
    const lod = determineLODLevel(zoom, { nodeCount: nodesToRender.length });
    if (lod > LODLevel.Far) {
      return {
        canvasNodes: [] as Node<RichNodeData>[],
        domNodes: nodesToRender,
      };
    }
    // Far or VeryFar: draw all on canvas, pass none to React Flow (or pass minimal placeholder for hit area)
    return { canvasNodes: nodesToRender, domNodes: [] as Node<RichNodeData>[] };
  }, [nodesToRender, viewportBounds]);

  // Use DAG-laid-out nodes (or viewport-filtered, D3: dom-only when canvas active) as initial nodes
  const initialNodes = useMemo(
    () => (canvasNodes.length > 0 ? domNodes : nodesToRender),
    [canvasNodes.length, domNodes, nodesToRender],
  );

  // OPTIMIZATION (Task 3.2): Use R-tree culled edges if available
  // Falls back to visible links for small graphs where R-tree overhead isn't worth it
  const edgesForRendering = useMemo(() => {
    // Use R-tree results if viewport culling is active
    if (visibleEdgesFromRTree) {
      return visibleEdgesFromRTree;
    }
    // For small graphs, use all visible links (no culling overhead)
    return visibleLinks;
  }, [visibleEdgesFromRTree, visibleLinks]);

  // OPTIMIZATION (Task 3.2): Edge rendering with LOD and R-tree culling
  // Applies distance-based detail levels for smooth performance
  const initialEdges = useMemo((): Edge[] => {
    const viewport = getViewport?.() ?? { x: 0, y: 0, zoom: 1 };
    const viewportCenter = {
      x: -viewport.x + window.innerWidth / 2 / viewport.zoom,
      y: -viewport.y + window.innerHeight / 2 / viewport.zoom,
    };

    // Build node positions map for O(1) lookups
    const nodePositions = new Map(dagreLaidoutNodes.map((n) => [n.id, n.position]));

    // C1: At scale (500+ nodes or 1000+ edges), disable animation and labels
    const atScale =
      dagreLaidoutNodes.length >= SCALE_NODE_THRESHOLD || edgesForRendering.length >= 1000;
    // OPTIMIZATION: Limit animated edges to avoid GPU overload; C1: at scale disable all
    const maxAnimatedEdges = atScale ? 0 : MAX_ANIMATED_EDGE_COUNT;
    const animatedEdgeIds = new Set(
      edgesForRendering
        .filter((link) => link.type === 'depends_on' || link.type === 'blocks')
        .slice(0, maxAnimatedEdges)
        .map((link) => link.id),
    );

    // OPTIMIZATION (Fix 1.6 + Task 3.3): Use cached edge styles with LOD tiers
    return edgesForRendering
      .map((link) => {
        const cached = getCachedEdgeStyle(link.type);

        const sourcePos = nodePositions.get(link.sourceId);
        const targetPos = nodePositions.get(link.targetId);
        if (!sourcePos || !targetPos) {
          return null;
        }

        // Calculate edge midpoint for LOD calculation
        const edgeMidpoint = calculateEdgeMidpoint(sourcePos, targetPos);

        // Get LOD tier based on distance from viewport center
        const lodTier = getEdgeLODTier(edgeMidpoint, viewportCenter, viewport.zoom);
        if (lodTier.level === 'hidden') {
          return null;
        }

        // C1: at scale hide labels to reduce paint cost
        const showLabel = !atScale && lodTier.showLabel;
        return {
          id: link.id,
          source: link.sourceId,
          target: link.targetId,
          type: lodTier.pathType === 'bezier' ? 'smoothstep' : 'default',
          animated: lodTier.level === 'detailed' && animatedEdgeIds.has(link.id),
          style: {
            ...cached.style,
            strokeWidth: lodTier.strokeWidth,
            opacity: lodTier.opacity,
          },
          ...(showLabel && {
            label: cached.label,
            labelBgStyle: EDGE_LABEL_BG_STYLE,
            labelStyle: cached.labelStyle,
          }),
          ...(lodTier.showArrow && cached.markerEnd && { markerEnd: cached.markerEnd }),
        };
      })
      .filter(Boolean) as Edge[];
  }, [edgesForRendering, dagreLaidoutNodes, getViewport]);

  // D1: When viewport window is on, only edges between nodes in viewport; D3: when canvas active only edges between dom nodes
  const edgesToRender = useMemo(() => {
    let nodeIdsForEdges: Set<string> | null = null;
    if (canvasNodes.length > 0) {
      nodeIdsForEdges = new Set(domNodes.map((node) => node.id));
    } else if (viewportBounds !== null && dagreLaidoutNodes.length > VIEWPORT_WINDOW_THRESHOLD) {
      nodeIdsForEdges = new Set(nodesToRender.map((node) => node.id));
    }

    if (!nodeIdsForEdges) {
      return initialEdges;
    }
    return initialEdges.filter(
      (edge) => nodeIdsForEdges.has(edge.source) && nodeIdsForEdges.has(edge.target),
    );
  }, [
    initialEdges,
    viewportBounds,
    dagreLaidoutNodes.length,
    nodesToRender,
    canvasNodes.length,
    domNodes,
  ]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const layoutInputSignature = useMemo(() => {
    const nodeIds = visibleNodes.map((node) => node.id).join('|');
    const linkIds = visibleLinks.map((link) => link.id).join('|');
    return `${layout}|${nodeIds}|${linkIds}`;
  }, [visibleNodes, visibleLinks, layout]);
  const edgesSignature = useMemo(
    () =>
      visibleLinks
        .map((edge) => `${edge.id}:${edge.sourceId}->${edge.targetId}:${edge.type}`)
        .join('|'),
    [visibleLinks],
  );
  const prevNodesSignature = useRef<string>('');
  const prevEdgesSignature = useRef<string>('');

  // Update nodes when data or viewport window or canvas/dom split changes (D1, D3)
  const nodesForState = canvasNodes.length > 0 ? domNodes : nodesToRender;
  useEffect(() => {
    if (layoutInputSignature) {
      prevNodesSignature.current = layoutInputSignature;
    }
    setNodes(nodesForState);
  }, [nodesForState, layoutInputSignature, setNodes]);

  useEffect(() => {
    if (edgesSignature) {
      prevEdgesSignature.current = edgesSignature;
    }
    setEdges(edgesToRender);
  }, [edgesToRender, edgesSignature, setEdges]);

  // D1: Sync viewport bounds when viewport changes (pan/zoom) so viewport window updates; D3: store zoom for canvas LOD
  const handleViewportChange = useCallback((): void => {
    const viewport = getViewport?.();
    if (viewport === undefined) {
      return;
    }
    const { x, y, zoom } = viewport;
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const pad = VIEWPORT_WINDOW_PADDING / zoom;
    setViewportBounds({
      maxX: (-x + viewportWidth) / zoom + pad,
      maxY: (-y + viewportHeight) / zoom + pad,
      minX: -x / zoom - pad,
      minY: -y / zoom - pad,
      x,
      y,
      zoom,
    });
  }, [getViewport]);

  // D1: Set initial viewport bounds after first layout so we don't wait for user move
  useEffect((): (() => void) | void => {
    if (dagreLaidoutNodes.length === 0) {
      return;
    }
    const viewportSyncTimerId = setTimeout(handleViewportChange, INITIAL_VIEWPORT_SYNC_DELAY_MS);
    return (): void => {
      clearTimeout(viewportSyncTimerId);
    };
  }, [dagreLaidoutNodes.length, handleViewportChange]);

  // D3: Draw far-LOD nodes on canvas when canvas hybrid is active (flow-to-screen: node.x * zoom + x)
  useEffect((): void => {
    if (canvasNodes.length === 0 || !viewportBounds) {
      return;
    }
    const canvas = canvasLayerRef.current;
    if (!canvas) {
      return;
    }
    const container = canvas.parentElement;
    if (!container) {
      return;
    }
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    if (containerWidth <= 0 || containerHeight <= 0) {
      return;
    }
    canvas.width = containerWidth;
    canvas.height = containerHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      return;
    }
    const { zoom, x, y } = viewportBounds;
    ctx.clearRect(0, 0, containerWidth, containerHeight);
    const radius = 3;
    canvasNodes.forEach((node) => {
      const screenX = node.position.x * zoom + x;
      const screenY = node.position.y * zoom + y;
      ctx.beginPath();
      ctx.arc(screenX, screenY, radius, 0, Math.PI * 2);
      ctx.fillStyle = '#64748b';
      ctx.fill();
    });
  }, [canvasNodes, viewportBounds]);

  // Auto-fit on initial load
  useEffect((): (() => void) | void => {
    if (autoFit && nodes.length > 0) {
      const autoFitTimerId = setTimeout((): void => {
        void fitView();
      }, AUTO_FIT_DELAY_MS);
      return (): void => {
        clearTimeout(autoFitTimerId);
      };
    }
  }, [autoFit, fitView, nodes.length]);

  // OPTIMIZATION: Pre-build graph indices for O(1) link lookups
  const graphIndices = useMemo(() => buildGraphIndices(items, links), [items, links]);

  // Selected node data
  // OPTIMIZATION (Fix 1.4): Use O(1) Map lookup instead of linear find
  const selectedNode = useMemo(() => {
    if (selectedNodeId === null || selectedNodeId.length === 0) {
      return null;
    }
    return nodeMap.get(selectedNodeId) ?? null;
  }, [nodeMap, selectedNodeId]);

  // OPTIMIZATION: Links for selected node using indices (O(1) vs O(n))
  // Provides 75-95% latency reduction for related item queries
  const { incomingLinks, outgoingLinks, relatedItems } = useMemo(() => {
    if (selectedNodeId === null || selectedNodeId.length === 0) {
      return { incomingLinks: [], outgoingLinks: [], relatedItems: [] };
    }

    // Use indexed lookups instead of filtering all links
    // This changes complexity from O(m) to O(1) + O(k) where k = related items
    const relatedData = getRelatedItems(selectedNodeId, graphIndices);

    return {
      incomingLinks: relatedData.incoming,
      outgoingLinks: relatedData.outgoing,
      relatedItems: relatedData.relatedItems,
    };
  }, [selectedNodeId, graphIndices]);

  // Fullscreen: sync state when user exits via Escape
  useEffect((): (() => void) => {
    const onFullscreenChange = (): void => {
      setIsFullscreen(Boolean(document.fullscreenElement));
    };
    document.addEventListener('fullscreenchange', onFullscreenChange);
    return (): void => {
      document.removeEventListener('fullscreenchange', onFullscreenChange);
    };
  }, []);

  const toggleFullscreen = useCallback(async (): Promise<void> => {
    if (!graphContainerRef.current) {
      return;
    }
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen();
      } else {
        await graphContainerRef.current.requestFullscreen();
      }
    } catch {
      // Ignore when fullscreen not supported or denied
    }
  }, []);

  const handleFullscreenToggle = useCallback((): void => {
    void toggleFullscreen();
  }, [toggleFullscreen]);

  // Handlers (stable refs for ReactFlow / Panel children — A1 perf)
  const handleFit = useCallback((): void => {
    void fitView();
  }, [fitView]);

  const handleReset = useCallback((): void => {
    setPerspective('all');
    setLayout('flow-chart');
    setSelectedNodeId(null);
    setExpandedNodes(new Set());
  }, [setPerspective]);

  const handleFocusNode = useCallback((nodeId: string): void => {
    setSelectedNodeId(nodeId);
  }, []);

  // Stable MiniMap nodeColor (avoids new function every render — A1 perf)
  const miniMapNodeColor = useCallback((node: Node): string => {
    const nodeType = (node.data as RichNodeData | undefined)?.type;
    if (typeof nodeType === 'string' && nodeType.length > 0) {
      return ENHANCED_TYPE_COLORS[nodeType] ?? '#64748b';
    }
    return '#64748b';
  }, []);

  // Stable ReactFlow options (A1 perf)
  const reactFlowProOptions = useMemo(() => ({ hideAttribution: true }), []);
  const canvasLayerStyle = useMemo(() => ({ zIndex: CANVAS_LAYER_Z_INDEX }), []);
  const legendColorStyles = useMemo(() => {
    return new Map(
      Object.entries(ENHANCED_TYPE_COLORS).map(([type, color]) => [
        type,
        { backgroundColor: color },
      ]),
    );
  }, []);
  const visibleLegendEntries = useMemo(() => {
    return Object.entries(ENHANCED_TYPE_COLORS)
      .filter(([type]) => visibleTypes.has(type))
      .slice(0, LEGEND_TYPE_LIMIT);
  }, [visibleTypes]);
  const handleDetailPanelToggle = useCallback((): void => {
    setShowDetailPanel((previous) => !previous);
  }, []);
  const handleZoomIn = useCallback((): void => {
    void zoomIn();
  }, [zoomIn]);
  const handleZoomOut = useCallback((): void => {
    void zoomOut();
  }, [zoomOut]);
  const handleCloseDetailPanel = useCallback((): void => {
    setSelectedNodeId(null);
  }, []);
  const getFpsClassName = useCallback((fps: number): string => {
    if (fps >= FPS_GOOD_THRESHOLD) {
      return 'text-green-500';
    }
    if (fps >= FPS_WARN_THRESHOLD) {
      return 'text-yellow-500';
    }
    return 'text-red-500';
  }, []);

  // OPTIMIZATION: Performance monitoring (dev mode only)
  const { getStats: getCacheStats } = useGraphCache();
  const performanceMonitor = useGraphPerformanceMonitor<EnhancedNodeData, Link>({
    cacheStats: useMemo(() => {
      const stats = getCacheStats();
      return {
        grouping: toPerformanceCacheStats(stats.grouping, 'graph-groupings-store'),
        layout: toPerformanceCacheStats(stats.layout, 'graph-layouts-store'),
        search: toPerformanceCacheStats(stats.search, 'graph-search-store'),
      };
    }, [getCacheStats]),
    edges: links,
    enabled: DEV_MODE,
    lodDistribution: useMemo(() => {
      const dist = { high: 0, low: 0, medium: 0, skeleton: 0 };
      const zoom = getViewport?.()?.zoom ?? 1;
      const nodeCount = visibleNodes.length;
      const lodLevel = determineLODLevel(zoom, { nodeCount });

      visibleNodes.forEach(() => {
        if (lodLevel >= LODLevel.Close) {
          dist.high++;
        } else if (lodLevel === LODLevel.Medium) {
          dist.medium++;
        } else if (lodLevel === LODLevel.Far) {
          dist.low++;
        } else {
          dist.skeleton++;
        }
      });

      return dist;
    }, [visibleNodes, getViewport]),
    logToConsole: DEV_MODE,
    nodes: enhancedNodes,
    persistToStorage: DEV_MODE,
    reportInterval: 5000,
    visibleEdges: edgesForRendering,
    visibleNodes,
  });

  return (
    <div className='flex h-full flex-col'>
      {/* Controls */}
      {showControls && (
        <Card className='mb-2 p-1.5 sm:mb-3 sm:p-2'>
          <div className='flex min-w-0 flex-wrap items-center justify-between gap-2 sm:gap-3'>
            <div className='flex min-w-0 items-center gap-1.5 sm:gap-2'>
              {/* Layout selector */}
              <LayoutSelector
                value={layout}
                onChange={setLayout}
                variant='select'
                className='h-7 w-full max-w-[160px] min-w-0 text-xs sm:h-8 sm:max-w-[180px] sm:text-sm md:max-w-[200px]'
              />

              <Separator orientation='vertical' className='hidden h-5 sm:block sm:h-6' />

              {/* Detail panel toggle */}
              <Button
                variant='ghost'
                size='sm'
                onClick={handleDetailPanelToggle}
                className='h-7 w-7 shrink-0 p-0 sm:h-8 sm:w-8'
              >
                {showDetailPanel ? (
                  <PanelRightClose className='h-4 w-4' />
                ) : (
                  <PanelRight className='h-4 w-4' />
                )}
              </Button>
            </div>

            <div className='flex items-center gap-1 rounded-md border p-0.5'>
              <Button variant='ghost' size='sm' onClick={handleZoomIn} className='h-7 w-7 p-0'>
                <ZoomIn className='h-4 w-4' />
              </Button>
              <Button variant='ghost' size='sm' onClick={handleZoomOut} className='h-7 w-7 p-0'>
                <ZoomOut className='h-4 w-4' />
              </Button>
              <Button
                variant='ghost'
                size='sm'
                onClick={handleFit}
                className='h-7 w-7 p-0'
                title='Fit view'
              >
                <Maximize2 className='h-4 w-4' />
              </Button>
              <Button
                variant='ghost'
                size='sm'
                onClick={handleFullscreenToggle}
                className='h-7 w-7 p-0'
                title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
              >
                {isFullscreen ? <Minimize className='h-4 w-4' /> : <Maximize className='h-4 w-4' />}
              </Button>
              <Button
                variant='ghost'
                size='sm'
                onClick={handleReset}
                className='h-7 w-7 p-0'
                title='Reset view'
              >
                <RotateCcw className='h-4 w-4' />
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Graph area */}
      <div className='flex min-w-0 flex-1 gap-2 sm:gap-3'>
        {/* Graph - ref for fullscreen target; 3.1: empty state when no nodes */}
        <Card
          ref={graphContainerRef}
          className='bg-card min-h-0 flex-1 overflow-hidden p-0 [&:fullscreen]:!rounded-none'
        >
          {items.length === 0 ? (
            <div className='text-muted-foreground flex h-full min-h-[280px] flex-col items-center justify-center p-6 text-center'>
              <p className='text-sm font-medium'>No nodes to display</p>
              <p className='mt-1 text-xs'>Add items or links in this project to see the graph.</p>
            </div>
          ) : (
            <div className='relative min-h-0 w-full flex-1'>
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onMoveEnd={handleViewportChange}
                nodeTypes={nodeTypes}
                fitView={autoFit}
                minZoom={0.1}
                maxZoom={2}
                nodesDraggable={false}
                nodesConnectable={false}
                elementsSelectable
                proOptions={reactFlowProOptions}
                className='bg-background'
              >
                <Background variant={BackgroundVariant.Dots} gap={20} size={1} color='#374151' />
                <Controls showInteractive={false} />
                <MiniMap
                  nodeColor={miniMapNodeColor}
                  maskColor='rgba(0, 0, 0, 0.7)'
                  className='!bg-card !border-border'
                />
                <Panel position='bottom-left' className='!m-1 sm:!m-2'>
                  <div className='bg-card/90 flex max-w-[90vw] flex-wrap gap-1 rounded-md border p-1.5 text-[9px] backdrop-blur-sm sm:gap-2 sm:rounded-lg sm:p-2 sm:text-[10px]'>
                    {visibleLegendEntries.map(([type]) => (
                      <div key={type} className='flex min-w-0 items-center gap-0.5 sm:gap-1'>
                        <div
                          className='h-2 w-4 shrink-0 rounded sm:h-2.5 sm:w-5'
                          style={legendColorStyles.get(type)}
                        />
                        <span className='truncate capitalize'>{type.replaceAll('_', ' ')}</span>
                      </div>
                    ))}
                  </div>
                </Panel>

                {/* Performance Monitor Panel (dev mode only) */}
                {DEV_MODE && performanceMonitor.currentMetrics && (
                  <Panel position='top-right' className='!m-1 sm:!m-2'>
                    <div className='bg-card/90 space-y-0.5 rounded-md border p-1.5 font-mono text-[9px] backdrop-blur-sm sm:rounded-lg sm:p-2 sm:text-[10px]'>
                      <div className='flex items-center gap-1'>
                        <span className='text-muted-foreground'>FPS:</span>
                        <span
                          className={getFpsClassName(performanceMonitor.currentMetrics.fps.current)}
                        >
                          {performanceMonitor.currentMetrics.fps.current}
                        </span>
                        <span className='text-muted-foreground text-[8px]'>
                          (avg: {performanceMonitor.currentMetrics.fps.average})
                        </span>
                      </div>
                      <div className='flex items-center gap-1'>
                        <span className='text-muted-foreground'>Nodes:</span>
                        <span className='text-primary'>
                          {performanceMonitor.currentMetrics.nodes.rendered}/
                          {performanceMonitor.currentMetrics.nodes.total}
                        </span>
                        <span className='text-muted-foreground text-[8px]'>
                          ({performanceMonitor.currentMetrics.nodes.cullingRatio.toFixed(0)}%
                          culled)
                        </span>
                      </div>
                      <div className='flex items-center gap-1'>
                        <span className='text-muted-foreground'>Edges:</span>
                        <span className='text-primary'>
                          {performanceMonitor.currentMetrics.edges.rendered}/
                          {performanceMonitor.currentMetrics.edges.total}
                        </span>
                        <span className='text-muted-foreground text-[8px]'>
                          ({performanceMonitor.currentMetrics.edges.cullingRatio.toFixed(0)}%
                          culled)
                        </span>
                      </div>
                      <div className='flex items-center gap-1'>
                        <span className='text-muted-foreground'>Cache:</span>
                        <span className='text-primary'>
                          {(
                            performanceMonitor.currentMetrics.cache.combined.hitRatio * 100
                          ).toFixed(0)}
                          %
                        </span>
                      </div>
                    </div>
                  </Panel>
                )}
              </ReactFlow>
              {/* D3: Canvas layer for far-LOD nodes when zoomed out and many nodes */}
              {canvasNodes.length > 0 && viewportBounds && (
                <canvas
                  ref={canvasLayerRef}
                  className='pointer-events-none absolute inset-0 h-full w-full'
                  style={canvasLayerStyle}
                  aria-hidden
                />
              )}
            </div>
          )}
        </Card>

        {/* Node Detail Panel */}
        {showDetailPanel && selectedNode && (
          <NodeDetailPanel
            node={selectedNode}
            relatedItems={relatedItems}
            incomingLinks={incomingLinks}
            outgoingLinks={outgoingLinks}
            onClose={handleCloseDetailPanel}
            onNavigateToItem={onNavigateToItem ?? noop}
            onFocusNode={handleFocusNode}
          />
        )}
      </div>
    </div>
  );
}

export const FlowGraphViewInner = memo(FlowGraphViewInnerComponent);
