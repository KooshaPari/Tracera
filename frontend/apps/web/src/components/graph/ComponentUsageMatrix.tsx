// ComponentUsageMatrix.tsx - Matrix view of component usage across pages/views
// Shows which components are used where, usage counts, variants, and deprecation status

import {
  AlertCircle,
  BarChart3,
  ChevronDown,
  Code2,
  Component,
  ExternalLink,
  Grid3x3,
  Layers,
  Package,
  Search,
  Square,
  TrendingUp,
  Zap,
} from 'lucide-react';
import { memo, useMemo, useState } from 'react';

import type { ComponentCategory, ComponentUsage, LibraryComponent } from '@tracertm/types';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui/components/Card';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@tracertm/ui/components/Collapsible';
import { Input } from '@tracertm/ui/components/Input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';
import { Separator } from '@tracertm/ui/components/Separator';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

// =============================================================================
// TYPES
// =============================================================================

export interface ComponentUsageMatrixProps {
  /** All library components */
  components: LibraryComponent[];
  /** Component usage data */
  usage?: ComponentUsage[] | undefined;
  /** List of page/view names where components are used */
  pages?: string[] | undefined;
  /** Currently selected component category filter */
  selectedCategory?: ComponentCategory | 'all' | undefined;
  /** Callback when category filter changes */
  onCategoryChange?: ((category: ComponentCategory | 'all') => void) | undefined;
  /** Callback when a component is selected */
  onSelectComponent?: ((componentId: string) => void) | undefined;
  /** Callback to view component in code */
  onViewInCode?: ((componentId: string) => void) | undefined;
  /** Loading state */
  isLoading?: boolean | undefined;
  /** Enable filtering */
  enableFiltering?: boolean | undefined;
  /** Highlight unused/deprecated components */
  highlightUnused?: boolean | undefined;
  /** Show variant information */
  showVariants?: boolean | undefined;
  /** Show props information */
  showProps?: boolean | undefined;
  /** Custom page labels mapping */
  pageLabels?: Record<string, string> | undefined;
}

// =============================================================================
// CONSTANTS
// =============================================================================

const CATEGORY_ICONS: Record<ComponentCategory, React.ComponentType<{ className?: string }>> = {
  atom: Square,
  'data-display': BarChart3,
  'data-entry': Component,
  feedback: AlertCircle,
  layout: Layers,
  molecule: Grid3x3,
  navigation: Grid3x3,
  organism: Layers,
  other: Component,
  overlay: Package,
  page: BarChart3,
  template: Package,
  utility: Zap,
};

const CATEGORY_LABELS: Record<ComponentCategory, string> = {
  atom: 'Atoms',
  'data-display': 'Data Display',
  'data-entry': 'Data Entry',
  feedback: 'Feedback',
  layout: 'Layout',
  molecule: 'Molecules',
  navigation: 'Navigation',
  organism: 'Organisms',
  other: 'Other',
  overlay: 'Overlay',
  page: 'Pages',
  template: 'Templates',
  utility: 'Utility',
};

const STATUS_COLORS: Record<string, string> = {
  beta: 'bg-blue-100 text-blue-800 border-blue-200',
  deprecated: 'bg-red-100 text-red-800 border-red-200',
  experimental: 'bg-purple-100 text-purple-800 border-purple-200',
  stable: 'bg-green-100 text-green-800 border-green-200',
};

const STATUS_LABELS: Record<string, string> = {
  beta: 'Beta',
  deprecated: 'Deprecated',
  experimental: 'Experimental',
  stable: 'Stable',
};

// =============================================================================
// HELPERS
// =============================================================================

interface UsageStats {
  totalUsage: number;
  pageUsage: Record<string, number>;
  variantUsage: Record<string, number>;
}

