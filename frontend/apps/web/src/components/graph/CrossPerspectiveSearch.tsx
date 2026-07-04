import { ChevronDown, ChevronUp, Link as LinkIcon, Network, Search, X } from 'lucide-react';
import { memo, useCallback, useMemo, useState } from 'react';

import type { Item, ItemStatus, Link } from '@tracertm/types';

import { cn } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { Input } from '@tracertm/ui/components/Input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';

import type {
  CrossPerspectiveSearchResult,
  GroupedSearchResults,
  SearchFilters,
} from './hooks/useCrossPerspectiveSearch';

import { useCrossPerspectiveSearch } from './hooks/useCrossPerspectiveSearch';

interface CrossPerspectiveSearchProps {
  items: Item[];
  links: Link[];
  onSelect: (itemId: string) => void;
  onHighlight: (itemId: string | null) => void;
  compact?: boolean;
  className?: string;
  maxResultsPerPerspective?: number;
}

/**
 * Get perspective color for visual distinction
 */
function getPerspectiveColor(perspective: string): string {
  const colors: Record<string, string> = {
    api: '#f59e0b',
    architecture: '#f97316',
    code: '#8b5cf6',
    configuration: '#a855f7',
    database: '#ec4899',
    dataflow: '#0ea5e9',
    dependency: '#ef4444',
    deployment: '#14b8a6',
    documentation: '#6366f1',
    domain: '#f43f5e',
    feature: '#3b82f6',
    infrastructure: '#84cc16',
    journey: '#d946ef',
    monitoring: '#fb923c',
    performance: '#22c55e',
    security: '#8b5cf6',
    test: '#10b981',
    wireframe: '#06b6d4',
  };
  return colors[perspective.toLowerCase()] ?? '#64748b';
}

/**
 * Get status color
 */
function getStatusColor(status: ItemStatus): string {
  const colors: Record<ItemStatus, string> = {
    blocked: '#ef4444',
    cancelled: '#94a3b8',
    done: '#10b981',
    in_progress: '#f59e0b',
    todo: '#64748b',
  };
  return colors[status] || '#64748b';
}

/**
 * Format confidence score as percentage
 */
function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

/**
 * Highlight matching text in content
 */
function highlightMatch(text: string, query: string): React.ReactNode {
  if (!text || !query.trim()) {
    return text;
  }

  const lowerText = text.toLowerCase();
  const lowerQuery = query.toLowerCase();
  const index = lowerText.indexOf(lowerQuery);

  if (index === -1) {
    return text;
  }

  return (
    <>
      {text.slice(0, index)}
      <mark className='bg-yellow-200/60 font-semibold dark:bg-yellow-900/40'>
        {text.slice(index, index + query.length)}
      </mark>
      {text.slice(index + query.length)}
    </>
  );
}

/**
 * Result item for a single search result
 */
interface ResultItemProps {
  result: CrossPerspectiveSearchResult;
  query: string;
  isSelected: boolean;
  perspectiveColor: string;
  onSelect: (itemId: string) => void;
  onHighlight: (itemId: string) => void;
  onMouseEnter: () => void;
}

const ResultItem = memo(function ResultItemComponent({
  result,
  query,
  isSelected,
  perspectiveColor,
  onSelect,
  onMouseEnter,
}: ResultItemProps) {
  return (
    <div
      className={cn(
        'px-4 py-3 border-b last:border-b-0 cursor-pointer transition-colors',
        isSelected && 'bg-accent',
      )}
      onClick={() => {
        onSelect(result.item.id);
      }}
      onMouseEnter={onMouseEnter}
    >
      <div className='space-y-2'>
        {/* Title and Perspective */}
        <div className='flex items-start justify-between gap-3'>
          <div className='min-w-0 flex-1'>
            <h4 className='truncate text-sm font-semibold'>
              {highlightMatch(result.item.title, query)}
            </h4>
            <p className='text-muted-foreground mt-0.5 text-xs'>
              {result.item.type && (
                <>
                  <span>{result.item.type}</span>
                  {result.item.status && <span className='mx-1'>•</span>}
                </>
              )}
              {result.item.status && (
                <span style={{ color: getStatusColor(result.item.status) }}>
                  {result.item.status.replace('_', ' ')}
                </span>
              )}
            </p>
          </div>
          <Badge
            variant='outline'
            className='shrink-0 text-[10px]'
            style={{
              backgroundColor: `${perspectiveColor}20`,
              borderColor: `${perspectiveColor}40`,
              color: perspectiveColor,
            }}
          >
            {result.perspective.toUpperCase()}
          </Badge>
        </div>

        {/* Description if matched */}
        {result.matchType === 'description' && result.item.description && (
          <p className='text-muted-foreground line-clamp-2 text-xs'>
            {highlightMatch(result.item.description, query)}
          </p>
        )}

        {/* Equivalences section */}
        {result.equivalences.length > 0 && (
          <div className='flex flex-wrap items-start gap-1.5'>
            {result.equivalences.map((equiv) => (
              <div
                key={equiv.equivalentItemId}
                className='bg-muted/50 flex items-center gap-1 rounded-full px-2 py-1 text-[10px]'
              >
                <LinkIcon className='text-primary h-3 w-3' />
                <span className='text-muted-foreground'>{equiv.equivalentPerspective}</span>
                <Badge variant='secondary' className='h-4 px-1 text-[8px]'>
                  {formatConfidence(equiv.confidence)}
                </Badge>
              </div>
            ))}
          </div>
        )}

        {/* Score */}
        <div className='flex items-center justify-between'>
          <div className='text-muted-foreground text-[10px]'>
            Match score: <span className='font-semibold'>{result.score}</span>
          </div>
          {result.matchType !== 'title' && (
            <Badge variant='secondary' className='text-[10px]'>
              {result.matchType}
            </Badge>
          )}
        </div>
      </div>
    </div>
  );
});

