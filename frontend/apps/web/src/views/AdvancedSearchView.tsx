import { useQuery } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';
import React from 'react';

import { client } from '@/api/client';
import { CardErrorFallback } from '@/lib/lazy-loading';
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui/components/Tabs';

const { getAuthHeaders } = client;

type SearchTab = 'items' | 'projects' | 'links';

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

interface AdvancedSearchResultRow {
  description?: string;
  id: string;
  name?: string;
  project_id?: string;
  status?: string;
  title?: string;
  type: string;
  view?: string;
  view_type?: string;
}

interface AdvancedSearchResponse {
  filters: AdvancedFilters | null;
  project_id: string;
  query: string | null;
  results: AdvancedSearchResultRow[];
  total: number;
}

interface SelectOption {
  label: string;
  value: string;
}

interface SelectFilterFieldProps {
  id: string;
  label: string;
  options: SelectOption[];
  placeholder: string;
  value: string;
  onValueChange: (nextValue: string) => void;
}

interface DateFilterFieldProps {
  id: string;
  label: string;
  value: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

interface SearchResultsProps {
  query: string;
  results: AdvancedSearchResultRow[];
  total: number;
}

interface SearchFiltersCardProps {
  activeTab: SearchTab;
  filters: AdvancedFilters;
  query: string;
  onActiveTabChange: (nextTabValue: string) => void;
  onClearFilters: () => void;
  onCreatedAfterChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onCreatedBeforeChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onItemTypeChange: (nextValue: string) => void;
  onLinkTypeChange: (nextValue: string) => void;
  onPriorityChange: (nextValue: string) => void;
  onProjectChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onQueryChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onSearchClick: () => void;
  onStatusChange: (nextValue: string) => void;
  onViewChange: (nextValue: string) => void;
}

const FILTER_KEYS: (keyof AdvancedFilters)[] = [
  'view',
  'status',
  'project_id',
  'item_type',
  'owner',
  'priority',
  'created_after',
  'created_before',
  'updated_after',
  'updated_before',
];

const VIEW_OPTIONS: SelectOption[] = [
  { label: 'All Views', value: 'all' },
  { label: 'Feature', value: 'FEATURE' },
  { label: 'Requirement', value: 'REQUIREMENT' },
  { label: 'Test', value: 'TEST' },
  { label: 'Code', value: 'CODE' },
  { label: 'API', value: 'API' },
];

const STATUS_OPTIONS: SelectOption[] = [
  { label: 'All Statuses', value: 'all' },
  { label: 'To Do', value: 'todo' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Done', value: 'done' },
  { label: 'Blocked', value: 'blocked' },
];

const ITEM_TYPE_OPTIONS: SelectOption[] = [
  { label: 'All Types', value: 'all' },
  { label: 'Feature', value: 'feature' },
  { label: 'Requirement', value: 'requirement' },
  { label: 'Test', value: 'test' },
  { label: 'Bug', value: 'bug' },
];

const PRIORITY_OPTIONS: SelectOption[] = [
  { label: 'All Priorities', value: 'all' },
  { label: 'Low', value: 'low' },
  { label: 'Medium', value: 'medium' },
  { label: 'High', value: 'high' },
  { label: 'Critical', value: 'critical' },
];

const LINK_TYPE_OPTIONS: SelectOption[] = [
  { label: 'All Link Types', value: 'all' },
  { label: 'Implements', value: 'implements' },
  { label: 'Tests', value: 'tests' },
  { label: 'Depends On', value: 'depends_on' },
  { label: 'Blocks', value: 'blocks' },
];
const EMPTY_RESULTS: AdvancedSearchResultRow[] = [];

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;

const isSearchTab = (value: string): value is SearchTab =>
  value === 'items' || value === 'projects' || value === 'links';

const mapAdvancedFilters = (value: unknown): AdvancedFilters | null => {
  if (!isRecord(value)) {
    return null;
  }

  const mapped: AdvancedFilters = {};
  for (const key of FILTER_KEYS) {
    const rawValue = value[key];
    if (typeof rawValue === 'string' && rawValue.length > 0) {
      mapped[key] = rawValue;
    }
  }

  return Object.keys(mapped).length > 0 ? mapped : null;
};

const mapAdvancedSearchResult = (value: unknown): AdvancedSearchResultRow | null => {
  if (!isRecord(value)) {
    return null;
  }

  const id = value['id'];
  const type = value['type'];

  if (typeof id !== 'string' || typeof type !== 'string') {
    return null;
  }

  const mapped: AdvancedSearchResultRow = { id, type };

  if (typeof value['description'] === 'string') {
    mapped.description = value['description'];
  }
  if (typeof value['name'] === 'string') {
    mapped.name = value['name'];
  }
  if (typeof value['project_id'] === 'string') {
    mapped.project_id = value['project_id'];
  }
  if (typeof value['status'] === 'string') {
    mapped.status = value['status'];
  }
  if (typeof value['title'] === 'string') {
    mapped.title = value['title'];
  }
  if (typeof value['view'] === 'string') {
    mapped.view = value['view'];
  }
  if (typeof value['view_type'] === 'string') {
    mapped.view_type = value['view_type'];
  }

  return mapped;
};

const mapAdvancedSearchResponse = (value: unknown): AdvancedSearchResponse => {
  if (!isRecord(value)) {
    throw new Error('Invalid search response format');
  }

  const resultsRaw = Array.isArray(value['results']) ? value['results'] : [];
  const results = resultsRaw
    .map((entry) => mapAdvancedSearchResult(entry))
    .filter((entry): entry is AdvancedSearchResultRow => entry !== null);
  const total = typeof value['total'] === 'number' ? value['total'] : 0;

  return {
    filters: mapAdvancedFilters(value['filters']),
    project_id: typeof value['project_id'] === 'string' ? value['project_id'] : 'all',
    query: typeof value['query'] === 'string' ? value['query'] : null,
    results,
    total,
  };
};

const getResultRoute = (result: AdvancedSearchResultRow): string => {
  if (result.type === 'item') {
    if (typeof result.project_id === 'string') {
      const viewName = String(result.view ?? result.view_type ?? 'feature').toLowerCase();
      return `/projects/${result.project_id}/views/${viewName}/${result.id}`;
    }

    return '/projects';
  }

  if (result.type === 'project') {
    return `/projects/${result.id}`;
  }

  if (typeof result.project_id === 'string') {
    return `/projects/${result.project_id}/views/feature`;
  }

  return '/projects';
};

const SelectFilterField = ({
  id,
  label,
  options,
  placeholder,
  value,
  onValueChange,
}: SelectFilterFieldProps): JSX.Element => (
  <div>
    <label htmlFor={id} className='mb-2 block text-sm font-medium'>
      {label}
    </label>
    <Select value={value} onValueChange={onValueChange}>
      <SelectTrigger id={id} className='mt-2'>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {options.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  </div>
);

const DateFilterField = ({ id, label, value, onChange }: DateFilterFieldProps): JSX.Element => (
  <div>
    <label htmlFor={id} className='mb-2 block text-sm font-medium'>
      {label}
    </label>
    <Input id={id} type='date' value={value} onChange={onChange} className='mt-2' />
  </div>
);

const LoadingState = (): JSX.Element => (
  <Card className='p-4 text-sm text-gray-600'>Loading...</Card>
);

const SearchResults = ({ query, results, total }: SearchResultsProps): JSX.Element => {
  if (results.length === 0) {
    return (
      <Card className='p-12 text-center text-gray-500'>
        <p>No results found</p>
        {query.length > 0 && <p className='mt-2 text-sm'>Try adjusting your filters</p>}
      </Card>
    );
  }

  return (
    <div>
      <div className='mb-4 flex items-center justify-between'>
        <h2 className='text-xl font-semibold'>Results ({total})</h2>
      </div>

      <div className='space-y-3'>
        {results.map((result) => {
          const hasStatus = typeof result.status === 'string' && result.status.length > 0;
          const hasDescription =
            typeof result.description === 'string' && result.description.length > 0;
          const hasProjectId =
            typeof result.project_id === 'string' && result.project_id.length > 0;

          return (
            <Link key={result.id} to={getResultRoute(result)}>
              <Card className='p-4 transition-shadow hover:shadow-md'>
                <div className='flex items-start gap-3'>
                  <div className='flex-1'>
                    <div className='mb-1 flex items-center gap-2'>
                      <h3 className='font-medium'>{result.title ?? result.name}</h3>
                      <span className='rounded bg-gray-100 px-2 py-0.5 text-xs'>{result.type}</span>
                      {hasStatus && (
                        <span className='rounded border px-2 py-0.5 text-xs'>{result.status}</span>
                      )}
                    </div>
                    {hasDescription && (
                      <p className='line-clamp-2 text-sm text-gray-600'>{result.description}</p>
                    )}
                    {hasProjectId && (
                      <p className='mt-1 text-xs text-gray-500'>Project: {result.project_id}</p>
                    )}
                  </div>
                </div>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
};

const SearchFiltersCard = ({
  activeTab,
  filters,
  query,
  onActiveTabChange,
  onClearFilters,
  onCreatedAfterChange,
  onCreatedBeforeChange,
  onItemTypeChange,
  onLinkTypeChange,
  onPriorityChange,
  onProjectChange,
  onQueryChange,
  onSearchClick,
  onStatusChange,
  onViewChange,
}: SearchFiltersCardProps): JSX.Element => (
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
          onChange={onQueryChange}
          className='mt-2'
        />
      </div>

      <Tabs value={activeTab} onValueChange={onActiveTabChange}>
        <TabsList>
          <TabsTrigger value='items'>Items</TabsTrigger>
          <TabsTrigger value='projects'>Projects</TabsTrigger>
          <TabsTrigger value='links'>Links</TabsTrigger>
        </TabsList>

        <TabsContent value='items' className='mt-4 space-y-4'>
          <div className='grid grid-cols-2 gap-4'>
            <SelectFilterField
              id='view-filter'
              label='View'
              options={VIEW_OPTIONS}
              placeholder='All Views'
              value={filters.view ?? 'all'}
              onValueChange={onViewChange}
            />
            <SelectFilterField
              id='status-filter'
              label='Status'
              options={STATUS_OPTIONS}
              placeholder='All Statuses'
              value={filters.status ?? 'all'}
              onValueChange={onStatusChange}
            />
            <SelectFilterField
              id='type-filter'
              label='Item Type'
              options={ITEM_TYPE_OPTIONS}
              placeholder='All Types'
              value={filters.item_type ?? 'all'}
              onValueChange={onItemTypeChange}
            />
            <SelectFilterField
              id='priority-filter'
              label='Priority'
              options={PRIORITY_OPTIONS}
              placeholder='All Priorities'
              value={filters.priority ?? 'all'}
              onValueChange={onPriorityChange}
            />
          </div>

          <div className='grid grid-cols-2 gap-4'>
            <DateFilterField
              id='created-after'
              label='Created After'
              value={filters.created_after ?? ''}
              onChange={onCreatedAfterChange}
            />
            <DateFilterField
              id='created-before'
              label='Created Before'
              value={filters.created_before ?? ''}
              onChange={onCreatedBeforeChange}
            />
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
              value={filters.project_id ?? ''}
              onChange={onProjectChange}
              className='mt-2'
            />
          </div>
        </TabsContent>

        <TabsContent value='links' className='mt-4 space-y-4'>
          <SelectFilterField
            id='link-type-filter'
            label='Link Type'
            options={LINK_TYPE_OPTIONS}
            placeholder='All Link Types'
            value={filters.view ?? 'all'}
            onValueChange={onLinkTypeChange}
          />
        </TabsContent>
      </Tabs>

      <div className='flex gap-2'>
        <Button onClick={onSearchClick}>Search</Button>
        <Button variant='outline' onClick={onClearFilters}>
          Clear Filters
        </Button>
      </div>
    </div>
  </Card>
);

export function AdvancedSearchView(): JSX.Element {
  const [query, setQuery] = React.useState('');
  const [filters, setFilters] = React.useState<AdvancedFilters>({});
  const [activeTab, setActiveTab] = React.useState<SearchTab>('items');

  const hasQuery = query.trim().length > 0;
  const hasFilters = Object.keys(filters).length > 0;

  const searchQuery = useQuery({
    enabled: hasQuery || hasFilters,
    queryFn: async (): Promise<AdvancedSearchResponse | null> => {
      if (!hasQuery && !hasFilters) {
        return null;
      }

      const response = await fetch(
        `/api/v1/projects/${filters.project_id ?? 'all'}/search/advanced`,
        {
          body: JSON.stringify({
            filters,
            query: query.length > 0 ? query : undefined,
          }),
          headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
          method: 'POST',
        },
      );

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const payload = (await response.json()) as unknown;
      return mapAdvancedSearchResponse(payload);
    },
    queryKey: ['advanced-search', query, filters, activeTab],
  });

  const { data, error, isError, isLoading, refetch } = searchQuery;

  const handleFilterChange = React.useCallback(
    (key: keyof AdvancedFilters, value: string): void => {
      setFilters((previousFilters) => {
        if (value === 'all' || value.length === 0) {
          const { [key]: _removedFilter, ...remainingFilters } = previousFilters;
          return remainingFilters;
        }

        return {
          ...previousFilters,
          [key]: value,
        };
      });
    },
    [],
  );

  const clearFilters = React.useCallback((): void => {
    setFilters({});
    setQuery('');
  }, []);

  const handleSearchClick = React.useCallback((): void => {
    refetch().catch(() => null);
  }, [refetch]);

  const handleRetry = React.useCallback((): void => {
    refetch().catch(() => null);
  }, [refetch]);

  const handleQueryChange = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>): void => {
      setQuery(event.target.value);
    },
    [],
  );

  const handleActiveTabChange = React.useCallback((nextTabValue: string): void => {
    if (isSearchTab(nextTabValue)) {
      setActiveTab(nextTabValue);
    }
  }, []);

  const handleViewChange = React.useCallback(
    (nextValue: string): void => {
      handleFilterChange('view', nextValue);
    },
    [handleFilterChange],
  );

  const handleStatusChange = React.useCallback(
    (nextValue: string): void => {
      handleFilterChange('status', nextValue);
    },
    [handleFilterChange],
  );

  const handleItemTypeChange = React.useCallback(
    (nextValue: string): void => {
      handleFilterChange('item_type', nextValue);
    },
    [handleFilterChange],
  );

  const handlePriorityChange = React.useCallback(
    (nextValue: string): void => {
      handleFilterChange('priority', nextValue);
    },
    [handleFilterChange],
  );

  const handleCreatedAfterChange = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>): void => {
      handleFilterChange('created_after', event.target.value);
    },
    [handleFilterChange],
  );

  const handleCreatedBeforeChange = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>): void => {
      handleFilterChange('created_before', event.target.value);
    },
    [handleFilterChange],
  );

  const handleProjectChange = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>): void => {
      handleFilterChange('project_id', event.target.value);
    },
    [handleFilterChange],
  );

