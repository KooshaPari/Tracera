// DimensionFilters.tsx - Filter/highlight nodes by orthogonal dimensions
// Dimensions are cross-cutting concerns (maturity, complexity, coverage, risk)
// That apply to items regardless of their perspective

import {
  Activity,
  AlertTriangle,
  Boxes,
  Filter,
  Highlighter,
  Layers,
  Palette,
  Target,
  TrendingUp,
  X,
} from 'lucide-react';
import { memo, useCallback, useState } from 'react';

import type {
  ComplexityLevel,
  DimensionDisplayMode,
  DimensionFilter,
  MaturityLevel,
  RiskLevel,
} from '@tracertm/types';

import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Popover, PopoverContent, PopoverTrigger } from '@tracertm/ui/components/Popover';
import { Slider } from '@tracertm/ui/components/Slider';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

// =============================================================================
// TYPES
// =============================================================================

export interface DimensionFiltersProps {
  /** Currently active dimension filters */
  activeFilters: DimensionFilter[];
  /** Callback when filters change */
  onFiltersChange: (filters: DimensionFilter[]) => void;
  /** How to display matching items */
  displayMode: DimensionDisplayMode;
  /** Callback when display mode changes */
  onDisplayModeChange: (mode: DimensionDisplayMode) => void;
  /** Whether the filters panel is expanded */
  isExpanded?: boolean | undefined;
  /** Compact mode for toolbar */
  compact?: boolean | undefined;
}

interface DimensionConfig {
  id: keyof DimensionValues;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  type: 'enum' | 'range';
  values?: string[] | undefined;
  min?: number | undefined;
  max?: number | undefined;
}

interface DimensionValues {
  maturity: MaturityLevel;
  complexity: ComplexityLevel;
  coverage: number;
  risk: RiskLevel;
}

// =============================================================================
// CONSTANTS
// =============================================================================

const NOT_FOUND_INDEX = -1;
const DEFAULT_DIMENSION_SIZE = 0.5;
const MIN_DIMENSION_SIZE = 0.3;
const MAX_DIMENSION_SIZE = 1;
const SIZE_SCALING_FACTOR = 0.7;

// =============================================================================
// CONFIGURATION
// =============================================================================

const DIMENSION_CONFIGS: DimensionConfig[] = [
  {
    color: '#3b82f6',
    icon: TrendingUp,
    id: 'maturity',
    label: 'Maturity',
    type: 'enum',
    values: ['idea', 'draft', 'defined', 'implemented', 'verified', 'stable', 'deprecated'],
  },
  {
    color: '#f59e0b',
    icon: Boxes,
    id: 'complexity',
    label: 'Complexity',
    type: 'enum',
    values: ['trivial', 'simple', 'moderate', 'complex', 'very_complex'],
  },
  {
    color: '#22c55e',
    icon: Target,
    id: 'coverage',
    label: 'Coverage',
    max: 100,
    min: 0,
    type: 'range',
  },
  {
    color: '#ef4444',
    icon: AlertTriangle,
    id: 'risk',
    label: 'Risk',
    type: 'enum',
    values: ['none', 'low', 'medium', 'high', 'critical'],
  },
];

const DISPLAY_MODE_OPTIONS: {
  id: DimensionDisplayMode;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  { icon: Filter, id: 'filter', label: 'Filter' },
  { icon: Highlighter, id: 'highlight', label: 'Highlight' },
  { icon: Palette, id: 'color', label: 'Color' },
  { icon: Layers, id: 'size', label: 'Size' },
];

const MATURITY_COLORS: Record<MaturityLevel, string> = {
  defined: '#3b82f6',
  deprecated: '#ef4444',
  draft: '#64748b',
  idea: '#94a3b8',
  implemented: '#8b5cf6',
  stable: '#10b981',
  verified: '#22c55e',
};

const COMPLEXITY_COLORS: Record<ComplexityLevel, string> = {
  complex: '#ef4444',
  moderate: '#f59e0b',
  simple: '#84cc16',
  trivial: '#22c55e',
  very_complex: '#dc2626',
};

const RISK_COLORS: Record<RiskLevel, string> = {
  critical: '#dc2626',
  high: '#ef4444',
  low: '#84cc16',
  medium: '#f59e0b',
  none: '#22c55e',
};

// =============================================================================
// COMPONENT
// =============================================================================

