// Page Interaction Flow - Storybook-like visualization of UI page flows
// Maps page-to-page interactions with cross-linking and visual flow diagrams

import type { Edge, Node, NodeProps, NodeTypes } from '@xyflow/react';

import {
  Background,
  BackgroundVariant,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from '@xyflow/react';
import {
  ArrowRight,
  ChevronRight,
  Eye,
  Layers,
  Monitor,
  MousePointer,
  MousePointerClick,
  Search,
  Smartphone,
  Tablet,
  Workflow,
} from 'lucide-react';
import { memo, useCallback, useEffect, useMemo, useState } from 'react';

import type { Item, Link } from '@tracertm/types';

import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { Input } from '@tracertm/ui/components/Input';

import '@xyflow/react/dist/style.css';
import { ScrollArea } from '@tracertm/ui/components/ScrollArea';
import { Tabs, TabsList, TabsTrigger } from '@tracertm/ui/components/Tabs';

// UI-related item types
const UI_PAGE_TYPES = new Set(['page', 'screen', 'view', 'modal', 'dialog']);
const UI_WIREFRAME_TYPES = new Set(['wireframe', 'mockup', 'prototype']);

// Interaction types (link types that represent user interactions)
const INTERACTION_LINK_TYPES = new Set(['navigates_to', 'opens', 'triggers', 'related_to']);

// Page node data
interface PageNodeData {
  id: string;
  item: Item;
  label: string;
  description?: string | undefined;
  screenshotUrl?: string | undefined;
  thumbnailUrl?: string | undefined;
  deviceType?: 'desktop' | 'tablet' | 'mobile' | undefined;
  interactionCount: number;
  onSelect?: ((id: string) => void) | undefined;
  onPreview?: ((id: string) => void) | undefined;
  // Index signature for React Flow compatibility
  [key: string]: unknown;
}

// Page node component
function PageNodeComponent({ data, selected }: NodeProps<Node<PageNodeData, 'page'>>) {
  const [isHovered, setIsHovered] = useState(false);
  const hasPreview = Boolean(data.screenshotUrl) || Boolean(data.thumbnailUrl);

  const DeviceIcon = {
    desktop: Monitor,
    mobile: Smartphone,
    tablet: Tablet,
  }[data.deviceType ?? 'desktop'];

  return (
    <>
      <Handle
        type='target'
        position={Position.Left}
        className='!border-background !h-2.5 !w-2.5 !border-2 !bg-pink-500'
      />

      <Card
        className={`w-48 cursor-pointer overflow-hidden transition-all duration-200 ${selected ? 'ring-offset-background ring-2 ring-pink-500 ring-offset-2' : ''} ${isHovered ? 'scale-[1.02] shadow-xl' : 'shadow-lg'} `}
        onMouseEnter={() => {
          setIsHovered(true);
        }}
        onMouseLeave={() => {
          setIsHovered(false);
        }}
        onClick={() => data.onSelect?.(data.id)}
      >
        {/* Preview thumbnail */}
        {hasPreview ? (
          <div className='bg-muted relative h-28'>
            <img
              src={data.thumbnailUrl ?? data.screenshotUrl}
              alt={data.label}
              className='h-full w-full object-cover object-top'
              loading='lazy'
            />
            <div className='absolute top-2 left-2'>
              <DeviceIcon className='h-4 w-4 text-white drop-shadow-md' />
            </div>
            {data.interactionCount > 0 && (
              <Badge className='absolute top-2 right-2 bg-pink-500 px-1.5 text-[10px] text-white'>
                <MousePointerClick className='mr-0.5 h-3 w-3' />
                {data.interactionCount}
              </Badge>
            )}
            {isHovered && (
              <Button
                variant='secondary'
                size='sm'
                className='bg-background/90 absolute right-2 bottom-2 h-6 px-2 text-[10px]'
                onClick={(e) => {
                  e.stopPropagation();
                  data.onPreview?.(data.id);
                }}
              >
                <Eye className='mr-1 h-3 w-3' />
                Preview
              </Button>
            )}
          </div>
        ) : (
          <div className='flex h-28 items-center justify-center bg-gradient-to-br from-pink-500/20 to-purple-500/20'>
            <Monitor className='text-muted-foreground/30 h-12 w-12' />
          </div>
        )}

        {/* Content */}
        <div className='p-3'>
          <h4 className='line-clamp-1 text-sm font-medium'>{data.label}</h4>
          {data.description && (
            <p className='text-muted-foreground mt-1 line-clamp-2 text-[11px]'>
              {data.description}
            </p>
          )}
        </div>
      </Card>

      <Handle
        type='source'
        position={Position.Right}
        className='!border-background !h-2.5 !w-2.5 !border-2 !bg-pink-500'
      />
    </>
  );
}

const PageNode = memo(PageNodeComponent);

// Custom node types - using as assertion for React Flow compatibility
const nodeTypes = {
  page: PageNode,
} as const satisfies NodeTypes;

// User journey type
interface UserJourney {
  id: string;
  name: string;
  description?: string;
  steps: string[]; // Page IDs in order
}

interface PageInteractionFlowProps {
  items: Item[];
  links: Link[];
  onSelectItem?: ((itemId: string) => void) | undefined;
  onPreviewItem?: ((itemId: string) => void) | undefined;
}

function PageInteractionFlowInner({
  items,
  links,
  onSelectItem,
  onPreviewItem,
}: PageInteractionFlowProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJourney, setSelectedJourney] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'flow' | 'journeys' | 'matrix'>('flow');
  const { fitView } = useReactFlow();

  // Filter to UI pages only
  const uiPages = useMemo(
    () =>
      items.filter((item) => {
        const type = (item.type || '').toLowerCase();
        return (
          UI_PAGE_TYPES.has(type) ||
          UI_WIREFRAME_TYPES.has(type) ||
          item.view?.toLowerCase().includes('ui')
        );
      }),
    [items],
  );

  // Build interaction links between pages
  const pageLinks = useMemo(() => {
    const pageIds = new Set(uiPages.map((p) => p.id));
    return links.filter(
      (link) =>
        pageIds.has(link.sourceId) &&
        pageIds.has(link.targetId) &&
        INTERACTION_LINK_TYPES.has(link.type),
    );
  }, [uiPages, links]);

  // Count interactions per page
  const interactionCounts = useMemo(() => {
    const counts = new Map<string, number>();
    for (const link of pageLinks) {
      counts.set(link.sourceId, (counts.get(link.sourceId) ?? 0) + 1);
    }
    return counts;
  }, [pageLinks]);

  // Detect user journeys (sequences of connected pages)
  const userJourneys = useMemo((): UserJourney[] => {
    const journeys: UserJourney[] = [];
    const visited = new Set<string>();

    // Build adjacency list
    const adjacency = new Map<string, string[]>();
    for (const link of pageLinks) {
      if (!adjacency.has(link.sourceId)) {
        adjacency.set(link.sourceId, []);
      }
      adjacency.get(link.sourceId)!.push(link.targetId);
    }

    // Find entry points (pages with no incoming links)
    const hasIncoming = new Set(pageLinks.map((l) => l.targetId));
    const entryPoints = uiPages.filter((p) => !hasIncoming.has(p.id));

    // DFS from each entry point
    function dfs(pageId: string, path: string[]): void {
      if (visited.has(pageId) && path.length > 1) {
        // Found a journey
        journeys.push({
          description: path.map((id) => uiPages.find((p) => p.id === id)?.title ?? id).join(' → '),
          id: `journey-${journeys.length + 1}`,
          name: `Journey ${journeys.length + 1}`,
          steps: [...path],
        });
        return;
      }

      visited.add(pageId);
      const neighbors = adjacency.get(pageId) ?? [];

      if (neighbors.length === 0 && path.length > 1) {
        // End of journey
        journeys.push({
          description: path.map((id) => uiPages.find((p) => p.id === id)?.title ?? id).join(' → '),
          id: `journey-${journeys.length + 1}`,
          name: `Journey ${journeys.length + 1}`,
          steps: [...path],
        });
      } else {
        for (const neighbor of neighbors) {
          if (!path.includes(neighbor)) {
            dfs(neighbor, [...path, neighbor]);
          }
        }
      }
    }

    for (const entry of entryPoints.slice(0, 5)) {
      visited.clear();
      dfs(entry.id, [entry.id]);
    }

    return journeys.slice(0, 10);
  }, [uiPages, pageLinks]);

  // Build interaction matrix
  const interactionMatrix = useMemo(() => {
    const matrix: { source: Item; target: Item; interactions: number }[] = [];
    const pairCounts = new Map<string, number>();

    for (const link of pageLinks) {
      const key = `${link.sourceId}:${link.targetId}`;
      pairCounts.set(key, (pairCounts.get(key) ?? 0) + 1);
    }

    for (const [key, count] of pairCounts) {
      const [sourceId, targetId] = key.split(':');
      const source = uiPages.find((p) => p.id === sourceId);
      const target = uiPages.find((p) => p.id === targetId);
      if (source && target) {
        matrix.push({ interactions: count, source, target });
      }
    }

    return matrix.toSorted((a, b) => b.interactions - a.interactions);
  }, [uiPages, pageLinks]);

  const createNodeData = useCallback(
    (page: Item): PageNodeData => {
      const data: PageNodeData = {
        description: page.description ?? undefined,
        deviceType:
          ((page.metadata?.['deviceType'] as 'desktop' | 'tablet' | 'mobile') ?? undefined) ||
          'desktop',
        id: page.id,
        interactionCount: interactionCounts.get(page.id) ?? 0,
        item: page,
        label: page.title || 'Untitled',
        onPreview: onPreviewItem ?? undefined,
        onSelect: onSelectItem ?? undefined,
        screenshotUrl: (page.metadata?.['screenshotUrl'] as string) ?? undefined,
        thumbnailUrl: (page.metadata?.['thumbnailUrl'] as string) ?? undefined,
      };
      return data;
    },
    [interactionCounts, onSelectItem, onPreviewItem],
  );

  // Calculate layout for pages
  const calculateLayout = useCallback(
    (pages: Item[], journey?: UserJourney): Node<PageNodeData>[] => {
      const nodeWidth = 200;
      const nodeHeight = 180;
      const padding = 60;

      if (journey) {
        // Linear layout for journey
        return journey.steps
          .map((pageId, index) => {
            const page = pages.find((p) => p.id === pageId);
            if (!page) {
              return null;
            }
            return {
              data: createNodeData(page),
              id: page.id,
              position: { x: index * (nodeWidth + padding), y: 100 },
              type: 'page',
            };
          })
          .filter(Boolean) as Node<PageNodeData>[];
      }

      // Grid layout for all pages
      const cols = Math.ceil(Math.sqrt(pages.length));
      return pages.map((page, index) => ({
        data: createNodeData(page),
        id: page.id,
        position: {
          x: (index % cols) * (nodeWidth + padding),
          y: Math.floor(index / cols) * (nodeHeight + padding),
        },
        type: 'page',
      }));
    },
    [createNodeData],
  );

  // Filter pages by search
  const filteredPages = useMemo(() => {
    if (!searchQuery) {
      return uiPages;
    }
    const query = searchQuery.toLowerCase();
    return uiPages.filter(
      (p) =>
        (p.title || '').toLowerCase().includes(query) ||
        (p.description ?? '').toLowerCase().includes(query),
    );
  }, [uiPages, searchQuery]);

  // Selected journey pages
  const journeyPages = useMemo(() => {
    if (!selectedJourney) {
      return filteredPages;
    }
    const journey = userJourneys.find((j) => j.id === selectedJourney);
    if (!journey) {
      return filteredPages;
    }
    return filteredPages.filter((p) => journey.steps.includes(p.id));
  }, [filteredPages, selectedJourney, userJourneys]);

  const initialNodes = useMemo(() => {
    const journey = selectedJourney
      ? userJourneys.find((j) => j.id === selectedJourney)
      : undefined;
    return calculateLayout(journeyPages, journey);
  }, [journeyPages, selectedJourney, userJourneys, calculateLayout]);

  const initialEdges = useMemo((): Edge[] => {
    const pageIds = new Set(journeyPages.map((p) => p.id));
    return pageLinks
      .filter((link) => pageIds.has(link.sourceId) && pageIds.has(link.targetId))
      .map((link) => ({
        animated: true,
        id: link.id,
        label: link.type.replaceAll('_', ' '),
        labelBgPadding: [3, 2] as [number, number],
        labelBgStyle: { fill: 'rgba(26, 26, 46, 0.9)' },
        labelStyle: { fill: '#ec4899', fontSize: 9 },
        markerEnd: { color: '#ec4899', type: MarkerType.ArrowClosed },
        source: link.sourceId,
        style: { stroke: '#ec4899', strokeWidth: 2 },
        target: link.targetId,
        type: 'smoothstep',
      }));
  }, [journeyPages, pageLinks]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes as Node[]);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    const journey = selectedJourney
      ? userJourneys.find((j) => j.id === selectedJourney)
      : undefined;
    setNodes(calculateLayout(journeyPages, journey) as Node[]);
    setEdges(initialEdges);
    setTimeout(async () => fitView({ padding: 0.2 }), 100);
  }, [
    journeyPages,
    selectedJourney,
    userJourneys,
    calculateLayout,
    initialEdges,
    setNodes,
    setEdges,
    fitView,
  ]);

  return (
    <Card className='flex h-full flex-col overflow-hidden'>
      {/* Header */}
      <div className='space-y-3 border-b p-4'>
        <div className='flex items-center justify-between'>
          <div className='flex items-center gap-2'>
            <Workflow className='h-5 w-5 text-pink-500' />
            <h3 className='font-semibold'>Page Interactions</h3>
          </div>
          <Badge variant='secondary' className='text-xs'>
            {uiPages.length} pages · {pageLinks.length} interactions
          </Badge>
        </div>

        {/* Search */}
        <div className='relative'>
          <Search className='text-muted-foreground absolute top-2.5 left-2.5 h-4 w-4' />
          <Input
            placeholder='Search pages...'
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
            }}
            className='h-9 pl-8'
          />
        </div>

        {/* Tabs */}
        <Tabs
          value={activeTab}
          onValueChange={(v) => {
            setActiveTab(v as typeof activeTab);
          }}
        >
          <TabsList className='w-full'>
            <TabsTrigger value='flow' className='flex-1 text-xs'>
              <Workflow className='mr-1 h-3.5 w-3.5' />
              Flow
            </TabsTrigger>
            <TabsTrigger value='journeys' className='flex-1 text-xs'>
              <MousePointer className='mr-1 h-3.5 w-3.5' />
              Journeys
            </TabsTrigger>
            <TabsTrigger value='matrix' className='flex-1 text-xs'>
              <Layers className='mr-1 h-3.5 w-3.5' />
              Matrix
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Content */}
      <div className='flex-1 overflow-hidden'>
        {activeTab === 'flow' && (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
            minZoom={0.2}
            maxZoom={1.5}
            proOptions={{ hideAttribution: true }}
            className='bg-background'
          >
            <Background variant={BackgroundVariant.Dots} gap={16} size={1} color='#374151' />
            <Controls showInteractive={false} className='!bottom-2 !left-2' />
            <MiniMap
              nodeColor={() => '#ec4899'}
              maskColor='rgba(0, 0, 0, 0.8)'
              className='!bg-card !border-border !right-2 !bottom-2'
              style={{ height: 70, width: 100 }}
            />
          </ReactFlow>
        )}

        {activeTab === 'journeys' && (
          <ScrollArea className='h-full'>
            <div className='space-y-3 p-4'>
              {userJourneys.length > 0 ? (
                userJourneys.map((journey) => (
                  <Card
                    key={journey.id}
                    className={`cursor-pointer p-3 transition-colors ${
                      selectedJourney === journey.id
                        ? 'border-pink-500 bg-pink-500/10'
                        : 'hover:bg-muted/50'
                    }`}
                    onClick={() => {
                      setSelectedJourney(selectedJourney === journey.id ? null : journey.id);
                      setActiveTab('flow');
                    }}
                  >
                    <div className='mb-2 flex items-center justify-between'>
                      <h4 className='text-sm font-medium'>{journey.name}</h4>
                      <Badge variant='secondary' className='text-[10px]'>
                        {journey.steps.length} steps
                      </Badge>
                    </div>
                    <div className='text-muted-foreground flex flex-wrap items-center gap-1 text-xs'>
                      {journey.steps.slice(0, 4).map((stepId, idx) => {
                        const page = uiPages.find((p) => p.id === stepId);
                        return (
                          <span key={stepId} className='flex items-center'>
                            <span className='bg-muted rounded px-1.5 py-0.5'>
                              {page?.title ?? stepId}
                            </span>
                            {idx < Math.min(journey.steps.length - 1, 3) && (
                              <ChevronRight className='mx-0.5 h-3 w-3' />
                            )}
                          </span>
                        );
                      })}
                      {journey.steps.length > 4 && (
                        <span className='text-muted-foreground'>
                          +{journey.steps.length - 4} more
                        </span>
                      )}
                    </div>
                  </Card>
                ))
              ) : (
                <div className='text-muted-foreground py-8 text-center'>
                  <MousePointer className='mx-auto mb-2 h-12 w-12 opacity-50' />
                  <p className='text-sm'>No user journeys detected</p>
                  <p className='mt-1 text-xs'>Link pages with navigation relationships</p>
                </div>
              )}
            </div>
          </ScrollArea>
        )}

        {activeTab === 'matrix' && (
          <ScrollArea className='h-full'>
            <div className='space-y-2 p-4'>
              {interactionMatrix.length > 0 ? (
                interactionMatrix.map((interaction, idx) => (
                  <div
                    key={idx}
                    className='bg-muted/30 flex items-center gap-2 rounded-lg p-2 text-sm'
                  >
                    <Button
                      variant='ghost'
                      size='sm'
                      className='h-6 px-2 text-xs'
                      onClick={() => onSelectItem?.(interaction.source.id)}
                    >
                      {interaction.source.title}
                    </Button>
                    <ArrowRight className='h-4 w-4 text-pink-500' />
                    <Button
                      variant='ghost'
                      size='sm'
                      className='h-6 px-2 text-xs'
                      onClick={() => onSelectItem?.(interaction.target.id)}
                    >
                      {interaction.target.title}
                    </Button>
                    <Badge variant='outline' className='ml-auto text-[10px]'>
                      {interaction.interactions}x
                    </Badge>
                  </div>
                ))
              ) : (
                <div className='text-muted-foreground py-8 text-center'>
                  <Layers className='mx-auto mb-2 h-12 w-12 opacity-50' />
                  <p className='text-sm'>No page interactions found</p>
                  <p className='mt-1 text-xs'>Link UI pages to see the interaction matrix</p>
                </div>
              )}
            </div>
          </ScrollArea>
        )}
      </div>
    </Card>
  );
}

export function PageInteractionFlow(props: PageInteractionFlowProps) {
  return (
    <ReactFlowProvider>
      <PageInteractionFlowInner {...props} />
    </ReactFlowProvider>
  );
}
