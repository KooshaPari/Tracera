// Unified Graph View - Multi-dimensional traceability visualization
// Supports multiple perspectives, dimension filtering, and equivalence display
// Implements: Single, Split, Layered, Unified, and Pivot display modes

import { ReactFlowProvider } from '@xyflow/react';
import {
  ArrowLeftRight,
  Columns2,
  Component,
  EyeOff,
  Filter,
  Focus,
  Layers,
  Layers2,
  Link2,
  Maximize2,
  Merge,
} from 'lucide-react';
import { memo, useCallback, useMemo, useState } from 'react';

import type {
  CanonicalConcept,
  CanonicalProjection,
  EquivalenceLink,
  Item,
  Link,
  DimensionFilter,
} from '@tracertm/types';

import { cn } from '@tracertm/ui';
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
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

import type { GraphViewMode } from './GraphViewConfig';
import type { LayoutType } from './layouts/useDagLayout';
import type { GraphPerspective } from './types';

import { DimensionFilters, applyDimensionFilters } from './DimensionFilters';
import { FlowGraphViewInner } from './FlowGraphViewInner';
import { GraphViewContainer } from './GraphViewContainer';
import { PageInteractionFlow } from './PageInteractionFlow';
import { PivotNavigation, buildPivotTargets } from './PivotNavigation';
import { PERSPECTIVE_CONFIGS, TYPE_TO_PERSPECTIVE } from './types';
import { UIComponentTree } from './UIComponentTree';

// =============================================================================
// TYPES
// =============================================================================

/**
 * Multi-perspective display modes
 */
export type DisplayMode =
  | 'single' // One perspective, cross-links hidden
  | 'split' // Side-by-side perspectives, equivalences as bridges
  | 'layered' // Perspectives as semi-transparent layers
  | 'unified' // All perspectives merged, dimension-colored
  | 'pivot'; // Focus on one node, show its projections in all perspectives

/**
 * Equivalence visualization modes
 */
export type EquivalenceMode =
  | 'hide' // Don't show equivalence links
  | 'highlight' // Show equivalence links with special styling
  | 'merge'; // Merge equivalent nodes into single composite node

/**
 * Journey/trace overlay
 */
export interface DerivedJourney {
  id: string;
  name: string;
  type: 'user_flow' | 'data_path' | 'call_chain' | 'test_trace';
  nodeIds: string[];
  links: { sourceId: string; targetId: string; type: string }[];
  color?: string | undefined;
}

/**
 * Props for UnifiedGraphView
 */
interface UnifiedGraphViewProps {
  // Core data
  items: Item[];
  links: Link[];
  isLoading?: boolean | undefined;
  projectId?: string | undefined;

  // Navigation
  onNavigateToItem?: ((itemId: string) => void) | undefined;
  defaultView?: GraphViewMode | undefined;

  // ✅ NEW: Progressive edge loading
  canLoadMore?: boolean | undefined;
  visibleEdges?: number | undefined;
  totalEdges?: number | undefined;
  onLoadMore?: (() => void) | undefined;

  // Multi-perspective controls
  activePerspectives?: GraphPerspective[] | undefined;
  displayMode?: DisplayMode | undefined;
  onDisplayModeChange?: ((mode: DisplayMode) => void) | undefined;

  // Dimension filtering
  dimensionFilters?: DimensionFilter[] | undefined;
  onDimensionFiltersChange?: ((filters: DimensionFilter[]) => void) | undefined;

  // Equivalence display
  equivalenceLinks?: EquivalenceLink[] | undefined;
  equivalenceMode?: EquivalenceMode | undefined;
  onEquivalenceModeChange?: ((mode: EquivalenceMode) => void) | undefined;

  // Canonical concepts
  canonicalConcepts?: CanonicalConcept[] | undefined;
  canonicalProjections?: CanonicalProjection[] | undefined;
  showCanonicalLayer?: boolean | undefined;
  onShowCanonicalLayerChange?: ((show: boolean) => void) | undefined;

