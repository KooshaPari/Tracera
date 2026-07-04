// Graph Search Component
// Filter nodes by name/type, highlight matching nodes, show result count

import { ChevronDown, ChevronUp, Search, X } from 'lucide-react';
import { memo, useCallback, useMemo, useState } from 'react';

import type { Item } from '@tracertm/types';

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

/**
 * Search result item
 */
export interface SearchResult {
  item: Item;
  matchType: 'title' | 'description' | 'type';
  score: number;
}

type SearchFilter = 'all' | 'title' | 'description' | 'type';

interface GraphSearchProps {
  items: Item[];
  onSearch: (query: string, results: SearchResult[], filter: SearchFilter) => void;
  onHighlight: (itemId: string | null) => void;
  compact?: boolean;
  className?: string;
}

/**
 * Calculate search score based on relevance
 */
function calculateSearchScore(item: Item, query: string, filter: SearchFilter): number {
  const lowerQuery = query.toLowerCase();
  let score = 0;

  // Title match (highest priority)
  if ((filter === 'all' || filter === 'title') && item.title) {
    const titleLower = item.title.toLowerCase();
    if (titleLower === lowerQuery) {
      score += 100; // Exact match
    } else if (titleLower.startsWith(lowerQuery)) {
      score += 75; // Prefix match
    } else if (titleLower.includes(lowerQuery)) {
      score += 50; // Substring match
    }
  }

  // Description match
  if ((filter === 'all' || filter === 'description') && item.description) {
    const descLower = item.description.toLowerCase();
    if (descLower.includes(lowerQuery)) {
      score += 25;
    }
  }

  // Type match
  if ((filter === 'all' || filter === 'type') && item.type) {
    const typeLower = item.type.toLowerCase();
    if (typeLower === lowerQuery) {
      score += 50;
    } else if (typeLower.includes(lowerQuery)) {
      score += 25;
    }
  }

  return score;
}

/**
 * Perform search on items
 */
function performSearch(items: Item[], query: string, filter: SearchFilter): SearchResult[] {
  if (!query.trim()) {
    return [];
  }

  const results: SearchResult[] = [];

  for (const item of items) {
    const score = calculateSearchScore(item, query, filter);
    if (score > 0) {
      // Determine match type
      const lowerQuery = query.toLowerCase();
      let matchType: 'title' | 'description' | 'type' = 'title';

      if (item.title?.toLowerCase().includes(lowerQuery)) {
        matchType = 'title';
      } else if (item.description?.toLowerCase().includes(lowerQuery)) {
        matchType = 'description';
      } else if (item.type?.toLowerCase().includes(lowerQuery)) {
        matchType = 'type';
      }

      results.push({ item, matchType, score });
    }
  }

  // Sort by score (descending)
  results.sort((a, b) => b.score - a.score);

  return results;
}

/**
 * Get type color for result badges
 */
function getTypeColor(type?: string): string {
  const colors: Record<string, string> = {
    api: '#10b981',
    component: '#3b82f6',
    database: '#f59e0b',
    feature: '#ec4899',
    page: '#8b5cf6',
  };
  return colors[type?.toLowerCase() ?? ''] ?? '#64748b';
}

/**
 * Graph search component
 */
