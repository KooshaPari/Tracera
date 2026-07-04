import { Filter, Plus, Search } from 'lucide-react';
import { useCallback } from 'react';

import type { Project } from '@tracertm/types';

import { cn } from '@/lib/utils';
import {
  Button,
  Card,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui';

import itemsTableConstants from './constants';
import itemsTableFormatters from './formatters';

interface ItemsTableLabels {
  title: string;
  description: string;
  emptyTitle: string;
  emptyDescription: string;
  createModalTitle?: string;
  createButtonLabel?: string;
  newButtonLabel?: string;
}

interface ItemsTableFiltersBarProps {
  items: unknown[];
  filteredCount: number;
  labels: ItemsTableLabels;
  projectId?: string | undefined;
  type?: string | undefined;
  projects: Project[];
  projectFilter: string | undefined;
  typeFilter: string | undefined;
  searchQuery: string;
  onSearchQueryChange: (next: string) => void;
  onProjectFilterChange: (value: string) => void;
  onTypeFilterChange: (value: string) => void;
  onRefresh: () => void;
  onCreate: () => void;
}

function ItemsTableFiltersBar({
  items,
  filteredCount,
  labels,
  projectId,
  type,
  projects,
  projectFilter,
  typeFilter,
  searchQuery,
  onSearchQueryChange,
  onProjectFilterChange,
  onTypeFilterChange,
  onRefresh,
  onCreate,
}: ItemsTableFiltersBarProps): JSX.Element {
  const handleSearchChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>): void => {
      onSearchQueryChange(event.target.value);
    },
    [onSearchQueryChange],
  );

  const projectSelectValue = itemsTableFormatters.createViewTypeValue(projectFilter);
  const typeSelectValue = itemsTableFormatters.createViewTypeValue(typeFilter);
  const createLabel = labels.newButtonLabel ?? itemsTableConstants.DEFAULT_NEW_LABEL;

  return (
    <div className='animate-in-fade-up mx-auto max-w-[1600px] space-y-6 px-4 py-6 pb-4 sm:space-y-8 sm:px-6 sm:py-8 sm:pb-6'>
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-2xl font-black tracking-tight uppercase'>{labels.title}</h1>
          <p className='text-muted-foreground text-sm font-medium'>{labels.description}</p>
        </div>
        <div className='flex items-center gap-2'>
          <Button variant='outline' size='sm' onClick={onRefresh} className='gap-2 rounded-xl'>
            Refresh
          </Button>
          <Button
            size='sm'
            onClick={onCreate}
            aria-label={createLabel}
            className='shadow-primary/20 min-h-[44px] gap-2 rounded-xl shadow-lg'
          >
            <Plus className='h-4 w-4' /> {createLabel}
          </Button>
        </div>
      </div>

      <Card className='bg-muted/30 flex flex-wrap items-center gap-2 rounded-2xl border-none p-2'>
        <div
          className={cn(
            'relative flex-1',
            `min-w-[${itemsTableConstants.SEARCH_INPUT_MIN_WIDTH}px]`,
          )}
        >
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <Input
            placeholder='Search identifiers...'
            className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
            value={searchQuery}
            onChange={handleSearchChange}
            aria-label='Search items by title or ID'
          />
          <Button
            variant='ghost'
            size='icon'
            aria-label='Search items'
            className='absolute top-1/2 right-2 h-8 w-8 -translate-y-1/2'
          >
            <Search className='h-4 w-4' />
          </Button>
        </div>
        <div className='bg-border/50 mx-2 hidden h-6 w-px md:block' />
        <div className='text-muted-foreground/60 hidden px-2 text-[10px] lg:block'>
          Showing {filteredCount} of {items.length} items
        </div>
        <div className='bg-border/50 mx-2 hidden h-6 w-px md:block' />
        <Button variant='ghost' size='sm' aria-label='Filter items' className='h-10 px-3'>
          <Filter className='h-4 w-4' />
        </Button>

        {projectId === undefined && (
          <Select value={projectSelectValue} onValueChange={onProjectFilterChange}>
            <SelectTrigger className='hover:bg-background/50 h-10 w-[180px] border-none bg-transparent transition-colors'>
              <div className='flex items-center gap-2'>
                <Filter className='text-muted-foreground h-3.5 w-3.5' />
                <SelectValue placeholder='All Projects' />
              </div>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={itemsTableConstants.FILTER_ALL}>Global Scope</SelectItem>
              {projects.map((project) => (
                <SelectItem key={project.id} value={project.id}>
                  {project.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}

        {type === undefined && (
          <Select value={typeSelectValue} onValueChange={onTypeFilterChange}>
            <SelectTrigger className='hover:bg-background/50 h-10 w-[140px] border-none bg-transparent transition-colors'>
              <SelectValue placeholder='All Types' />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={itemsTableConstants.FILTER_ALL}>Any Type</SelectItem>
              {itemsTableConstants.VIEW_TYPE_OPTIONS.map((option) => (
                <SelectItem key={option} value={option} className='capitalize'>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </Card>
    </div>
  );
}

export { ItemsTableFiltersBar };
export type { ItemsTableFiltersBarProps, ItemsTableLabels };