  // Journey overlay
  activeJourney?: DerivedJourney | undefined;
  availableJourneys?: DerivedJourney[] | undefined;
  onJourneyChange?: ((journey: DerivedJourney | undefined) => void) | undefined;

  // Pivot mode
  focusedItemId?: string | undefined;
  onFocusedItemChange?: ((itemId: string | undefined) => void) | undefined;
}

// =============================================================================
// DISPLAY MODE CONFIGURATION
// =============================================================================

const DISPLAY_MODE_CONFIGS: {
  id: DisplayMode;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  {
    description: 'One perspective at a time',
    icon: Maximize2,
    id: 'single',
    label: 'Single',
  },
  {
    description: 'Side-by-side comparison',
    icon: Columns2,
    id: 'split',
    label: 'Split',
  },
  {
    description: 'Overlapping perspectives',
    icon: Layers2,
    id: 'layered',
    label: 'Layered',
  },
  {
    description: 'All merged with dimensions',
    icon: Merge,
    id: 'unified',
    label: 'Unified',
  },
  {
    description: 'Focus on equivalences',
    icon: Focus,
    id: 'pivot',
    label: 'Pivot',
  },
];

const EQUIVALENCE_MODE_CONFIGS: {
  id: EquivalenceMode;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  { icon: EyeOff, id: 'hide', label: 'Hide' },
  { icon: Link2, id: 'highlight', label: 'Highlight' },
  { icon: Merge, id: 'merge', label: 'Merge' },
];

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Filter items and links by perspective
 */
function filterByPerspective(
  items: Item[],
  links: Link[],
  perspective: GraphPerspective | null,
): { filteredItems: Item[]; filteredLinks: Link[] } {
  if (!perspective || perspective === 'all') {
    return { filteredItems: items, filteredLinks: links };
  }

  const filteredItems = items.filter((item) => {
    const itemType = (item.type || item.view || 'item').toLowerCase();
    const perspectives = TYPE_TO_PERSPECTIVE[itemType] ?? ['all'];
    return perspectives.includes(perspective);
  });

  const itemIds = new Set(filteredItems.map((i) => i.id));
  const filteredLinks = links.filter(
    (link) => itemIds.has(link.sourceId) && itemIds.has(link.targetId),
  );

  return { filteredItems, filteredLinks };
}

/**
 * Filter items by dimension criteria
 */
function filterByDimensions(
  items: Item[],
  links: Link[],
  filters: DimensionFilter[],
): { filteredItems: Item[]; filteredLinks: Link[] } {
  if (!filters || filters.length === 0) {
    return { filteredItems: items, filteredLinks: links };
  }

  const filteredItems = applyDimensionFilters(
    items as unknown as { dimensions?: Record<string, unknown> }[],
    filters,
  ) as unknown as Item[];
  const itemIds = new Set(filteredItems.map((i) => i.id));
  const filteredLinks = links.filter(
    (link) => itemIds.has(link.sourceId) && itemIds.has(link.targetId),
  );

  return { filteredItems, filteredLinks };
}

/**
 * Add equivalence links to the graph
 */
function addEquivalenceLinks(
  links: Link[],
  equivalenceLinks: EquivalenceLink[],
  mode: EquivalenceMode,
): Link[] {
  if (mode === 'hide' || !equivalenceLinks || equivalenceLinks.length === 0) {
    return links;
  }

  const equivalenceLinkObjects: Link[] = equivalenceLinks.map((eq) => ({
    id: `eq-${eq.id}`,
    projectId: eq.projectId,
    sourceId: eq.sourceItemId,
    targetId: eq.targetItemId,
    type: 'same_as' as const,
    version: 1,
    createdAt: eq.createdAt,
    updatedAt: eq.updatedAt,
    // Mark as equivalence link for special styling
    metadata: {
      confidence: eq.confidence,
      isEquivalence: true,
      status: eq.status,
    },
  }));

  return [...links, ...equivalenceLinkObjects];
}

