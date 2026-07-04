// PivotNavigation.tsx - Navigate between equivalent nodes across perspectives
// When viewing an item, shows clickable badges for its projections in other perspectives

import {
  ArrowRight,
  Briefcase,
  Code,
  ExternalLink,
  Gauge,
  Layout,
  Network,
  Shield,
  Users,
} from 'lucide-react';
import { memo, useMemo } from 'react';

import type { CanonicalProjection, EquivalenceLink, Item } from '@tracertm/types';

import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Popover, PopoverContent, PopoverTrigger } from '@tracertm/ui/components/Popover';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

import type { GraphPerspective } from './types';

import { PERSPECTIVE_CONFIGS } from './types';

// =============================================================================
// TYPES
// =============================================================================

export interface PivotNavigationProps {
  /** The currently selected/focused item */
  currentItem: Item;
  /** The current perspective being viewed */
  currentPerspective: GraphPerspective;
  /** Equivalent items in other perspectives */
  equivalentItems: PivotTarget[];
  /** Callback when user pivots to another perspective */
  onPivot: (perspectiveId: GraphPerspective, itemId: string) => void;
  /** Compact mode for inline display */
  compact?: boolean;
  /** Show all perspectives even if no equivalents */
  showEmpty?: boolean;
}

export interface PivotTarget {
  item: Item;
  perspectiveId: GraphPerspective;
  confidence: number;
  source: 'equivalence' | 'canonical' | 'manual';
}

// =============================================================================
// CONSTANTS
// =============================================================================

const PERSPECTIVE_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  all: Network,
  business: Briefcase,
  performance: Gauge,
  product: Users,
  security: Shield,
  technical: Code,
  ui: Layout,
};

// =============================================================================
// COMPONENT
// =============================================================================