function DimensionFiltersComponent({
  activeFilters,
  onFiltersChange,
  displayMode,
  onDisplayModeChange,
  isExpanded = false,
  compact = false,
}: DimensionFiltersProps) {
  // Track expansion state internally (currently unused but available for future use)
  const [_isOpen, _setIsOpen] = useState(isExpanded);

  const handleAddFilter = useCallback(
    (dimension: keyof DimensionValues, value: string | number | boolean | string[] | number[]) => {
      const existingIndex = activeFilters.findIndex((f) => f.dimension === dimension);
      const newFilter: DimensionFilter = {
        dimension,
        operator: Array.isArray(value) ? 'in' : 'eq',
        value,
      };

      if (existingIndex !== NOT_FOUND_INDEX) {
        const updated = [...activeFilters];
        updated[existingIndex] = newFilter;
        onFiltersChange(updated);
      } else {
        onFiltersChange([...activeFilters, newFilter]);
      }
    },
    [activeFilters, onFiltersChange],
  );

  const handleRemoveFilter = useCallback(
    (dimension: string) => {
      onFiltersChange(activeFilters.filter((f) => f.dimension !== dimension));
    },
    [activeFilters, onFiltersChange],
  );

  const handleClearAll = useCallback(() => {
    onFiltersChange([]);
  }, [onFiltersChange]);

  const getActiveFilterValue = (dimension: string) =>
    activeFilters.find((f) => f.dimension === dimension)?.value;

  if (compact) {
    return (
      <CompactDimensionFilters
        activeFilters={activeFilters}
        onFiltersChange={onFiltersChange}
        displayMode={displayMode}
        onDisplayModeChange={onDisplayModeChange}
      />
    );
  }

  return (
    <TooltipProvider>
      <div className='flex flex-col gap-2'>
        {/* Header with display mode toggle */}
        <div className='flex items-center justify-between'>
          <div className='flex items-center gap-2'>
            <Activity className='text-muted-foreground h-4 w-4' />
            <span className='text-sm font-medium'>Dimensions</span>
            {activeFilters.length > 0 && (
              <Badge variant='secondary' className='text-xs'>
                {activeFilters.length} active
              </Badge>
            )}
          </div>
          <div className='flex items-center gap-1'>
            {/* Display mode selector */}
            <div className='bg-muted/50 flex items-center gap-0.5 rounded-md p-0.5'>
              {DISPLAY_MODE_OPTIONS.map((option) => {
                const Icon = option.icon;
                const isActive = displayMode === option.id;
                return (
                  <Tooltip key={option.id} delayDuration={200}>
                    <TooltipTrigger asChild>
                      <Button
                        variant={isActive ? 'default' : 'ghost'}
                        size='sm'
                        className='h-7 w-7 p-0'
                        onClick={() => {
                          onDisplayModeChange(option.id);
                        }}
                      >
                        <Icon className='h-3.5 w-3.5' />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent side='bottom'>{option.label} mode</TooltipContent>
                  </Tooltip>
                );
              })}
            </div>
            {activeFilters.length > 0 && (
              <Button
                variant='ghost'
                size='sm'
                className='h-7 px-2 text-xs'
                onClick={handleClearAll}
              >
                Clear all
              </Button>
            )}
          </div>
        </div>

        {/* Dimension filters */}
        <div className='grid grid-cols-2 gap-2'>
          {DIMENSION_CONFIGS.map((config) => {
            const Icon = config.icon;
            const currentValue = getActiveFilterValue(config.id);
            const isActive = currentValue !== undefined;

            return (
              <Popover key={config.id}>
                <PopoverTrigger asChild>
                  <Button
                    variant={isActive ? 'default' : 'outline'}
                    size='sm'
                    className='h-8 justify-start gap-2'
                    style={
                      isActive
                        ? {
                            backgroundColor: config.color,
                            borderColor: config.color,
                          }
                        : undefined
                    }
                  >
                    <Icon className='h-3.5 w-3.5' />
                    <span className='text-xs'>{config.label}</span>
                    {isActive && (
                      <Badge
                        variant='secondary'
                        className='ml-auto bg-white/20 px-1.5 py-0 text-[10px]'
                      >
                        {formatFilterValue(currentValue)}
                      </Badge>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className='w-64 p-3' align='start'>
                  <DimensionFilterEditor
                    config={config}
                    value={currentValue}
                    onChange={(value) => {
                      handleAddFilter(config.id, value);
                    }}
                    onClear={() => {
                      handleRemoveFilter(config.id);
                    }}
                  />
                </PopoverContent>
              </Popover>
            );
          })}
        </div>

        {/* Active filter pills */}
        {activeFilters.length > 0 && (
          <div className='flex flex-wrap gap-1.5 pt-1'>
            {activeFilters.map((filter) => {
              const config = DIMENSION_CONFIGS.find((c) => c.id === filter.dimension);
              if (!config) {
                return null;
              }
              const Icon = config.icon;

              return (
                <Badge
                  key={filter.dimension}
                  variant='secondary'
                  className='gap-1.5 pr-1'
                  style={{
                    backgroundColor: `${config.color}20`,
                    color: config.color,
                  }}
                >
                  <Icon className='h-3 w-3' />
                  <span className='text-xs'>
                    {config.label}: {formatFilterValue(filter.value)}
                  </span>
                  <Button
                    variant='ghost'
                    size='sm'
                    className='h-4 w-4 p-0 hover:bg-transparent'
                    onClick={() => {
                      handleRemoveFilter(filter.dimension);
                    }}
                  >
                    <X className='h-3 w-3' />
                  </Button>
                </Badge>
              );
            })}
          </div>
        )}
      </div>
    </TooltipProvider>
  );
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

interface DimensionFilterEditorProps {
  config: DimensionConfig;
  value: string | number | boolean | string[] | number[] | undefined;
  onChange: (value: string | number | boolean | string[] | number[]) => void;
  onClear: () => void;
}

function DimensionFilterEditor({ config, value, onChange, onClear }: DimensionFilterEditorProps) {
  if (config.type === 'range') {
    const numValue = typeof value === 'number' ? value : 50;
    return (
      <div className='space-y-3'>
        <div className='flex items-center justify-between'>
          <span className='text-sm font-medium'>{config.label}</span>
          {value !== undefined && (
            <Button variant='ghost' size='sm' className='h-6 px-2 text-xs' onClick={onClear}>
              Clear
            </Button>
          )}
        </div>
        <div className='space-y-2'>
          <div className='text-muted-foreground flex items-center justify-between text-xs'>
            <span>{config.min}%</span>
            <span className='text-foreground font-medium'>{numValue}%</span>
            <span>{config.max}%</span>
          </div>
          <Slider
            value={[numValue]}
            min={config.min ?? 0}
            max={config.max ?? 100}
            step={5}
            onValueChange={([v]) => {
              if (v !== undefined) onChange(v);
            }}
            className='w-full'
          />
        </div>
        <p className='text-muted-foreground text-xs'>
          Show items with {config.label.toLowerCase()} &ge; {numValue}%
        </p>
      </div>
    );
  }

  // Enum type
  const selectedValues = Array.isArray(value) ? value : value ? [value] : [];

  return (
    <div className='space-y-3'>
      <div className='flex items-center justify-between'>
        <span className='text-sm font-medium'>{config.label}</span>
        {value !== undefined && (
          <Button variant='ghost' size='sm' className='h-6 px-2 text-xs' onClick={onClear}>
            Clear
          </Button>
        )}
      </div>
      <div className='flex flex-wrap gap-1.5'>
        {config.values?.map((v) => {
          const isSelected = selectedValues.includes(v);
          const color = getDimensionValueColor(config.id, v);

          return (
            <Button
              key={v}
              variant={isSelected ? 'default' : 'outline'}
              size='sm'
              className='h-7 text-xs capitalize'
              style={isSelected ? { backgroundColor: color, borderColor: color } : undefined}
              onClick={() => {
                if (isSelected) {
                  const newValues = selectedValues.filter((sv) => sv !== v);
                  if (newValues.length === 0) {
                    onClear();
                  } else {
                    onChange((newValues.length === 1 ? newValues[0] : newValues) as any);
                  }
                } else {
                  const newValues = [...selectedValues, v];
                  onChange((newValues.length === 1 ? newValues[0] : newValues) as any);
                }
              }}
            >
              {v.replace('_', ' ')}
            </Button>
          );
        })}
      </div>
    </div>
  );
}

interface CompactDimensionFiltersProps {
  activeFilters: DimensionFilter[];
  onFiltersChange: (filters: DimensionFilter[]) => void;
  displayMode: DimensionDisplayMode;
  onDisplayModeChange: (mode: DimensionDisplayMode) => void;
}

function CompactDimensionFilters({
  activeFilters,
  onFiltersChange,
  displayMode,
  onDisplayModeChange,
}: CompactDimensionFiltersProps) {
  return (
    <TooltipProvider>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant={activeFilters.length > 0 ? 'default' : 'outline'}
            size='sm'
            className='h-8 gap-2'
          >
            <Activity className='h-3.5 w-3.5' />
            <span className='text-xs'>Dimensions</span>
            {activeFilters.length > 0 && (
              <Badge variant='secondary' className='bg-white/20 px-1.5 py-0 text-[10px]'>
                {activeFilters.length}
              </Badge>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className='w-80 p-4' align='end'>
          <DimensionFiltersComponent
            activeFilters={activeFilters}
            onFiltersChange={onFiltersChange}
            displayMode={displayMode}
            onDisplayModeChange={onDisplayModeChange}
          />
        </PopoverContent>
      </Popover>
    </TooltipProvider>
  );
}

// =============================================================================
// UTILITIES
// =============================================================================

function formatFilterValue(
  value: string | number | boolean | string[] | number[] | undefined,
): string {
  if (value === undefined) {
    return '';
  }
  if (Array.isArray(value)) {
    return value.length === 1 ? String(value[0]) : `${value.length} selected`;
  }
  if (typeof value === 'number') {
    return `${value}%`;
  }
  return String(value).replace('_', ' ');
}

function getDimensionValueColor(dimension: string, value: string): string {
  if (dimension === 'maturity') {
    return MATURITY_COLORS[value as MaturityLevel] || '#64748b';
  }
  if (dimension === 'complexity') {
    return COMPLEXITY_COLORS[value as ComplexityLevel] || '#64748b';
  }
  if (dimension === 'risk') {
    return RISK_COLORS[value as RiskLevel] || '#64748b';
  }
  return '#64748b';
}

// =============================================================================
// EXPORTS
// =============================================================================

export const DimensionFilters = memo(DimensionFiltersComponent);

// Export utility functions for use in graph rendering
export { DIMENSION_CONFIGS, MATURITY_COLORS, COMPLEXITY_COLORS, RISK_COLORS };

/**
 * Apply dimension filters to a list of items
 * Returns items that match all active filters
 */
export function applyDimensionFilters<T extends { dimensions?: Record<string, unknown> }>(
  items: T[],
  filters: DimensionFilter[],
): T[] {
  if (filters.length === 0) {
    return items;
  }

  return items.filter((item) =>
    filters.every((filter) => {
      const itemValue = item.dimensions?.[filter.dimension];
      if (itemValue === undefined) {
        return false;
      }

      switch (filter.operator) {
        case 'eq': {
          return itemValue === filter.value;
        }
        case 'neq': {
          return itemValue !== filter.value;
        }
        case 'gt': {
          return typeof itemValue === 'number' && itemValue > (filter.value as number);
        }
        case 'gte': {
          return typeof itemValue === 'number' && itemValue >= (filter.value as number);
        }
        case 'lt': {
          return typeof itemValue === 'number' && itemValue < (filter.value as number);
        }
        case 'lte': {
          return typeof itemValue === 'number' && itemValue <= (filter.value as number);
        }
        case 'in': {
          return (
            Array.isArray(filter.value) && (filter.value as any[]).includes(itemValue as string)
          );
        }
        case 'not_in': {
          return (
            Array.isArray(filter.value) && !(filter.value as any[]).includes(itemValue as string)
          );
        }
        default: {
          return true;
        }
      }
    }),
  );
}

/**
 * Get color for an item based on its dimension value and the current color dimension
 */
export function getDimensionColor(
  dimensions: Record<string, unknown> | undefined,
  colorDimension: keyof DimensionValues,
): string | undefined {
  if (!dimensions) {
    return undefined;
  }
  const value = dimensions[colorDimension];
  if (value === undefined) {
    return undefined;
  }

  const safeStr =
    typeof value === 'object' && value !== null ? JSON.stringify(value) : String(value);
  return getDimensionValueColor(colorDimension, safeStr);
}

/**
 * Get relative size (0-1) for an item based on its dimension value
 */
export function getDimensionSize(
  dimensions: Record<string, unknown> | undefined,
  sizeDimension: keyof DimensionValues,
): number {
  if (!dimensions) {
    return DEFAULT_DIMENSION_SIZE;
  }
  const value = dimensions[sizeDimension];
  if (value === undefined) {
    return DEFAULT_DIMENSION_SIZE;
  }

  if (typeof value === 'number') {
    // Normalize 0-100 to MIN_DIMENSION_SIZE-MAX_DIMENSION_SIZE
    return MIN_DIMENSION_SIZE + (value / 100) * SIZE_SCALING_FACTOR;
  }

  // For enum types, map to size
  const config = DIMENSION_CONFIGS.find((c) => c.id === sizeDimension);
  if (config?.values) {
    const index = config.values.indexOf(value as string);
    if (index !== NOT_FOUND_INDEX) {
      return MIN_DIMENSION_SIZE + (index / (config.values.length - 1)) * SIZE_SCALING_FACTOR;
    }
  }

  return DEFAULT_DIMENSION_SIZE;
}
