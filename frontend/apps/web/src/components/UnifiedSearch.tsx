import { Network, Search } from 'lucide-react';
import { useState } from 'react';

import type { Item, Link } from '@tracertm/types';

import { logger } from '@/lib/logger';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui/components/Tabs';

import { CrossPerspectiveSearch } from './graph/CrossPerspectiveSearch';
import { GraphSearch } from './graph/GraphSearch';

interface UnifiedSearchProps {
  items: Item[];
  links: Link[];
  onSelectItem: (itemId: string) => void;
  onHighlightItem: (itemId: string | null) => void;
  className?: string;
}

/**
 * Unified Search Component
 * Supports both single-perspective and cross-perspective search modes
 *
 * Features:
 * - Basic search: Filter items by name, description, type
 * - Cross-perspective: Search across perspectives with equivalence awareness
 * - Results grouped by perspective for cross-perspective mode
 * - Keyboard navigation and quick selection
 */
export function UnifiedSearch({
  items,
  links,
  onSelectItem,
  onHighlightItem,
  className,
}: UnifiedSearchProps) {
  const [searchMode, setSearchMode] = useState<'basic' | 'cross-perspective'>('basic');

  return (
    <div className={className}>
      <Tabs
        value={searchMode}
        onValueChange={(mode) => {
          setSearchMode(mode as typeof searchMode);
        }}
      >
        <TabsList className='grid w-full grid-cols-2'>
          <TabsTrigger value='basic' className='flex items-center gap-2'>
            <Search className='h-4 w-4' />
            Basic Search
          </TabsTrigger>
          <TabsTrigger value='cross-perspective' className='flex items-center gap-2'>
            <Network className='h-4 w-4' />
            Cross-Perspective
          </TabsTrigger>
        </TabsList>

        <TabsContent value='basic' className='space-y-4'>
          <div className='text-muted-foreground text-sm'>
            Search items by name, description, or type within current perspective
          </div>
          <GraphSearch
            items={items}
            onSearch={(query, results) => {
              logger.info(`Found ${results.length} results for "${query}"`);
            }}
            onHighlight={onHighlightItem}
          />
        </TabsContent>

        <TabsContent value='cross-perspective' className='space-y-4'>
          <div className='text-muted-foreground text-sm'>
            Search across perspectives to find equivalent concepts and related items
          </div>
          <CrossPerspectiveSearch
            items={items}
            links={links}
            onSelect={onSelectItem}
            onHighlight={onHighlightItem}
            maxResultsPerPerspective={10}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