function PivotNavigationComponent({
  currentPerspective,
  equivalentItems,
  onPivot,
  compact = false,
  showEmpty = false,
}: Omit<PivotNavigationProps, 'currentItem'>) {
  // Group equivalent items by perspective
  const itemsByPerspective = useMemo(() => {
    const grouped = new Map<GraphPerspective, PivotTarget[]>();

    for (const target of equivalentItems) {
      if (target.perspectiveId === currentPerspective) {
        continue;
      }
      if (target.perspectiveId === 'all') {
        continue;
      }

      const existing = grouped.get(target.perspectiveId) ?? [];
      existing.push(target);
      grouped.set(target.perspectiveId, existing);
    }

    return grouped;
  }, [equivalentItems, currentPerspective]);

  // Get perspectives that have equivalents
  const perspectivesWithItems = useMemo(
    () =>
      PERSPECTIVE_CONFIGS.filter((config) => {
        if (config.id === 'all') {
          return false;
        }
        if (config.id === currentPerspective) {
          return false;
        }
        return showEmpty || itemsByPerspective.has(config.id);
      }),
    [itemsByPerspective, currentPerspective, showEmpty],
  );

  if (perspectivesWithItems.length === 0 && !showEmpty) {
    return null;
  }

  if (compact) {
    return (
      <CompactPivotNavigation
        currentPerspective={currentPerspective}
        itemsByPerspective={itemsByPerspective}
        perspectivesWithItems={perspectivesWithItems}
        onPivot={onPivot}
      />
    );
  }

  return (
    <TooltipProvider>
      <div className='flex flex-col gap-2'>
        <div className='text-muted-foreground flex items-center gap-2 text-xs'>
          <ArrowRight className='h-3.5 w-3.5' />
          <span>Pivot to perspective</span>
        </div>

        <div className='flex flex-wrap gap-1.5'>
          {perspectivesWithItems.map((config) => {
            const items = itemsByPerspective.get(config.id) ?? [];
            const Icon = PERSPECTIVE_ICONS[config.id] ?? Network;
            const hasItems = items.length > 0;

            if (items.length === 1 && items[0]) {
              // Single item - direct navigation
              const target = items[0];
              return (
                <Tooltip key={config.id} delayDuration={200}>
                  <TooltipTrigger asChild>
                    <Button
                      variant='outline'
                      size='sm'
                      className='h-7 gap-1.5 px-2'
                      style={{
                        borderColor: hasItems ? config.color : undefined,
                        color: hasItems ? config.color : undefined,
                      }}
                      disabled={!hasItems}
                      onClick={() => {
                        onPivot(config.id, target.item.id);
                      }}
                    >
                      <Icon className='h-3.5 w-3.5' />
                      <span className='text-xs'>{config.label.replace(' View', '')}</span>
                      <ConfidenceIndicator confidence={target.confidence} />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side='bottom' className='max-w-xs'>
                    <div className='space-y-1'>
                      <p className='font-medium'>{target.item.title}</p>
                      <p className='text-muted-foreground text-xs'>
                        {target.item.type} &bull; {Math.round(target.confidence * 100)}% confidence
                      </p>
                      <p className='text-muted-foreground text-xs'>
                        Click to view in {config.label}
                      </p>
                    </div>
                  </TooltipContent>
                </Tooltip>
              );
            }

            if (items.length > 1) {
              // Multiple items - show popover
              return (
                <Popover key={config.id}>
                  <PopoverTrigger asChild>
                    <Button
                      variant='outline'
                      size='sm'
                      className='h-7 gap-1.5 px-2'
                      style={{
                        borderColor: config.color,
                        color: config.color,
                      }}
                    >
                      <Icon className='h-3.5 w-3.5' />
                      <span className='text-xs'>{config.label.replace(' View', '')}</span>
                      <Badge
                        variant='secondary'
                        className='h-4 px-1 text-[10px]'
                        style={{ backgroundColor: `${config.color}20` }}
                      >
                        {items.length}
                      </Badge>
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className='w-72 p-2' align='start'>
                    <div className='space-y-1'>
                      <p className='text-muted-foreground px-2 py-1 text-xs font-medium'>
                        Select equivalent in {config.label}
                      </p>
                      {items.map((target) => (
                        <Button
                          key={target.item.id}
                          variant='ghost'
                          size='sm'
                          className='h-auto w-full justify-start gap-2 py-2'
                          onClick={() => {
                            onPivot(config.id, target.item.id);
                          }}
                        >
                          <div className='min-w-0 flex-1 text-left'>
                            <p className='truncate text-sm font-medium'>{target.item.title}</p>
                            <p className='text-muted-foreground text-xs'>{target.item.type}</p>
                          </div>
                          <ConfidenceIndicator confidence={target.confidence} />
                        </Button>
                      ))}
                    </div>
                  </PopoverContent>
                </Popover>
              );
            }

            // No items - disabled button
            if (showEmpty) {
              return (
                <Tooltip key={config.id} delayDuration={200}>
                  <TooltipTrigger asChild>
                    <Button
                      variant='ghost'
                      size='sm'
                      className='h-7 gap-1.5 px-2 opacity-50'
                      disabled
                    >
                      <Icon className='h-3.5 w-3.5' />
                      <span className='text-xs'>{config.label.replace(' View', '')}</span>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side='bottom'>No equivalents in {config.label}</TooltipContent>
                </Tooltip>
              );
            }

            return null;
          })}
        </div>
      </div>
    </TooltipProvider>
  );
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

interface CompactPivotNavigationProps {
  currentPerspective: GraphPerspective;
  itemsByPerspective: Map<GraphPerspective, PivotTarget[]>;
  perspectivesWithItems: typeof PERSPECTIVE_CONFIGS;
  onPivot: (perspectiveId: GraphPerspective, itemId: string) => void;
}

function CompactPivotNavigation({
  currentPerspective,
  itemsByPerspective,
  perspectivesWithItems,
  onPivot,
}: CompactPivotNavigationProps) {
  const totalEquivalents = [...itemsByPerspective.values()].reduce(
    (sum, items) => sum + items.length,
    0,
  );

  if (totalEquivalents === 0) {
    return null;
  }

  return (
    <TooltipProvider>
      <Popover>
        <PopoverTrigger asChild>
          <Button variant='outline' size='sm' className='h-7 gap-1.5 px-2'>
            <ArrowRight className='h-3.5 w-3.5' />
            <span className='text-xs'>Pivot</span>
            <Badge variant='secondary' className='h-4 px-1 text-[10px]'>
              {totalEquivalents}
            </Badge>
          </Button>
        </PopoverTrigger>
        <PopoverContent className='w-80 p-3' align='end'>
          <div className='space-y-3'>
            <p className='text-sm font-medium'>Pivot to another perspective</p>
            <div className='space-y-2'>
              {perspectivesWithItems.map((config) => {
                const items = itemsByPerspective.get(config.id) ?? [];
                if (items.length === 0) {
                  return null;
                }

                // 								Const _Icon = PERSPECTIVE_ICONS[config.id] || Network;

                return (
                  <div key={config.id} className='space-y-1'>
                    <div className='flex items-center gap-2 px-2'>
                      <div
                        className='h-2 w-2 rounded-full'
                        style={{ backgroundColor: config.color }}
                      />
                      <span className='text-xs font-medium'>{config.label}</span>
                    </div>
                    {items.map((target) => (
                      <Button
                        key={target.item.id}
                        variant='ghost'
                        size='sm'
                        className='h-auto w-full justify-between gap-2 py-2 pl-6'
                        onClick={() => {
                          onPivot(config.id, target.item.id);
                        }}
                      >
                        <div className='min-w-0 flex-1 text-left'>
                          <p className='truncate text-sm'>{target.item.title}</p>
                          <p className='text-muted-foreground text-xs'>{target.item.type}</p>
                        </div>
                        <div className='flex items-center gap-2'>
                          <ConfidenceIndicator confidence={target.confidence} />
                          <ExternalLink className='h-3.5 w-3.5 opacity-50' />
                        </div>
                      </Button>
                    ))}
                  </div>
                );
              })}
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </TooltipProvider>
  );
}

interface ConfidenceIndicatorProps {
  confidence: number;
}

function getConfidenceColor(conf: number): string {
  if (conf >= 0.9) {
    return 'bg-green-500';
  }
  if (conf >= 0.7) {
    return 'bg-amber-500';
  }
  if (conf >= 0.5) {
    return 'bg-orange-500';
  }
  return 'bg-red-500';
}

function ConfidenceIndicator({ confidence }: ConfidenceIndicatorProps) {
  return (
    <Tooltip delayDuration={200}>
      <TooltipTrigger asChild>
        <div className='flex items-center gap-0.5'>
          {[0.25, 0.5, 0.75, 1].map((threshold) => (
            <div
              key={threshold}
              className={`h-2 w-1 rounded-sm ${
                confidence >= threshold ? getConfidenceColor(confidence) : 'bg-muted-foreground/20'
              }`}
            />
          ))}
        </div>
      </TooltipTrigger>
      <TooltipContent side='top' className='text-xs'>
        {Math.round(confidence * 100)}% confidence
      </TooltipContent>
    </Tooltip>
  );
}

// =============================================================================
// UTILITIES
// =============================================================================

/**
 * Build pivot targets from equivalence links and canonical projections
 */
export function buildPivotTargets(
  currentItem: Item,
  equivalenceLinks: EquivalenceLink[],
  projections: CanonicalProjection[],
  items: Item[],
): PivotTarget[] {
  const itemsMap = new Map(items.map((i) => [i.id, i]));
  const results: PivotTarget[] = [];
  const seenIds = new Set<string>();

  // From equivalence links
  for (const link of equivalenceLinks) {
    const targetId = link.sourceItemId === currentItem.id ? link.targetItemId : link.sourceItemId;
    if (seenIds.has(targetId)) {
      continue;
    }
    seenIds.add(targetId);

    const item = itemsMap.get(targetId);
    if (!item) {
      continue;
    }

    results.push({
      confidence: link.confidence,
      item,
      perspectiveId: getPerspectiveForItem(item),
      source: 'equivalence',
    });
  }

  // From canonical projections
  for (const projection of projections) {
    if (projection.itemId === currentItem.id) {
      continue;
    }
    if (seenIds.has(projection.itemId)) {
      continue;
    }
    seenIds.add(projection.itemId);

    const item = itemsMap.get(projection.itemId);
    if (!item) {
      continue;
    }

    results.push({
      confidence: projection.confidence,
      item,
      perspectiveId: projection.perspective || getPerspectiveForItem(item),
      source: 'canonical',
    });
  }

  return results.toSorted((a, b) => b.confidence - a.confidence);
}

function getPerspectiveForItem(item: Item): GraphPerspective {
  if (item.perspective) {
    return item.perspective;
  }

  const itemType = item.type.toLowerCase();

  if (['api', 'database', 'code', 'architecture', 'infrastructure'].includes(itemType)) {
    return 'technical';
  }
  if (['wireframe', 'ui_component', 'page', 'component', 'layout', 'section'].includes(itemType)) {
    return 'ui';
  }
  if (['requirement', 'feature', 'user_story', 'story', 'journey'].includes(itemType)) {
    return 'product';
  }
  if (['epic', 'task', 'bug'].includes(itemType)) {
    return 'business';
  }
  if (['security', 'vulnerability', 'audit'].includes(itemType)) {
    return 'security';
  }
  if (['performance', 'monitoring', 'metric'].includes(itemType)) {
    return 'performance';
  }

  return 'all';
}

// =============================================================================
// EXPORTS
// =============================================================================

export const PivotNavigation = memo(PivotNavigationComponent);