/**
 * Perspective group section
 */
interface PerspectiveGroupProps {
  group: GroupedSearchResults;
  query: string;
  perspectiveColor: string;
  selectedResultIndex: number;
  globalIndexOffset: number;
  maxResults: number;
  onSelect: (itemId: string) => void;
  onHighlight: (itemId: string) => void;
  onSelectResult: (index: number) => void;
}

const PerspectiveGroup = memo(function PerspectiveGroupComponent({
  group,
  query,
  perspectiveColor,
  selectedResultIndex,
  globalIndexOffset,
  maxResults,
  onSelect,
  onHighlight,
  onSelectResult,
}: PerspectiveGroupProps) {
  const displayResults = group.results.slice(0, maxResults);
  const hiddenCount = group.results.length - displayResults.length;

  return (
    <div className='border-t first:border-t-0'>
      {/* Group header */}
      <div
        className='bg-muted/30 sticky top-0 z-10 flex items-center justify-between px-4 py-2'
        style={{ borderLeftColor: perspectiveColor, borderLeftWidth: '4px' }}
      >
        <div className='flex items-center gap-2'>
          <Network className='h-4 w-4' style={{ color: perspectiveColor }} />
          <span className='text-sm font-semibold'>{group.perspective}</span>
          <Badge variant='secondary' className='text-[10px]'>
            {group.count}
          </Badge>
        </div>
      </div>

      {/* Results in group */}
      {displayResults.map((result, idx) => {
        const globalIndex = globalIndexOffset + idx;
        return (
          <ResultItem
            key={result.item.id}
            result={result}
            query={query}
            isSelected={globalIndex === selectedResultIndex}
            perspectiveColor={perspectiveColor}
            onSelect={onSelect}
            onHighlight={onHighlight}
            onMouseEnter={() => {
              onSelectResult(globalIndex);
            }}
          />
        );
      })}

      {/* Hidden results indicator */}
      {hiddenCount > 0 && (
        <div className='text-muted-foreground bg-muted/10 px-4 py-2 text-center text-xs'>
          +{hiddenCount} more in {group.perspective}
        </div>
      )}
    </div>
  );
});

/**
 * Cross-perspective search component
 */