  const handleLinkTypeChange = React.useCallback(
    (nextValue: string): void => {
      handleFilterChange('view', nextValue);
    },
    [handleFilterChange],
  );

  const results = data?.results ?? EMPTY_RESULTS;

  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-3xl font-bold'>Advanced Search</h1>
        <p className='text-gray-600'>Search with advanced filters across all projects</p>
      </div>

      <SearchFiltersCard
        activeTab={activeTab}
        filters={filters}
        query={query}
        onActiveTabChange={handleActiveTabChange}
        onClearFilters={clearFilters}
        onCreatedAfterChange={handleCreatedAfterChange}
        onCreatedBeforeChange={handleCreatedBeforeChange}
        onItemTypeChange={handleItemTypeChange}
        onLinkTypeChange={handleLinkTypeChange}
        onPriorityChange={handlePriorityChange}
        onProjectChange={handleProjectChange}
        onQueryChange={handleQueryChange}
        onSearchClick={handleSearchClick}
        onStatusChange={handleStatusChange}
        onViewChange={handleViewChange}
      />

      {isLoading && <LoadingState />}

      {data && <SearchResults query={query} results={results} total={data.total} />}

      {isError && (
        <Card className='overflow-hidden p-0'>
          <CardErrorFallback
            title='Search failed'
            message={error?.message ?? 'Error performing search. Please try again.'}
            error={error ?? undefined}
            retry={handleRetry}
            className='rounded-none border-0 p-6'
          />
        </Card>
      )}
    </div>
  );
}