function getUsageStats(component: LibraryComponent, usageData?: ComponentUsage[]): UsageStats {
  const stats: UsageStats = {
    pageUsage: {},
    totalUsage: component.usageCount || 0,
    variantUsage: {},
  };

  if (!usageData) {
    return stats;
  }

  usageData.forEach((usage) => {
    if (usage.componentId === component.id) {
      if (usage.usedInFilePath) {
        stats.pageUsage[usage.usedInFilePath] = (stats.pageUsage[usage.usedInFilePath] ?? 0) + 1;
      }
      if (usage.variantUsed) {
        stats.variantUsage[usage.variantUsed] = (stats.variantUsage[usage.variantUsed] ?? 0) + 1;
      }
    }
  });

  return stats;
}

function getUsagePercentage(used: number, total: number): number {
  if (total === 0) {
    return 0;
  }
  return Math.round((used / total) * 100);
}

// =============================================================================
// MATRIX ROW COMPONENT
// =============================================================================

interface MatrixRowProps {
  component: LibraryComponent;
  stats: UsageStats;
  isSelected?: boolean | undefined;
  onSelect?: (() => void) | undefined;
  onViewInCode?: (() => void) | undefined;
  pageLabels?: Record<string, string> | undefined;
  showVariants?: boolean | undefined;
  showProps?: boolean | undefined;
  highlightUnused?: boolean | undefined;
}