function CrossPerspectiveSearchComponent({
  items,
  links,
  onSelect,
  onHighlight,
  compact = false,
  className,
  maxResultsPerPerspective = 5,
}: CrossPerspectiveSearchProps) {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({});
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedResultIndex, setSelectedResultIndex] = useState(0);
  const { performSearch, addToHistory, getHistory } = useCrossPerspectiveSearch();

  const results = useMemo(
    () => performSearch(items, links, query, filters),
    [items, links, query, filters, performSearch],
  );

  const totalResultsCount = useMemo(
    () => results.reduce((sum, group) => sum + group.count, 0),
    [results],
  );

  const handleSearch = useCallback((newQuery: string) => {
    setQuery(newQuery);
    setSelectedResultIndex(0);
  }, []);

  const handleClear = useCallback(() => {
    setQuery('');
    setFilters({});
    setSelectedResultIndex(0);
  }, []);

  const handleSelectResult = useCallback((index: number) => {
    setSelectedResultIndex(index);
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      // Calculate total results
      let totalResults = 0;
      for (const group of results) {
        totalResults += Math.min(group.count, maxResultsPerPerspective);
      }

      if (!totalResults) {
        return;
      }

      switch (e.key) {
        case 'ArrowDown': {
          e.preventDefault();
          setSelectedResultIndex((prev) => Math.min(prev + 1, totalResults - 1));
          break;
        }
        case 'ArrowUp': {
          e.preventDefault();
          setSelectedResultIndex((prev) => Math.max(prev - 1, 0));
          break;
        }
        case 'Enter': {
          e.preventDefault();
          // Find and select the result at the current index
          let currentIndex = 0;
          for (const group of results) {
            const groupSize = Math.min(group.count, maxResultsPerPerspective);
            if (selectedResultIndex < currentIndex + groupSize) {
              const resultIdx = selectedResultIndex - currentIndex;
              const result = group.results[resultIdx];
              if (result) onSelect(result.item.id);
              break;
            }
            currentIndex += groupSize;
          }
          break;
        }
        case 'Escape': {
          e.preventDefault();
          handleClear();
          break;
        }
      }
    },
    [results, selectedResultIndex, maxResultsPerPerspective, onSelect, handleClear],
  );

  const handleSelectItem = useCallback(
    (itemId: string) => {
      addToHistory(query);
      onSelect(itemId);
    },
    [query, onSelect, addToHistory],
  );

  if (compact) {
    return (
      <div className={cn('relative', className)}>
        <div className='flex items-center gap-2'>
          <Search className='text-muted-foreground h-4 w-4' />
          <Input
            placeholder='Search across perspectives...'
            value={query}
            onChange={(e) => {
              handleSearch(e.target.value);
            }}
            onKeyDown={handleKeyDown}
            className='h-8 text-sm'
          />
          {query && (
            <Button variant='ghost' size='sm' className='h-8 w-8 p-0' onClick={handleClear}>
              <X className='h-4 w-4' />
            </Button>
          )}
          {totalResultsCount > 0 && (
            <Badge variant='secondary' className='text-xs'>
              {totalResultsCount}
            </Badge>
          )}
        </div>

        {/* Compact results dropdown */}
        {query && results.length > 0 && (
          <div className='bg-card absolute top-full right-0 left-0 z-50 mt-2 max-h-72 overflow-y-auto rounded-lg border shadow-lg'>
            {results.map((group) => {
              const perspectiveColor = getPerspectiveColor(group.perspective);
              let globalIndexOffset = 0;

              // Calculate offset
              for (let i = 0; i < results.indexOf(group); i += 1) {
                globalIndexOffset += Math.min(results[i]?.count ?? 0, maxResultsPerPerspective);
              }

              return (
                <PerspectiveGroup
                  key={group.perspective}
                  group={group}
                  query={query}
                  perspectiveColor={perspectiveColor}
                  selectedResultIndex={selectedResultIndex}
                  globalIndexOffset={globalIndexOffset}
                  maxResults={Math.ceil(maxResultsPerPerspective / results.length)}
                  onSelect={handleSelectItem}
                  onHighlight={onHighlight}
                  onSelectResult={handleSelectResult}
                />
              );
            })}
          </div>
        )}
      </div>
    );
  }

  const searchHistory = getHistory();

  return (
    <Card className={cn('overflow-hidden', className)}>
      {/* Header */}
      <div className='space-y-3 border-b p-4'>
        <div className='flex items-center gap-2'>
          <Search className='text-muted-foreground h-4 w-4 shrink-0' />
          <Input
            placeholder='Search across all perspectives...'
            value={query}
            onChange={(e) => {
              handleSearch(e.target.value);
            }}
            onKeyDown={handleKeyDown}
            className='flex-1'
          />
          {query && (
            <Button variant='ghost' size='sm' className='h-8 w-8 p-0' onClick={handleClear}>
              <X className='h-4 w-4' />
            </Button>
          )}
          <Button
            variant='ghost'
            size='sm'
            className='h-8 w-8 p-0'
            onClick={() => {
              setIsExpanded(!isExpanded);
            }}
          >
            {isExpanded ? <ChevronUp className='h-4 w-4' /> : <ChevronDown className='h-4 w-4' />}
          </Button>
        </div>

        {/* Filters section */}
        {isExpanded && (
          <div className='space-y-3 border-t pt-2'>
            <div className='grid grid-cols-2 gap-3'>
              {/* Status filter */}
              <div>
                <label className='text-muted-foreground mb-1.5 block text-[10px] font-semibold uppercase'>
                  Status
                </label>
                <Select
                  value={filters.status ?? ''}
                  onValueChange={(val) => {
                    setFilters((prev) => ({
                      ...prev,
                      status: val || undefined,
                    }));
                  }}
                >
                  <SelectTrigger className='h-8 text-sm'>
                    <SelectValue placeholder='All statuses' />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value=''>All statuses</SelectItem>
                    <SelectItem value='todo'>To Do</SelectItem>
                    <SelectItem value='in_progress'>In Progress</SelectItem>
                    <SelectItem value='done'>Done</SelectItem>
                    <SelectItem value='blocked'>Blocked</SelectItem>
                    <SelectItem value='cancelled'>Cancelled</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Type filter */}
              <div>
                <label className='text-muted-foreground mb-1.5 block text-[10px] font-semibold uppercase'>
                  Type
                </label>
                <Select
                  value={filters.type ?? ''}
                  onValueChange={(val) => {
                    setFilters((prev) => ({
                      ...prev,
                      type: val || undefined,
                    }));
                  }}
                >
                  <SelectTrigger className='h-8 text-sm'>
                    <SelectValue placeholder='All types' />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value=''>All types</SelectItem>
                    {[...new Set(items.map((item) => item.type).filter(Boolean))].map((type) => (
                      <SelectItem key={type} value={type || ''}>
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Summary */}
            <div className='text-muted-foreground text-center text-xs'>
              {totalResultsCount > 0
                ? `Found ${totalResultsCount} result${totalResultsCount !== 1 ? 's' : ''} across ${results.length} perspective${results.length !== 1 ? 's' : ''}`
                : 'Enter a search query to find items'}
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      {results.length > 0 && query ? (
        <div className='max-h-96 overflow-y-auto'>
          {results.map((group) => {
            const perspectiveColor = getPerspectiveColor(group.perspective);
            let globalIndexOffset = 0;

            // Calculate offset for this group
            for (let i = 0; i < results.indexOf(group); i += 1) {
              globalIndexOffset += Math.min(results[i]?.count ?? 0, maxResultsPerPerspective);
            }

            return (
              <PerspectiveGroup
                key={group.perspective}
                group={group}
                query={query}
                perspectiveColor={perspectiveColor}
                selectedResultIndex={selectedResultIndex}
                globalIndexOffset={globalIndexOffset}
                maxResults={maxResultsPerPerspective}
                onSelect={handleSelectItem}
                onHighlight={onHighlight}
                onSelectResult={handleSelectResult}
              />
            );
          })}
        </div>
      ) : query ? (
        <div className='text-muted-foreground p-8 text-center'>
          <Search className='mx-auto mb-2 h-8 w-8 opacity-50' />
          <p className='text-sm'>No items found matching "{query}"</p>
          {searchHistory.length > 0 && (
            <div className='mt-4 space-y-2'>
              <p className='text-xs font-semibold'>Recent searches:</p>
              <div className='flex flex-wrap justify-center gap-2'>
                {searchHistory.map((historyQuery) => (
                  <Button
                    key={historyQuery}
                    variant='outline'
                    size='sm'
                    className='text-xs'
                    onClick={() => {
                      handleSearch(historyQuery);
                    }}
                  >
                    {historyQuery}
                  </Button>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className='text-muted-foreground space-y-4 p-8 text-center'>
          <Network className='mx-auto h-8 w-8 opacity-50' />
          <div>
            <p className='text-sm font-semibold'>Cross-Perspective Search</p>
            <p className='mt-1 text-xs'>
              Search across all {results.length || items.length} items in multiple perspectives
            </p>
          </div>
          {searchHistory.length > 0 && (
            <div className='space-y-2'>
              <p className='text-xs font-semibold'>Recent searches:</p>
              <div className='flex flex-wrap justify-center gap-2'>
                {searchHistory.map((historyQuery) => (
                  <Button
                    key={historyQuery}
                    variant='outline'
                    size='sm'
                    className='text-xs'
                    onClick={() => {
                      handleSearch(historyQuery);
                    }}
                  >
                    {historyQuery}
                  </Button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Footer with keyboard hints */}
      {query && results.length > 0 && (
        <div className='bg-muted/30 text-muted-foreground space-y-1 border-t px-4 py-2 text-[10px]'>
          <div className='flex items-center justify-between'>
            <span>
              <kbd className='bg-background rounded border px-1 text-[9px]'>↑↓</kbd>
              <span className='ml-1'>Navigate</span>
            </span>
            <span>
              <kbd className='bg-background rounded border px-1 text-[9px]'>Enter</kbd>
              <span className='ml-1'>Select</span>
            </span>
            <span>
              <kbd className='bg-background rounded border px-1 text-[9px]'>Esc</kbd>
              <span className='ml-1'>Clear</span>
            </span>
          </div>
        </div>
      )}
    </Card>
  );
}

export const CrossPerspectiveSearch = memo(CrossPerspectiveSearchComponent);
