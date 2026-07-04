/**
 * Edge Type Filter Component
 * Allows users to selectively show/hide edge types for managing visual complexity
 */

import { Filter } from 'lucide-react';
import { useCallback, useMemo, useState } from 'react';

import type { LinkType } from '@tracertm/types';

import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@tracertm/ui/components/DropdownMenu';

import { LINK_STYLES } from './types';

export interface EdgeTypeFilterProps {
  availableTypes: LinkType[];
  enabledTypes: Set<LinkType>;
  onToggleType: (type: LinkType) => void;
  onEnableAll: () => void;
  onDisableAll: () => void;
  edgeStats?: Record<LinkType, number>;
  compact?: boolean;
}

/**
 * Edge Type Filter - semantic filtering of edge types
 */
export function EdgeTypeFilter({
  availableTypes,
  enabledTypes,
  onToggleType,
  onEnableAll,
  onDisableAll,
  edgeStats,
  compact = false,
}: EdgeTypeFilterProps) {
  const sortedTypes = useMemo(
    () =>
      [...availableTypes].toSorted((a, b) => {
        if (edgeStats) {
          return (edgeStats[b] || 0) - (edgeStats[a] || 0);
        }
        return a.localeCompare(b);
      }),
    [availableTypes, edgeStats],
  );

  const activeCount = enabledTypes.size;
  const totalCount = availableTypes.length;

  if (compact) {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <span>
            <Button variant='outline' size='sm' className='h-8 gap-1'>
              <Filter className='h-3 w-3' />
              <span className='text-xs'>
                Types ({activeCount}/{totalCount})
              </span>
            </Button>
          </span>
        </DropdownMenuTrigger>
        <DropdownMenuContent align='start' className='w-64'>
          <DropdownMenuLabel className='flex items-center justify-between'>
            <span>Edge Types</span>
            <div className='flex gap-1'>
              <Button variant='ghost' size='sm' onClick={onEnableAll} className='h-6 px-2 text-xs'>
                All
              </Button>
              <Button variant='ghost' size='sm' onClick={onDisableAll} className='h-6 px-2 text-xs'>
                None
              </Button>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          {sortedTypes.map((type) => {
            const style = LINK_STYLES[type] ?? {
              arrow: false,
              color: '#64748b',
              dashed: false,
            };
            const count = edgeStats?.[type] ?? 0;
            const isEnabled = enabledTypes.size === 0 || enabledTypes.has(type);

            return (
              <DropdownMenuCheckboxItem
                key={type}
                checked={isEnabled}
                onCheckedChange={() => {
                  onToggleType(type);
                }}
                className='flex items-center justify-between'
              >
                <div className='flex items-center gap-2'>
                  <div
                    className='h-2 w-4 rounded'
                    style={{
                      backgroundColor: style.color,
                      opacity: isEnabled ? 1 : 0.3,
                    }}
                  />
                  <span className='text-xs capitalize'>{type.replaceAll('_', ' ')}</span>
                </div>
                {edgeStats && (
                  <Badge variant='secondary' className='ml-2 h-4 px-1 text-[10px]'>
                    {count}
                  </Badge>
                )}
              </DropdownMenuCheckboxItem>
            );
          })}
        </DropdownMenuContent>
      </DropdownMenu>
    );
  }

  return (
    <Card className='p-3'>
      <div className='mb-3 flex items-center justify-between'>
        <div className='flex items-center gap-2'>
          <Filter className='text-muted-foreground h-4 w-4' />
          <span className='text-sm font-medium'>Edge Types</span>
          <Badge variant='secondary' className='text-xs'>
            {activeCount === 0 ? 'All' : `${activeCount}/${totalCount}`}
          </Badge>
        </div>
        <div className='flex gap-1'>
          <Button variant='ghost' size='sm' onClick={onEnableAll} className='h-6 px-2 text-xs'>
            All
          </Button>
          <Button variant='ghost' size='sm' onClick={onDisableAll} className='h-6 px-2 text-xs'>
            None
          </Button>
        </div>
      </div>

      <div className='space-y-1.5'>
        {sortedTypes.map((type) => {
          const style = LINK_STYLES[type] ?? {
            arrow: false,
            color: '#64748b',
            dashed: false,
          };
          const count = edgeStats?.[type] ?? 0;
          const isEnabled = enabledTypes.size === 0 || enabledTypes.has(type);

          return (
            <button
              key={type}
              onClick={() => {
                onToggleType(type);
              }}
              className={`hover:bg-accent flex w-full items-center justify-between rounded-md p-2 transition-colors ${
                isEnabled ? 'bg-accent/50' : 'opacity-50'
              }`}
            >
              <div className='flex items-center gap-2'>
                <div
                  className='h-3 w-6 rounded'
                  style={{
                    backgroundColor: style.color,
                    opacity: isEnabled ? 1 : 0.5,
                  }}
                />
                <span className='text-sm capitalize'>{type.replaceAll('_', ' ')}</span>
              </div>
              <div className='flex items-center gap-2'>
                {edgeStats && (
                  <Badge variant='secondary' className='text-xs'>
                    {count}
                  </Badge>
                )}
                {isEnabled && <div className='bg-primary h-2 w-2 rounded-full' />}
              </div>
            </button>
          );
        })}
      </div>
    </Card>
  );
}

/**
 * Hook for managing edge type filter state
 */
export function useEdgeTypeFilter(availableTypes: LinkType[]) {
  const [enabledTypes, setEnabledTypes] = useState<Set<LinkType>>(new Set());

  const toggleType = useCallback((type: LinkType) => {
    setEnabledTypes((prev) => {
      const next = new Set(prev);
      if (next.has(type)) {
        next.delete(type);
      } else {
        next.add(type);
      }
      return next;
    });
  }, []);

  const enableAll = useCallback(() => {
    setEnabledTypes(new Set());
  }, []);

  const disableAll = useCallback(() => {
    setEnabledTypes(new Set(availableTypes));
  }, [availableTypes]);

  const resetToDefault = useCallback(() => {
    setEnabledTypes(new Set());
  }, []);

  return {
    disableAll,
    enableAll,
    enabledTypes,
    resetToDefault,
    setEnabledTypes,
    toggleType,
  };
}