const MatrixRow = memo(function MatrixRow({
  component,
  stats,
  isSelected,
  onSelect,
  onViewInCode,
  pageLabels,
  showVariants,
  showProps,
  highlightUnused,
}: MatrixRowProps) {
  const [expanded, setExpanded] = useState(false);
  const CategoryIcon = CATEGORY_ICONS[component.category];
  const isUnused = stats.totalUsage === 0;
  const isDeprecated = component.status === 'deprecated';

  return (
    <div>
      <div
        className={`flex cursor-pointer items-center gap-3 border-b px-4 py-3 transition-colors hover:bg-slate-50 ${isSelected ? 'bg-blue-50' : ''} ${isUnused && highlightUnused ? 'bg-orange-50' : ''} ${isDeprecated && highlightUnused ? 'bg-red-50' : ''} `}
        onClick={onSelect}
      >
        {/* Expand button */}
        {(showVariants && component.variants?.length) || (showProps && component.props?.length) ? (
          <button
            onClick={(e) => {
              e.stopPropagation();
              setExpanded(!expanded);
            }}
            className='rounded p-0.5 hover:bg-slate-200'
          >
            <ChevronDown
              className={`h-4 w-4 transition-transform ${expanded ? '' : '-rotate-90'}`}
            />
          </button>
        ) : (
          <div className='w-6' />
        )}

        {/* Component name and category */}
        <div className='min-w-0 flex-1'>
          <div className='flex items-center gap-2'>
            <CategoryIcon className='h-4 w-4 flex-shrink-0 text-slate-600' />
            <span className='truncate text-sm font-medium'>{component.displayName}</span>
            {isDeprecated && highlightUnused && (
              <Badge
                variant='outline'
                className='flex-shrink-0 border-red-200 bg-red-50 text-xs text-red-700'
              >
                Deprecated
              </Badge>
            )}
            {isUnused && highlightUnused && (
              <Badge
                variant='outline'
                className='flex-shrink-0 border-orange-200 bg-orange-50 text-xs text-orange-700'
              >
                Unused
              </Badge>
            )}
          </div>
          <p className='truncate text-xs text-slate-500'>{component.name}</p>
        </div>

        {/* Status badge */}
        <div className='flex-shrink-0'>
          <Badge variant='outline' className={`text-xs ${STATUS_COLORS[component.status]}`}>
            {STATUS_LABELS[component.status]}
          </Badge>
        </div>

        {/* Usage count */}
        <div className='min-w-[60px] flex-shrink-0 text-right'>
          <p className='text-sm font-semibold'>{stats.totalUsage}</p>
          <p className='text-xs text-slate-500'>times used</p>
        </div>

        {/* Actions */}
        <div className='flex flex-shrink-0 gap-1'>
          {onViewInCode && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant='ghost'
                  size='sm'
                  onClick={(e) => {
                    e.stopPropagation();
                    onViewInCode();
                  }}
                  className='h-8 w-8 p-0'
                >
                  <Code2 className='h-4 w-4' />
                </Button>
              </TooltipTrigger>
              <TooltipContent>View in code</TooltipContent>
            </Tooltip>
          )}
          {component.storybookUrl && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant='ghost'
                  size='sm'
                  onClick={(e) => {
                    e.stopPropagation();
                    window.open(component.storybookUrl, '_blank');
                  }}
                  className='h-8 w-8 p-0'
                >
                  <ExternalLink className='h-4 w-4' />
                </Button>
              </TooltipTrigger>
              <TooltipContent>View in Storybook</TooltipContent>
            </Tooltip>
          )}
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className='border-b bg-slate-50 px-4 py-3 text-sm'>
          {/* Props section */}
          {showProps && component.props && component.props.length > 0 && (
            <div className='mb-4'>
              <p className='mb-2 text-xs font-semibold text-slate-700 uppercase'>Props</p>
              <div className='flex flex-wrap gap-1'>
                {component.props.map((prop) => (
                  <Badge key={prop.name} variant='secondary' className='text-xs'>
                    {prop.name}
                    {prop.required ? '*' : ''}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Variants section */}
          {showVariants && component.variants && component.variants.length > 0 && (
            <div className='mb-4'>
              <p className='mb-2 text-xs font-semibold text-slate-700 uppercase'>Variants</p>
              <div className='flex flex-wrap gap-1'>
                {component.variants.map((variant) => {
                  const variantCount = stats.variantUsage[variant.name] ?? 0;
                  return (
                    <Badge key={variant.name} variant='outline' className='text-xs'>
                      {variant.name}
                      {variantCount > 0 && ` (${variantCount})`}
                    </Badge>
                  );
                })}
              </div>
            </div>
          )}

          {/* Page usage section */}
          {Object.keys(stats.pageUsage).length > 0 && (
            <div>
              <p className='mb-2 text-xs font-semibold text-slate-700 uppercase'>Used in Pages</p>
              <div className='text-xs text-slate-600'>
                {Object.entries(stats.pageUsage).map(([page, count]) => (
                  <div key={page} className='flex justify-between'>
                    <span>{pageLabels?.[page] ?? page}</span>
                    <span className='text-slate-500'>{count}x</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Description */}
          {component.description && (
            <div className='mt-4'>
              <p className='text-xs text-slate-600 italic'>{component.description}</p>
            </div>
          )}

          {/* Deprecation message */}
          {isDeprecated && component.deprecationMessage && (
            <div className='mt-3 rounded border border-red-200 bg-red-50 p-2 text-xs text-red-700'>
              {component.deprecationMessage}
            </div>
          )}
        </div>
      )}
    </div>
  );
});

// =============================================================================
// CATEGORY SECTION COMPONENT
// =============================================================================

interface CategorySectionProps {
  category: ComponentCategory;
  components: LibraryComponent[];
  stats: Record<string, UsageStats>;
  selectedComponentId?: string | undefined;
  onSelectComponent?: ((componentId: string) => void) | undefined;
  onViewInCode?: ((componentId: string) => void) | undefined;
  pageLabels?: Record<string, string> | undefined;
  showVariants?: boolean | undefined;
  showProps?: boolean | undefined;
  highlightUnused?: boolean | undefined;
}

const CategorySection = memo(function CategorySection({
  category,
  components,
  stats,
  selectedComponentId,
  onSelectComponent,
  onViewInCode,
  pageLabels,
  showVariants,
  showProps,
  highlightUnused,
}: CategorySectionProps) {
  const [expanded, setExpanded] = useState(true);
  const CategoryIcon = CATEGORY_ICONS[category];
  const totalUsage = components.reduce((sum, comp) => sum + (stats[comp.id]?.totalUsage ?? 0), 0);
  const unusedCount = components.filter((comp) => (stats[comp.id]?.totalUsage ?? 0) === 0).length;

  return (
    <Collapsible open={expanded} onOpenChange={setExpanded} className='border-b'>
      <CollapsibleTrigger className='flex w-full items-center gap-3 px-4 py-3 hover:bg-slate-50'>
        <CategoryIcon className='h-4 w-4 text-slate-600' />
        <span className='text-sm font-semibold'>{CATEGORY_LABELS[category]}</span>
        <div className='ml-auto flex gap-3 text-xs text-slate-500'>
          <span>{components.length} components</span>
          <span className='font-medium text-slate-600'>{totalUsage} total uses</span>
          {unusedCount > 0 && <span className='text-orange-600'>{unusedCount} unused</span>}
        </div>
      </CollapsibleTrigger>
      <CollapsibleContent className='bg-white'>
        {components.map((component) => (
          <MatrixRow
            key={component.id}
            component={component}
            stats={
              stats[component.id] ?? {
                pageUsage: {},
                totalUsage: 0,
                variantUsage: {},
              }
            }
            isSelected={selectedComponentId === component.id}
            onSelect={() => onSelectComponent?.(component.id)}
            onViewInCode={() => onViewInCode?.(component.id)}
            pageLabels={pageLabels}
            showVariants={showVariants}
            showProps={showProps}
            highlightUnused={highlightUnused}
          />
        ))}
      </CollapsibleContent>
    </Collapsible>
  );
});

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export const ComponentUsageMatrix = memo(function ComponentUsageMatrix({
  components,
  usage,
  selectedCategory = 'all',
  onCategoryChange,
  onSelectComponent,
  onViewInCode,
  isLoading = false,
  enableFiltering = true,
  highlightUnused = true,
  showVariants = true,
  showProps = true,
  pageLabels,
}: ComponentUsageMatrixProps) {
  const [searchQuery, setSearchQuery] = useState('');

  // Compute usage stats for all components
  const usageStats = useMemo(() => {
    const stats: Record<string, UsageStats> = {};
    components.forEach((comp) => {
      stats[comp.id] = getUsageStats(comp, usage);
    });
    return stats;
  }, [components, usage]);

  // Filter components by category and search query
  const filteredByCategory = useMemo(
    () =>
      selectedCategory === 'all'
        ? components
        : components.filter((comp) => comp.category === selectedCategory),
    [components, selectedCategory],
  );

  const filteredComponents = useMemo(() => {
    if (!searchQuery.trim()) {
      return filteredByCategory;
    }
    const query = searchQuery.toLowerCase();
    return filteredByCategory.filter(
      (comp) =>
        comp.name.toLowerCase().includes(query) ||
        comp.displayName.toLowerCase().includes(query) ||
        comp.description?.toLowerCase().includes(query),
    );
  }, [filteredByCategory, searchQuery]);

  // Group components by category
  const componentsByCategory = useMemo(() => {
    const grouped: Record<ComponentCategory, LibraryComponent[]> = {
      atom: [],
      'data-display': [],
      'data-entry': [],
      feedback: [],
      layout: [],
      molecule: [],
      navigation: [],
      organism: [],
      other: [],
      overlay: [],
      page: [],
      template: [],
      utility: [],
    };

    filteredComponents.forEach((comp) => {
      grouped[comp.category].push(comp);
    });

    return grouped;
  }, [filteredComponents]);

  // Calculate statistics
  const stats = useMemo(() => {
    const total = filteredComponents.length;
    const unused = filteredComponents.filter(
      (c) => (usageStats[c.id]?.totalUsage ?? 0) === 0,
    ).length;
    const deprecated = filteredComponents.filter((c) => c.status === 'deprecated').length;
    const totalUses = filteredComponents.reduce(
      (sum, c) => sum + (usageStats[c.id]?.totalUsage ?? 0),
      0,
    );

    return { deprecated, total, totalUses, unused };
  }, [filteredComponents, usageStats]);

  if (isLoading) {
    return (
      <Card className='w-full'>
        <CardHeader>
          <CardTitle>Component Usage Matrix</CardTitle>
        </CardHeader>
        <CardContent className='flex items-center justify-center py-8'>
          <LoadingSpinner size='sm' text='Loading components...' />
        </CardContent>
      </Card>
    );
  }

  const categories = Object.entries(componentsByCategory)
    .filter(([_, comps]) => comps.length > 0)
    .map(([cat]) => cat as ComponentCategory);

  return (
    <Card className='w-full'>
      <CardHeader>
        <div className='flex items-center justify-between'>
          <div>
            <CardTitle className='flex items-center gap-2'>
              <Grid3x3 className='h-5 w-5' />
              Component Usage Matrix
            </CardTitle>
            <p className='mt-1 text-sm text-slate-500'>
              {stats.total} components • {stats.totalUses} total uses
              {stats.unused > 0 && ` • ${stats.unused} unused`}
              {stats.deprecated > 0 && ` • ${stats.deprecated} deprecated`}
            </p>
          </div>
        </div>

        <Separator className='mt-4' />

        {/* Controls */}
        {enableFiltering && (
          <div className='mt-4 flex flex-col gap-3'>
            <div className='flex gap-3'>
              {/* Search */}
              <div className='relative flex-1'>
                <Search className='absolute top-2.5 left-3 h-4 w-4 text-slate-400' />
                <Input
                  placeholder='Search components...'
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                  }}
                  className='pl-9'
                />
              </div>

              {/* Category filter */}
              <Select
                value={selectedCategory}
                onValueChange={(value) =>
                  onCategoryChange?.(value === 'all' ? 'all' : (value as ComponentCategory))
                }
              >
                <SelectTrigger className='w-[180px]'>
                  <SelectValue placeholder='Select category' />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='all'>All Categories</SelectItem>
                  {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
                    <SelectItem key={key} value={key}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Active filters display */}
            {(searchQuery || selectedCategory !== 'all') && (
              <div className='flex items-center gap-2 text-xs'>
                <span className='text-slate-600'>Filters:</span>
                {selectedCategory !== 'all' && (
                  <Badge variant='secondary'>{CATEGORY_LABELS[selectedCategory]}</Badge>
                )}
                {searchQuery && <Badge variant='secondary'>"{searchQuery}"</Badge>}
              </div>
            )}
          </div>
        )}
      </CardHeader>

      <CardContent className='p-0'>
        {filteredComponents.length === 0 ? (
          <div className='flex items-center justify-center py-8 text-slate-500'>
            <AlertCircle className='mr-2 h-5 w-5' />
            No components found
          </div>
        ) : (
          <TooltipProvider>
            <div className='overflow-hidden rounded-md border'>
              {categories.map((category) => (
                <CategorySection
                  key={category}
                  category={category}
                  components={componentsByCategory[category]}
                  stats={usageStats}
                  selectedComponentId={undefined}
                  onSelectComponent={onSelectComponent}
                  onViewInCode={onViewInCode}
                  pageLabels={pageLabels}
                  showVariants={showVariants}
                  showProps={showProps}
                  highlightUnused={highlightUnused}
                />
              ))}
            </div>
          </TooltipProvider>
        )}
      </CardContent>

      {/* Stats footer */}
      {filteredComponents.length > 0 && (
        <div className='flex items-center justify-between border-t bg-slate-50 px-4 py-3 text-xs text-slate-600'>
          <div>
            Showing {filteredComponents.length} of {components.length} components
          </div>
          <div className='flex gap-4'>
            <div className='flex items-center gap-1'>
              <TrendingUp className='h-4 w-4' />
              <span>
                {getUsagePercentage(
                  stats.totalUses,
                  components.reduce((sum, c) => sum + (usageStats[c.id]?.totalUsage ?? 0), 0),
                )}
                % usage
              </span>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
});

ComponentUsageMatrix.displayName = 'ComponentUsageMatrix';