/**
 * Highlight journey nodes and links
 */
function applyJourneyOverlay(
  items: Item[],
  links: Link[],
  journey: DerivedJourney | undefined,
): { items: Item[]; links: Link[]; journeyActive: boolean } {
  if (!journey) {
    return { items, journeyActive: false, links };
  }

  const journeyNodeSet = new Set(journey.nodeIds);
  const journeyLinkSet = new Set(journey.links.map((l) => `${l.sourceId}-${l.targetId}`));

  // Mark items as part of journey
  const markedItems = items.map((item) => ({
    ...item,
    metadata: {
      ...item.metadata,
      _isInJourney: journeyNodeSet.has(item.id),
      _journeyColor: journey.color,
    },
  }));

  // Mark links as part of journey
  const markedLinks = links.map((link) => ({
    ...link,
    metadata: {
      ...link.metadata,
      _isInJourney: journeyLinkSet.has(`${link.sourceId}-${link.targetId}`),
      _journeyColor: journey.color,
    },
  }));

  return { items: markedItems, journeyActive: true, links: markedLinks };
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

/**
 * Display mode selector
 */
interface DisplayModeSelectorProps {
  mode: DisplayMode;
  onChange: (mode: DisplayMode) => void;
}

const DisplayModeSelector = memo(function DisplayModeSelector({
  mode,
  onChange,
}: DisplayModeSelectorProps) {
  return (
    <TooltipProvider>
      <div className='bg-muted flex items-center gap-1 rounded-lg p-1'>
        {DISPLAY_MODE_CONFIGS.map((config) => (
          <Tooltip key={config.id} delayDuration={300}>
            <TooltipTrigger asChild>
              <Button
                variant={mode === config.id ? 'secondary' : 'ghost'}
                size='sm'
                className={cn('h-8 w-8 p-0', mode === config.id && 'bg-background shadow-sm')}
                onClick={() => {
                  onChange(config.id);
                }}
              >
                <config.icon className='h-4 w-4' />
              </Button>
            </TooltipTrigger>
            <TooltipContent side='bottom'>
              <p className='font-medium'>{config.label}</p>
              <p className='text-muted-foreground text-xs'>{config.description}</p>
            </TooltipContent>
          </Tooltip>
        ))}
      </div>
    </TooltipProvider>
  );
});

/**
 * Equivalence mode selector
 */
interface EquivalenceModeSelectorProps {
  mode: EquivalenceMode;
  onChange: (mode: EquivalenceMode) => void;
  equivalenceCount: number;
}

const EquivalenceModeSelector = memo(function EquivalenceModeSelector({
  mode,
  onChange,
  equivalenceCount,
}: EquivalenceModeSelectorProps) {
  if (equivalenceCount === 0) {
    return null;
  }

  return (
    <div className='flex items-center gap-2'>
      <span className='text-muted-foreground text-xs'>Equivalences</span>
      <div className='bg-muted flex items-center gap-0.5 rounded-md p-0.5'>
        {EQUIVALENCE_MODE_CONFIGS.map((config) => (
          <Button
            key={config.id}
            variant={mode === config.id ? 'secondary' : 'ghost'}
            size='sm'
            className='h-6 px-2 text-xs'
            onClick={() => {
              onChange(config.id);
            }}
          >
            <config.icon className='mr-1 h-3 w-3' />
            {config.label}
          </Button>
        ))}
      </div>
      <Badge variant='secondary' className='text-xs'>
        {equivalenceCount}
      </Badge>
    </div>
  );
});

/**
 * Journey selector
 */
interface JourneySelectorProps {
  activeJourney: DerivedJourney | undefined;
  availableJourneys: DerivedJourney[];
  onChange: (journey: DerivedJourney | undefined) => void;
}

const JourneySelector = memo(function JourneySelector({
  activeJourney,
  availableJourneys,
  onChange,
}: JourneySelectorProps) {
  if (availableJourneys.length === 0) {
    return null;
  }

  return (
    <Select
      value={activeJourney?.id ?? 'none'}
      onValueChange={(value) => {
        if (value === 'none') {
          onChange(undefined);
        } else {
          onChange(availableJourneys.find((j) => j.id === value));
        }
      }}
    >
      <SelectTrigger className='h-8 w-[180px]'>
        <SelectValue placeholder='Select journey' />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value='none'>No journey overlay</SelectItem>
        {availableJourneys.map((journey) => (
          <SelectItem key={journey.id} value={journey.id}>
            <div className='flex items-center gap-2'>
              {journey.color && (
                <div className='h-2 w-2 rounded-full' style={{ backgroundColor: journey.color }} />
              )}
              <span>{journey.name}</span>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
});

/**
 * Split view for side-by-side perspective comparison
 */
interface SplitViewProps {
  items: Item[];
  links: Link[];
  perspectives: [GraphPerspective, GraphPerspective];
  equivalenceLinks?: EquivalenceLink[] | undefined;
  onNavigateToItem?: ((itemId: string) => void) | undefined;
}

function SplitView({
  items,
  links,
  perspectives,
  equivalenceLinks = [],
  onNavigateToItem,
}: SplitViewProps) {
  const [leftPerspective, rightPerspective] = perspectives;

  const leftData = useMemo(
    () => filterByPerspective(items, links, leftPerspective),
    [items, links, leftPerspective],
  );

  const rightData = useMemo(
    () => filterByPerspective(items, links, rightPerspective),
    [items, links, rightPerspective],
  );

  const leftConfig = PERSPECTIVE_CONFIGS.find((c) => c.id === leftPerspective);
  const rightConfig = PERSPECTIVE_CONFIGS.find((c) => c.id === rightPerspective);

  return (
    <div className='flex h-full gap-2 p-2'>
      {/* Left perspective */}
      <div className='flex-1 overflow-hidden rounded-lg border'>
        <div
          className='flex items-center gap-2 border-b px-3 py-2 text-sm font-medium'
          style={{
            backgroundColor: `${leftConfig?.color}10`,
            borderColor: leftConfig?.color,
          }}
        >
          <div className='h-2 w-2 rounded-full' style={{ backgroundColor: leftConfig?.color }} />
          {leftConfig?.label}
          <Badge variant='secondary' className='ml-auto text-xs'>
            {leftData.filteredItems.length}
          </Badge>
        </div>
        <div className='h-[calc(100%-44px)]'>
          <ReactFlowProvider>
            <FlowGraphViewInner
              items={leftData.filteredItems}
              links={leftData.filteredLinks}
              perspective={leftPerspective}
              onNavigateToItem={onNavigateToItem}
            />
          </ReactFlowProvider>
        </div>
      </div>

      {/* Bridge links indicator */}
      <div className='flex w-10 flex-col items-center justify-center'>
        <div className='flex flex-col items-center gap-2'>
          <ArrowLeftRight className='text-muted-foreground h-5 w-5' />
          {equivalenceLinks.length > 0 && (
            <Badge variant='outline' className='text-[10px]'>
              {equivalenceLinks.length}
            </Badge>
          )}
        </div>
      </div>

      {/* Right perspective */}
      <div className='flex-1 overflow-hidden rounded-lg border'>
        <div
          className='flex items-center gap-2 border-b px-3 py-2 text-sm font-medium'
          style={{
            backgroundColor: `${rightConfig?.color}10`,
            borderColor: rightConfig?.color,
          }}
        >
          <div className='h-2 w-2 rounded-full' style={{ backgroundColor: rightConfig?.color }} />
          {rightConfig?.label}
          <Badge variant='secondary' className='ml-auto text-xs'>
            {rightData.filteredItems.length}
          </Badge>
        </div>
        <div className='h-[calc(100%-44px)]'>
          <ReactFlowProvider>
            <FlowGraphViewInner
              items={rightData.filteredItems}
              links={rightData.filteredLinks}
              perspective={rightPerspective}
              onNavigateToItem={onNavigateToItem}
            />
          </ReactFlowProvider>
        </div>
      </div>
    </div>
  );
}

/**
 * Pivot view showing focused item and its equivalences
 */
interface PivotViewProps {
  items: Item[];
  links: Link[];
  focusedItemId: string | undefined;
  equivalenceLinks: EquivalenceLink[];
  canonicalProjections: CanonicalProjection[];
  onNavigateToItem?: ((itemId: string) => void) | undefined;
  onPivot: (perspectiveId: GraphPerspective, itemId: string) => void;
}

function PivotView({
  items,
  links,
  focusedItemId,
  equivalenceLinks,
  canonicalProjections,
  onNavigateToItem,
  onPivot,
}: PivotViewProps) {
  const focusedItem = useMemo(
    () => items.find((i) => i.id === focusedItemId),
    [items, focusedItemId],
  );

  const pivotTargets = useMemo(() => {
    if (!focusedItem) {
      return [];
    }

    const itemEquivalences = equivalenceLinks.filter(
      (eq) => eq.sourceItemId === focusedItem.id || eq.targetItemId === focusedItem.id,
    );

    return buildPivotTargets(focusedItem, itemEquivalences, canonicalProjections, items);
  }, [focusedItem, equivalenceLinks, canonicalProjections, items]);

  const currentPerspective = useMemo(() => {
    if (!focusedItem) {
      return 'all' as GraphPerspective;
    }
    const itemType = (focusedItem.type || focusedItem.view || 'item').toLowerCase();
    const perspectives = TYPE_TO_PERSPECTIVE[itemType] ?? ['all'];
    return perspectives[0]!;
  }, [focusedItem]);

  if (!focusedItem) {
    return (
      <div className='flex h-full items-center justify-center'>
        <div className='p-8 text-center'>
          <Focus className='text-muted-foreground mx-auto mb-4 h-12 w-12' />
          <h3 className='mb-2 text-lg font-medium'>Pivot Mode</h3>
          <p className='text-muted-foreground max-w-md text-sm'>
            Select an item in the graph to see its equivalences across all perspectives. This view
            helps you understand how concepts manifest in different views.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className='flex h-full'>
      {/* Main graph view */}
      <div className='flex-1 p-4'>
        <ReactFlowProvider>
          <FlowGraphViewInner
            items={items}
            links={links}
            perspective='all'
            onNavigateToItem={onNavigateToItem}
          />
        </ReactFlowProvider>
      </div>

      {/* Pivot sidebar */}
      <div className='bg-muted/30 w-80 overflow-y-auto border-l'>
        <div className='border-b p-4'>
          <h3 className='mb-1 font-semibold'>{focusedItem.title}</h3>
          <p className='text-muted-foreground text-sm'>
            {focusedItem.type} in {currentPerspective} view
          </p>
        </div>

        <div className='p-4'>
          <PivotNavigation
            currentPerspective={currentPerspective}
            equivalentItems={pivotTargets}
            onPivot={onPivot}
            showEmpty
          />
        </div>

        {pivotTargets.length > 0 && (
          <div className='border-t p-4'>
            <h4 className='mb-3 text-sm font-medium'>Equivalent Items</h4>
            <div className='space-y-2'>
              {pivotTargets.slice(0, 5).map((target) => {
                const config = PERSPECTIVE_CONFIGS.find((c) => c.id === target.perspectiveId);
                return (
                  <button
                    key={target.item.id}
                    type='button'
                    className='bg-background hover:bg-muted w-full rounded-lg border p-2 text-left transition-colors'
                    onClick={() => {
                      onPivot(target.perspectiveId, target.item.id);
                    }}
                  >
                    <div className='mb-1 flex items-center gap-2'>
                      <div
                        className='h-2 w-2 rounded-full'
                        style={{ backgroundColor: config?.color }}
                      />
                      <span className='text-muted-foreground text-xs'>{config?.label}</span>
                      <Badge variant='secondary' className='ml-auto text-[10px]'>
                        {Math.round(target.confidence * 100)}%
                      </Badge>
                    </div>
                    <p className='truncate text-sm font-medium'>{target.item.title}</p>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Component library view
 */
function ComponentLibraryView({
  items,
  links,
  onNavigateToItem,
}: {
  items: Item[];
  links: Link[];
  onNavigateToItem?: ((itemId: string) => void) | undefined;
}) {
  return (
    <div className='h-full p-4'>
      <Card className='h-full overflow-hidden'>
        <div className='flex items-center gap-2 border-b p-4'>
          <Component className='text-primary h-5 w-5' />
          <h2 className='font-semibold'>UI Component Library</h2>
        </div>
        <div className='h-[calc(100%-60px)]'>
          <UIComponentTree
            items={items}
            links={links}
            onSelectItem={onNavigateToItem ?? (() => {})}
            selectedItemId={null}
          />
        </div>
      </Card>
    </div>
  );
}

// =============================================================================
// MAIN VIEW RENDERER
// =============================================================================

interface ViewRendererProps {
  viewMode: GraphViewMode;
  perspective: GraphPerspective | null;
  layoutPreference?: LayoutType | undefined;
  items: Item[];
  links: Link[];
  displayMode: DisplayMode;
  equivalenceMode: EquivalenceMode;
  equivalenceLinks: EquivalenceLink[];
  activeJourney?: DerivedJourney | undefined;
  focusedItemId?: string | undefined;
  canonicalProjections: CanonicalProjection[];
  onNavigateToItem?: ((itemId: string) => void) | undefined;
  onPivot: (perspectiveId: GraphPerspective, itemId: string) => void;
  splitPerspectives?: [GraphPerspective, GraphPerspective] | undefined;
}

function ViewRenderer({
  viewMode,
  perspective,
  layoutPreference,
  items,
  links,
  displayMode,
  equivalenceMode,
  equivalenceLinks,
  activeJourney,
  focusedItemId,
  canonicalProjections,
  onNavigateToItem,
  onPivot,
  splitPerspectives = ['product', 'technical'],
}: ViewRendererProps) {
  // Apply perspective filtering
  const { filteredItems, filteredLinks } = useMemo(
    () => filterByPerspective(items, links, perspective),
    [items, links, perspective],
  );

  // Add equivalence links if in highlight mode
  const linksWithEquivalences = useMemo(
    () => addEquivalenceLinks(filteredLinks, equivalenceLinks, equivalenceMode),
    [filteredLinks, equivalenceLinks, equivalenceMode],
  );

  // Apply journey overlay
  const { items: journeyItems, links: journeyLinks } = useMemo(
    () => applyJourneyOverlay(filteredItems, linksWithEquivalences, activeJourney),
    [filteredItems, linksWithEquivalences, activeJourney],
  );

  // Handle special display modes
  if (displayMode === 'split' && viewMode !== 'page-flow' && viewMode !== 'components') {
    return (
      <SplitView
        items={items}
        links={links}
        perspectives={splitPerspectives}
        equivalenceLinks={equivalenceLinks}
        onNavigateToItem={onNavigateToItem}
      />
    );
  }

  if (displayMode === 'pivot' && viewMode !== 'page-flow' && viewMode !== 'components') {
    return (
      <PivotView
        items={items}
        links={links}
        focusedItemId={focusedItemId}
        equivalenceLinks={equivalenceLinks}
        canonicalProjections={canonicalProjections}
        onNavigateToItem={onNavigateToItem}
        onPivot={onPivot}
      />
    );
  }

  // Render based on view mode
  switch (viewMode) {
    case 'page-flow': {
      return (
        <div className='h-full p-4'>
          <PageInteractionFlow
            items={items}
            links={links}
            onSelectItem={onNavigateToItem}
            onPreviewItem={onNavigateToItem}
          />
        </div>
      );
    }

    case 'components': {
      return (
        <ComponentLibraryView items={items} links={links} onNavigateToItem={onNavigateToItem} />
      );
    }
    default: {
      return (
        <div className='h-full p-4'>
          <ReactFlowProvider>
            <FlowGraphViewInner
              items={journeyItems}
              links={journeyLinks}
              perspective={perspective ?? 'all'}
              defaultLayout={layoutPreference}
              onNavigateToItem={onNavigateToItem}
            />
          </ReactFlowProvider>
        </div>
      );
    }
  }
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export function UnifiedGraphView({
  items,
  links,
  isLoading = false,
  projectId,
  onNavigateToItem,
  defaultView = 'traceability',

  // ✅ NEW: Progressive edge loading
  canLoadMore,
  visibleEdges,
  totalEdges,
  onLoadMore,

  // Multi-perspective controls
  displayMode: externalDisplayMode,
  onDisplayModeChange,

  // Dimension filtering
  dimensionFilters: externalFilters = [],
  onDimensionFiltersChange,

  // Equivalence display
  equivalenceLinks = [],
  equivalenceMode: externalEquivalenceMode,
  onEquivalenceModeChange,

  // Canonical concepts
  canonicalConcepts = [],
  canonicalProjections = [],
  showCanonicalLayer = false,
  onShowCanonicalLayerChange,

  // Journey overlay
  activeJourney,
  availableJourneys = [],
  onJourneyChange,

  // Pivot mode
  focusedItemId,
  onFocusedItemChange,
}: UnifiedGraphViewProps) {
  // Internal state (used if not controlled externally)
  const [internalDisplayMode, setInternalDisplayMode] = useState<DisplayMode>('single');
  const [internalEquivalenceMode, setInternalEquivalenceMode] = useState<EquivalenceMode>('hide');
  const [internalFilters, setInternalFilters] = useState<DimensionFilter[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [splitPerspectives, setSplitPerspectives] = useState<[GraphPerspective, GraphPerspective]>([
    'product',
    'technical',
  ]);

  // Use external or internal state
  const displayMode = externalDisplayMode ?? internalDisplayMode;
  const equivalenceMode = externalEquivalenceMode ?? internalEquivalenceMode;
  const dimensionFilters = externalFilters.length > 0 ? externalFilters : internalFilters;

  // Handlers
  const handleDisplayModeChange = useCallback(
    (mode: DisplayMode) => {
      if (onDisplayModeChange) {
        onDisplayModeChange(mode);
      } else {
        setInternalDisplayMode(mode);
      }
    },
    [onDisplayModeChange],
  );

  const handleEquivalenceModeChange = useCallback(
    (mode: EquivalenceMode) => {
      if (onEquivalenceModeChange) {
        onEquivalenceModeChange(mode);
      } else {
        setInternalEquivalenceMode(mode);
      }
    },
    [onEquivalenceModeChange],
  );

  const handleFiltersChange = useCallback(
    (filters: DimensionFilter[]) => {
      if (onDimensionFiltersChange) {
        onDimensionFiltersChange(filters);
      } else {
        setInternalFilters(filters);
      }
    },
    [onDimensionFiltersChange],
  );

  const handlePivot = useCallback(
    (_perspectiveId: GraphPerspective, itemId: string) => {
      if (onFocusedItemChange) {
        onFocusedItemChange(itemId);
      }
      if (onNavigateToItem) {
        onNavigateToItem(itemId);
      }
    },
    [onFocusedItemChange, onNavigateToItem],
  );

  // Apply dimension filters
  const { filteredItems, filteredLinks } = useMemo(
    () => filterByDimensions(items, links, dimensionFilters),
    [items, links, dimensionFilters],
  );

  return (
    <div className='flex h-[calc(100vh-120px)] flex-col'>
      {/* Enhanced toolbar */}
      <div className='bg-background flex items-center gap-4 border-b px-4 py-2'>
        {/* Display mode selector */}
        <DisplayModeSelector mode={displayMode} onChange={handleDisplayModeChange} />

        {/* Split perspective selectors (when in split mode) */}
        {displayMode === 'split' && (
          <div className='flex items-center gap-2'>
            <Select
              value={splitPerspectives[0]}
              onValueChange={(v) => {
                setSplitPerspectives([v, splitPerspectives[1]]);
              }}
            >
              <SelectTrigger className='h-8 w-[140px]'>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PERSPECTIVE_CONFIGS.filter((c) => c.id !== 'all').map((config) => (
                  <SelectItem key={config.id} value={config.id}>
                    {config.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <span className='text-muted-foreground'>vs</span>
            <Select
              value={splitPerspectives[1]}
              onValueChange={(v) => {
                setSplitPerspectives([splitPerspectives[0], v]);
              }}
            >
              <SelectTrigger className='h-8 w-[140px]'>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PERSPECTIVE_CONFIGS.filter((c) => c.id !== 'all').map((config) => (
                  <SelectItem key={config.id} value={config.id}>
                    {config.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        <div className='flex-1' />

        {/* Equivalence mode selector */}
        <EquivalenceModeSelector
          mode={equivalenceMode}
          onChange={handleEquivalenceModeChange}
          equivalenceCount={equivalenceLinks.length}
        />

        {/* Journey selector */}
        <JourneySelector
          activeJourney={activeJourney}
          availableJourneys={availableJourneys}
          onChange={onJourneyChange ?? (() => {})}
        />

        {/* Dimension filters toggle */}
        <Button
          variant={showFilters ? 'secondary' : 'ghost'}
          size='sm'
          className='h-8'
          onClick={() => {
            setShowFilters(!showFilters);
          }}
        >
          <Filter className='mr-2 h-4 w-4' />
          Filters
          {dimensionFilters.length > 0 && (
            <Badge variant='secondary' className='ml-2 text-xs'>
              {dimensionFilters.length}
            </Badge>
          )}
        </Button>

        {/* Canonical layer toggle */}
        {canonicalConcepts.length > 0 && (
          <Button
            variant={showCanonicalLayer ? 'secondary' : 'ghost'}
            size='sm'
            className='h-8'
            onClick={() => onShowCanonicalLayerChange?.(!showCanonicalLayer)}
          >
            <Layers className='mr-2 h-4 w-4' />
            Canonical
          </Button>
        )}
      </div>

      {/* Dimension filters panel */}
      {showFilters && (
        <div className='border-b'>
          <DimensionFilters
            activeFilters={dimensionFilters}
            onFiltersChange={handleFiltersChange}
            displayMode='filter'
            onDisplayModeChange={() => {}}
            compact
          />
        </div>
      )}

      {/* Main content */}
      <div className='flex-1 overflow-hidden'>
        <GraphViewContainer
          items={filteredItems}
          links={filteredLinks}
          isLoading={isLoading}
          projectId={projectId}
          onNavigateToItem={onNavigateToItem}
          defaultView={defaultView}
          canLoadMore={canLoadMore}
          visibleEdges={visibleEdges}
          totalEdges={totalEdges}
          onLoadMore={onLoadMore}
        >
          {({
            viewMode,
            perspective,
            layoutPreference,
            items: viewItems,
            links: viewLinks,
            onNavigateToItem,
          }) => (
            <ViewRenderer
              viewMode={viewMode}
              perspective={(perspective as GraphPerspective) ?? null}
              layoutPreference={layoutPreference}
              items={viewItems}
              links={viewLinks}
              displayMode={displayMode}
              equivalenceMode={equivalenceMode}
              equivalenceLinks={equivalenceLinks}
              activeJourney={activeJourney}
              focusedItemId={focusedItemId}
              canonicalProjections={canonicalProjections}
              onNavigateToItem={onNavigateToItem}
              onPivot={handlePivot}
              splitPerspectives={splitPerspectives}
            />
          )}
        </GraphViewContainer>
      </div>
    </div>
  );
}