function GraphSearchComponent({
  items,
  onSearch,
  onHighlight,
  compact = false,
  className,
}: GraphSearchProps) {
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<SearchFilter>('all');
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedResultIndex, setSelectedResultIndex] = useState(0);

  const results = useMemo(() => performSearch(items, query, filter), [items, query, filter]);

  const handleSearch = useCallback(
    (newQuery: string) => {
      setQuery(newQuery);
      const newResults = performSearch(items, newQuery, filter);
      onSearch(newQuery, newResults, filter);
      setSelectedResultIndex(0);
    },
    [items, filter, onSearch],
  );

  const handleFilterChange = useCallback(
    (newFilter: SearchFilter) => {
      setFilter(newFilter);
      const newResults = performSearch(items, query, newFilter);
      onSearch(query, newResults, newFilter);
    },
    [items, query, onSearch],
  );

  const handleClear = useCallback(() => {
    setQuery('');
    onSearch('', [], 'all');
    setSelectedResultIndex(0);
  }, [onSearch]);

  const handleResultClick = useCallback(
    (itemId: string) => {
      onHighlight(itemId);
    },
    [onHighlight],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (results.length === 0) {
        return;
      }

      switch (e.key) {
        case 'ArrowDown': {
          e.preventDefault();
          setSelectedResultIndex((prev) => Math.min(prev + 1, results.length - 1));
          break;
        }
        case 'ArrowUp': {
          e.preventDefault();
          setSelectedResultIndex((prev) => Math.max(prev - 1, 0));
          break;
        }
        case 'Enter': {
          e.preventDefault();
          if (results[selectedResultIndex]) {
            handleResultClick(results[selectedResultIndex].item.id);
          }
          break;
        }
        case 'Escape': {
          e.preventDefault();
          handleClear();
          break;
        }
        default: {
          break;
        }
      }
    },
    [results, selectedResultIndex, handleResultClick, handleClear],
  );

  if (compact) {
    return (
      <div className={cn('relative', className)}>
        <div className='flex items-center gap-2'>
          <Search className='text-muted-foreground h-4 w-4' />
          <Input
            placeholder='Search items...'
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
          {results.length > 0 && (
            <Badge variant='secondary' className='text-xs'>
              {results.length}
            </Badge>
          )}
        </div>

        {/* Results dropdown */}
        {query && results.length > 0 && (
          <div className='bg-card absolute top-full right-0 left-0 z-50 mt-2 max-h-72 overflow-y-auto rounded-lg border shadow-lg'>
            {results.slice(0, 10).map((result, idx) => (
              <div
                key={result.item.id}
                className={cn(
                  'px-3 py-2 border-b last:border-b-0 cursor-pointer text-sm transition-colors',
                  idx === selectedResultIndex && 'bg-accent',
                )}
                onClick={() => {
                  handleResultClick(result.item.id);
                }}
                onMouseEnter={() => {
                  setSelectedResultIndex(idx);
                }}
              >
                <div className='flex items-center justify-between gap-2'>
                  <div className='min-w-0'>
                    <div className='truncate font-medium'>{result.item.title}</div>
                    {result.matchType !== 'title' && (
                      <div className='text-muted-foreground truncate text-xs'>
                        {result.matchType === 'type' ? result.item.type : result.item.description}
                      </div>
                    )}
                  </div>
                  <Badge variant='outline' className='shrink-0 text-[10px]'>
                    {result.matchType}
                  </Badge>
                </div>
              </div>
            ))}
            {results.length > 10 && (
              <div className='text-muted-foreground bg-muted/30 px-3 py-2 text-center text-xs'>
                +{results.length - 10} more results
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <Card className={cn('overflow-hidden', className)}>
      {/* Header */}
      <div className='border-b p-3'>
        <div className='flex items-center gap-2'>
          <Search className='text-muted-foreground h-4 w-4 shrink-0' />
          <Input
            placeholder='Search by title, description, or type...'
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

        {/* Filter */}
        {isExpanded && (
          <div className='mt-3'>
            <Select
              value={filter}
              onValueChange={(val) => {
                handleFilterChange(val as SearchFilter);
              }}
            >
              <SelectTrigger className='h-8 text-sm'>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='all'>All fields</SelectItem>
                <SelectItem value='title'>Title only</SelectItem>
                <SelectItem value='description'>Description</SelectItem>
                <SelectItem value='type'>Type</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}
      </div>

      {/* Results */}
      {results.length > 0 ? (
        <div className='max-h-96 overflow-y-auto'>
          {results.map((result, idx) => (
            <div
              key={result.item.id}
              className={cn(
                'px-4 py-3 border-b last:border-b-0 cursor-pointer transition-colors',
                idx === selectedResultIndex && 'bg-accent',
              )}
              onClick={() => {
                handleResultClick(result.item.id);
              }}
              onMouseEnter={() => {
                setSelectedResultIndex(idx);
              }}
            >
              <div className='flex items-start justify-between gap-2'>
                <div className='min-w-0 flex-1'>
                  <h4 className='truncate text-sm font-medium'>{result.item.title}</h4>
                  {result.item.description && (
                    <p className='text-muted-foreground mt-1 truncate text-xs'>
                      {result.item.description}
                    </p>
                  )}
                  <div className='mt-2 flex items-center gap-2'>
                    {result.item.type && (
                      <Badge
                        variant='outline'
                        className='text-[10px]'
                        style={{
                          backgroundColor: `${getTypeColor(result.item.type)}20`,
                          borderColor: `${getTypeColor(result.item.type)}40`,
                          color: getTypeColor(result.item.type),
                        }}
                      >
                        {result.item.type}
                      </Badge>
                    )}
                    <Badge variant='secondary' className='text-[10px]'>
                      {result.matchType}
                    </Badge>
                  </div>
                </div>
                <div className='text-muted-foreground text-xs whitespace-nowrap'>
                  Score: {result.score}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : query ? (
        <div className='text-muted-foreground p-8 text-center'>
          <Search className='mx-auto mb-2 h-8 w-8 opacity-50' />
          <p className='text-sm'>No items found matching &quot;{query}&quot;</p>
        </div>
      ) : (
        <div className='text-muted-foreground p-8 text-center'>
          <Search className='mx-auto mb-2 h-8 w-8 opacity-50' />
          <p className='text-sm'>Enter a search query to find items</p>
        </div>
      )}
    </Card>
  );
}

export const GraphSearch = memo(GraphSearchComponent);
