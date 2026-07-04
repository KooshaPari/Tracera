// Advanced Filter Controls for Graph Visualization
// Provides multi-select filters for node types, perspectives, and attributes

import { Check, ChevronDown, X } from 'lucide-react';
import { useCallback, useMemo, useState } from 'react';

import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Popover, PopoverContent, PopoverTrigger } from '@tracertm/ui/components/Popover';
import { Separator } from '@tracertm/ui/components/Separator';

import type { GraphPerspective } from './types';

import { ENHANCED_TYPE_COLORS, PERSPECTIVE_CONFIGS } from './types';

interface FilterControlsProps {
  // Perspective filter
  perspective?: GraphPerspective | undefined;
  onPerspectiveChange?: ((perspective: GraphPerspective) => void) | undefined;

  // Node type filter
  nodeTypes?: string[] | undefined;
  selectedNodeTypes?: string[] | undefined;
  onNodeTypeFilterChange?: ((types: string[]) => void) | undefined;

  // Status filter (optional)
  statuses?: string[] | undefined;
  selectedStatuses?: string[] | undefined;
  onStatusFilterChange?: ((statuses: string[]) => void) | undefined;

  // Callbacks
  onClose?: (() => void) | undefined;
  className?: string | undefined;
}

export function FilterControls({
  perspective,
  onPerspectiveChange,
  nodeTypes = [],
  selectedNodeTypes = [],
  onNodeTypeFilterChange,
  statuses = [],
  selectedStatuses = [],
  onStatusFilterChange,
  onClose,
  className,
}: FilterControlsProps) {
  const [showPerspectives, setShowPerspectives] = useState(false);
  const [showNodeTypes, setShowNodeTypes] = useState(false);
  const [showStatuses, setShowStatuses] = useState(false);

  // Handle perspective selection
  const handlePerspectiveSelect = useCallback(
    (p: GraphPerspective) => {
      onPerspectiveChange?.(p);
      setShowPerspectives(false);
    },
    [onPerspectiveChange],
  );

  // Handle node type toggle
  const handleNodeTypeToggle = useCallback(
    (type: string) => {
      if (!onNodeTypeFilterChange) {
        return;
      }

      const newTypes = selectedNodeTypes.includes(type)
        ? selectedNodeTypes.filter((t) => t !== type)
        : [...selectedNodeTypes, type];

      onNodeTypeFilterChange(newTypes);
    },
    [selectedNodeTypes, onNodeTypeFilterChange],
  );

  // Handle status toggle
  const handleStatusToggle = useCallback(
    (status: string) => {
      if (!onStatusFilterChange) {
        return;
      }

      const newStatuses = selectedStatuses.includes(status)
        ? selectedStatuses.filter((s) => s !== status)
        : [...selectedStatuses, status];

      onStatusFilterChange(newStatuses);
    },
    [selectedStatuses, onStatusFilterChange],
  );

  // Clear all filters
  const handleClearAll = useCallback(() => {
    onPerspectiveChange?.('all');
    onNodeTypeFilterChange?.([]);
    onStatusFilterChange?.([]);
  }, [onPerspectiveChange, onNodeTypeFilterChange, onStatusFilterChange]);

  // Active filter count
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (perspective && perspective !== 'all') {
      count += 1;
    }
    if (selectedNodeTypes.length > 0) {
      count += 1;
    }
    if (selectedStatuses.length > 0) {
      count += 1;
    }
    return count;
  }, [perspective, selectedNodeTypes, selectedStatuses]);

  // Current perspective config
  const currentPerspective = useMemo(
    () => PERSPECTIVE_CONFIGS.find((c) => c.id === perspective) ?? PERSPECTIVE_CONFIGS[0],
    [perspective],
  );

  return (
    <div className={`flex flex-col gap-3 ${className ?? ''}`}>
      <div className='flex items-center justify-between'>
        <h3 className='text-sm font-medium'>Filters</h3>
        <div className='flex items-center gap-2'>
          {activeFilterCount > 0 && (
            <>
              <Badge variant='secondary' className='text-xs'>
                {activeFilterCount} active
              </Badge>
              <Button variant='ghost' size='sm' onClick={handleClearAll} className='h-7 text-xs'>
                Clear all
              </Button>
            </>
          )}
          {onClose && (
            <Button variant='ghost' size='sm' onClick={onClose} className='h-7 w-7 p-0'>
              <X className='h-3.5 w-3.5' />
            </Button>
          )}
        </div>
      </div>

      <div className='flex flex-wrap items-center gap-2'>
        {/* Perspective filter */}
        {onPerspectiveChange && (
          <Popover open={showPerspectives} onOpenChange={setShowPerspectives}>
            <PopoverTrigger asChild>
              <Button
                variant='outline'
                size='sm'
                className='h-8 gap-2'
                style={{
                  borderColor: currentPerspective?.color,
                  color: currentPerspective?.color,
                }}
              >
                <span className='text-xs font-medium'>{currentPerspective?.label ?? 'All'}</span>
                <ChevronDown className='h-3 w-3 opacity-50' />
              </Button>
            </PopoverTrigger>
            <PopoverContent className='w-64 p-2' align='start'>
              <div className='space-y-1'>
                {PERSPECTIVE_CONFIGS.map((config) => (
                  <button
                    key={config.id}
                    onClick={() => {
                      handlePerspectiveSelect(config.id);
                    }}
                    className='hover:bg-accent flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left transition-colors'
                  >
                    <div
                      className='h-3 w-3 shrink-0 rounded-full'
                      style={{ backgroundColor: config.color }}
                    />
                    <div className='min-w-0 flex-1'>
                      <div className='text-sm font-medium'>{config.label}</div>
                      <div className='text-muted-foreground truncate text-xs'>
                        {config.description}
                      </div>
                    </div>
                    {perspective === config.id && (
                      <Check className='text-primary h-4 w-4 shrink-0' />
                    )}
                  </button>
                ))}
              </div>
            </PopoverContent>
          </Popover>
        )}

        <Separator orientation='vertical' className='h-6' />

        {/* Node type filter */}
        {onNodeTypeFilterChange && nodeTypes.length > 0 && (
          <Popover open={showNodeTypes} onOpenChange={setShowNodeTypes}>
            <PopoverTrigger asChild>
              <Button variant='outline' size='sm' className='h-8 gap-2'>
                <span className='text-xs font-medium'>
                  Node Types
                  {selectedNodeTypes.length > 0 && (
                    <Badge variant='secondary' className='ml-1.5 px-1 text-xs'>
                      {selectedNodeTypes.length}
                    </Badge>
                  )}
                </span>
                <ChevronDown className='h-3 w-3 opacity-50' />
              </Button>
            </PopoverTrigger>
            <PopoverContent className='w-64 p-2' align='start'>
              <div className='max-h-64 space-y-1 overflow-y-auto'>
                {nodeTypes.map((type) => {
                  const isSelected = selectedNodeTypes.includes(type);
                  const color = ENHANCED_TYPE_COLORS[type] ?? '#64748b';

                  return (
                    <button
                      key={type}
                      onClick={() => {
                        handleNodeTypeToggle(type);
                      }}
                      className='hover:bg-accent flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left transition-colors'
                    >
                      <div
                        className='h-3 w-3 shrink-0 rounded'
                        style={{ backgroundColor: color }}
                      />
                      <span className='flex-1 text-sm capitalize'>{type.replaceAll('_', ' ')}</span>
                      {isSelected && <Check className='text-primary h-4 w-4 shrink-0' />}
                    </button>
                  );
                })}
              </div>
            </PopoverContent>
          </Popover>
        )}

        {/* Status filter */}
        {onStatusFilterChange && statuses.length > 0 && (
          <>
            <Separator orientation='vertical' className='h-6' />
            <Popover open={showStatuses} onOpenChange={setShowStatuses}>
              <PopoverTrigger asChild>
                <Button variant='outline' size='sm' className='h-8 gap-2'>
                  <span className='text-xs font-medium'>
                    Status
                    {selectedStatuses.length > 0 && (
                      <Badge variant='secondary' className='ml-1.5 px-1 text-xs'>
                        {selectedStatuses.length}
                      </Badge>
                    )}
                  </span>
                  <ChevronDown className='h-3 w-3 opacity-50' />
                </Button>
              </PopoverTrigger>
              <PopoverContent className='w-48 p-2' align='start'>
                <div className='space-y-1'>
                  {statuses.map((status) => {
                    const isSelected = selectedStatuses.includes(status);

                    return (
                      <button
                        key={status}
                        onClick={() => {
                          handleStatusToggle(status);
                        }}
                        className='hover:bg-accent flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left transition-colors'
                      >
                        <span className='flex-1 text-sm capitalize'>
                          {status.replaceAll('_', ' ')}
                        </span>
                        {isSelected && <Check className='text-primary h-4 w-4 shrink-0' />}
                      </button>
                    );
                  })}
                </div>
              </PopoverContent>
            </Popover>
          </>
        )}
      </div>

      {/* Active filters summary */}
      {activeFilterCount > 0 && (
        <div className='flex flex-wrap gap-1.5'>
          {perspective && perspective !== 'all' && (
            <Badge
              variant='secondary'
              className='gap-1 text-xs'
              style={{
                backgroundColor: currentPerspective?.color + '20',
                color: currentPerspective?.color,
              }}
            >
              <span>{currentPerspective?.label}</span>
              <button onClick={() => onPerspectiveChange?.('all')} className='hover:opacity-70'>
                <X className='h-3 w-3' />
              </button>
            </Badge>
          )}

          {selectedNodeTypes.map((type) => {
            const color = ENHANCED_TYPE_COLORS[type] ?? '#64748b';
            return (
              <Badge
                key={type}
                variant='secondary'
                className='gap-1 text-xs'
                style={{
                  backgroundColor: color + '20',
                  color: color,
                }}
              >
                <span className='capitalize'>{type.replaceAll('_', ' ')}</span>
                <button
                  onClick={() => {
                    handleNodeTypeToggle(type);
                  }}
                  className='hover:opacity-70'
                >
                  <X className='h-3 w-3' />
                </button>
              </Badge>
            );
          })}

          {selectedStatuses.map((status) => (
            <Badge key={status} variant='secondary' className='gap-1 text-xs'>
              <span className='capitalize'>{status.replaceAll('_', ' ')}</span>
              <button
                onClick={() => {
                  handleStatusToggle(status);
                }}
                className='hover:opacity-70'
              >
                <X className='h-3 w-3' />
              </button>
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}
