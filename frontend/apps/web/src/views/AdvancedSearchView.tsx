import { useQuery } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';
import { useState } from 'react';

/* eslint-disable complexity, func-style, max-lines-per-function, react/jsx-max-depth, react-perf/jsx-no-new-function-as-prop, unicorn/no-nested-ternary */
import { client } from '@/api/client';
import { CardErrorFallback } from '@/lib/lazy-loading';
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
import { Skeleton } from '@tracertm/ui/components/Skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui/components/Tabs';

import type { SearchResult } from '../api/types';

const { getAuthHeaders } = client;

interface AdvancedFilters {
  view?: string;
  status?: string;
  project_id?: string;
  item_type?: string;
  owner?: string;
  priority?: string;
  created_after?: string;
  created_before?: string;
  updated_after?: string;
  updated_before?: string;
}

export function AdvancedSearchView() {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<AdvancedFilters>({});
  const [activeTab, setActiveTab] = useState<'items' | 'projects' | 'links'>('items');

  const searchQuery = useQuery({
    enabled: query.trim().length > 0 || Object.keys(filters).length > 0,
    queryFn: async () => {
      if (!query.trim() && Object.keys(filters).length === 0) {
        return null;
      }

      // Use the advanced search endpoint we created
      const response = await fetch(
        `/api/v1/projects/${filters.project_id || 'all'}/search/advanced`,
        {
          body: JSON.stringify({
            filters: filters,
            query: query || undefined,
          }),
          headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
          method: 'POST',
        },
      );

      if (!response.ok) {
        throw new Error('Search failed');
      }

      return response.json() as Promise<{
        project_id: string;
        query: string | null;
        filters: AdvancedFilters | null;
        results: SearchResult[];
        total: number;
      }>;
    },
    queryKey: ['advanced-search', query, filters, activeTab],
  });

  const handleFilterChange = (key: keyof AdvancedFilters, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value === 'all' ? undefined : value || undefined,
    }));
  };

  const clearFilters = () => {
    setFilters({});
    setQuery('');
  };

  const results = searchQuery.data?.results || [];
  const { isLoading } = searchQuery;

  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-3xl font-bold'>Advanced Search</h1>
        <p className='text-gray-600'>Search with advanced filters across all projects</p>
      </div>

      <Card className='p-6'>
        <div className='space-y-4'>
          <div>
            <label htmlFor='search-query' className='mb-2 block text-sm font-medium'>
              Search Query
            </label>
            <Input
              id='search-query'
              type='search'
              placeholder='Enter search terms...'
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className='mt-2'
            />
          </div>

          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as typeof activeTab)}>
            <TabsList>
              <TabsTrigger value='items'>Items</TabsTrigger>
              <TabsTrigger value='projects'>Projects</TabsTrigger>
              <TabsTrigger value='links'>Links</TabsTrigger>
            </TabsList>

            <TabsContent value='items' className='mt-4 space-y-4'>
              <div className='grid grid-cols-2 gap-4'>
                <div>
                  <label htmlFor='view-filter' className='mb-2 block text-sm font-medium'>
                    View
                  </label>
                  <Select
                    value={filters.view || 'all'}
                    onValueChange={(v) => handleFilterChange('view', v)}
                  >
                    <SelectTrigger id='view-filter' className='mt-2'>
                      <SelectValue placeholder='All Views' />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value='all'>All Views</SelectItem>
                      <SelectItem value='FEATURE'>Feature</SelectItem>
                      <SelectItem value='REQUIREMENT'>Requirement</SelectItem>
                      <SelectItem value='TEST'>Test</SelectItem>
                      <SelectItem value='CODE'>Code</SelectItem>
                      <SelectItem value='API'>API</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label htmlFor='status-filter' className='mb-2 block text-sm font-medium'>
                    Status
                  </label>
                  <Select
                    value={filters.status || 'all'}
                    onValueChange={(v) => handleFilterChange('status', v)}
                  >
                    <SelectTrigger id='status-filter' className='mt-2'>
                      <SelectValue placeholder='All Statuses' />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value='all'>All Statuses</SelectItem>
                      <SelectItem value='todo'>To Do</SelectItem>
                      <SelectItem value='in_progress'>In Progress</SelectItem>
                      <SelectItem value='done'>Done</SelectItem>
                      <SelectItem value='blocked'>Blocked</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label htmlFor='type-filter' className='mb-2 block text-sm font-medium'>
                    Item Type
                  </label>
                  <Select
                    value={filters.item_type || 'all'}
                    onValueChange={(v) => handleFilterChange('item_type', v)}
                  >
                    <SelectTrigger id='type-filter' className='mt-2'>
                      <SelectValue placeholder='All Types' />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value='all'>All Types</SelectItem>
                      <SelectItem value='feature'>Feature</SelectItem>
                      <SelectItem value='requirement'>Requirement</SelectItem>
                      <SelectItem value='test'>Test</SelectItem>
                      <SelectItem value='bug'>Bug</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label htmlFor='priority-filter' className='mb-2 block text-sm font-medium'>
                    Priority
                  </label>
                  <Select
                    value={filters.priority || 'all'}
                    onValueChange={(v) => handleFilterChange('priority', v)}
                  >
                    <SelectTrigger id='priority-filter' className='mt-2'>
                      <SelectValue placeholder='All Priorities' />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value='all'>All Priorities</SelectItem>
                      <SelectItem value='low'>Low</SelectItem>
                      <SelectItem value='medium'>Medium</SelectItem>
                      <SelectItem value='high'>High</SelectItem>
                      <SelectItem value='critical'>Critical</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className='grid grid-cols-2 gap-4'>
                <div>
                  <label htmlFor='created-after' className='mb-2 block text-sm font-medium'>
                    Created After
                  </label>
                  <Input
                    id='created-after'
                    type='date'
                    value={filters.created_after || ''}
                    onChange={(e) => handleFilterChange('created_after', e.target.value)}
                    className='mt-2'
                  />
                </div>

                <div>
                  <label htmlFor='created-before' className='mb-2 block text-sm font-medium'>
                    Created Before
                  </label>
                  <Input
                    id='created-before'
                    type='date'
                    value={filters.created_before || ''}
                    onChange={(e) => handleFilterChange('created_before', e.target.value)}
                    className='mt-2'
                  />
                </div>
              </div>
            </TabsContent>

            <TabsContent value='projects' className='mt-4 space-y-4'>
              <div>
                <label htmlFor='project-filter' className='mb-2 block text-sm font-medium'>
                  Project
                </label>
                <Input
                  id='project-filter'
                  placeholder='Project ID or name...'
                  value={filters.project_id || ''}
                  onChange={(e) => handleFilterChange('project_id', e.target.value)}
                  className='mt-2'
                />
              </div>
            </TabsContent>

            <TabsContent value='links' className='mt-4 space-y-4'>
              <div>
                <label htmlFor='link-type-filter' className='mb-2 block text-sm font-medium'>
                  Link Type
                </label>
                <Select
                  value={filters.view || 'all'}
                  onValueChange={(v) => handleFilterChange('view', v)}
                >
                  <SelectTrigger id='link-type-filter' className='mt-2'>
                    <SelectValue placeholder='All Link Types' />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value='all'>All Link Types</SelectItem>
                    <SelectItem value='implements'>Implements</SelectItem>
                    <SelectItem value='tests'>Tests</SelectItem>
                    <SelectItem value='depends_on'>Depends On</SelectItem>
                    <SelectItem value='blocks'>Blocks</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>
          </Tabs>

          <div className='flex gap-2'>
            <Button onClick={() => searchQuery.refetch()}>Search</Button>
            <Button variant='outline' onClick={clearFilters}>
              Clear Filters
            </Button>
          </div>
        </div>
      </Card>

      {isLoading && (
        <div className='space-y-3'>
          <Skeleton className='h-20' />
          <Skeleton className='h-20' />
          <Skeleton className='h-20' />
        </div>
      )}

      {searchQuery.data && (
        <div>
          <div className='mb-4 flex items-center justify-between'>
            <h2 className='text-xl font-semibold'>Results ({searchQuery.data.total})</h2>
          </div>

          {results.length > 0 ? (
            <div className='space-y-3'>
              {results.map((result: any) => (
                <Link
                  key={result.id}
                  to={
                    result.type === 'item'
                      ? result.project_id
                        ? `/projects/${result.project_id}/views/${String(result.view || result.view_type || 'feature').toLowerCase()}/${result.id}`
                        : '/projects'
                      : result.type === 'project'
                        ? `/projects/${result.id}`
                        : result.project_id
                          ? `/projects/${result.project_id}/views/feature`
                          : '/projects'
                  }
                >
                  <Card className='p-4 transition-shadow hover:shadow-md'>
                    <div className='flex items-start gap-3'>
                      <div className='flex-1'>
                        <div className='mb-1 flex items-center gap-2'>
                          <h3 className='font-medium'>{result.title || result.name}</h3>
                          <Badge variant='secondary'>{result.type}</Badge>
                          {result.status && <Badge variant='outline'>{result.status}</Badge>}
                        </div>
                        {result.description && (
                          <p className='line-clamp-2 text-sm text-gray-600'>{result.description}</p>
                        )}
                        {result.project_id && (
                          <p className='mt-1 text-xs text-gray-500'>Project: {result.project_id}</p>
                        )}
                      </div>
                    </div>
                  </Card>
                </Link>
              ))}
            </div>
          ) : (
            <Card className='p-12 text-center text-gray-500'>
              <p>No results found</p>
              {query && <p className='mt-2 text-sm'>Try adjusting your filters</p>}
            </Card>
          )}
        </div>
      )}

      {searchQuery.isError && (
        <Card className='overflow-hidden p-0'>
          <CardErrorFallback
            title='Search failed'
            message={searchQuery.error?.message ?? 'Error performing search. Please try again.'}
            error={searchQuery.error ?? undefined}
            retry={() => searchQuery.refetch()}
            className='rounded-none border-0 p-6'
          />
        </Card>
      )}
    </div>
  );
}
