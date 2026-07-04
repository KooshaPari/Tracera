import { Activity, Search } from 'lucide-react';
import { memo, useCallback, useMemo } from 'react';

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

type ProjectsListSortBy = 'date' | 'items' | 'name';
type ProjectsListSortOrder = 'asc' | 'desc';

interface ProjectsListFiltersBarProps {
  onSearchQueryChange: (value: string) => void;
  onSortByChange: (value: ProjectsListSortBy) => void;
  onSortOrderToggle: () => void;
  searchQuery: string;
  sortBy: ProjectsListSortBy;
  sortOrder: ProjectsListSortOrder;
}

const EMPTY_STRING = '';

const isSortBy = (value: string): value is ProjectsListSortBy =>
  value === 'date' || value === 'items' || value === 'name';

const ProjectsListFiltersBar = memo(function ProjectsListFiltersBar({
  onSearchQueryChange,
  onSortByChange,
  onSortOrderToggle,
  searchQuery,
  sortBy,
  sortOrder,
}: ProjectsListFiltersBarProps): JSX.Element {
  const sortIconClassName = useMemo<string>(() => {
    if (sortOrder === 'desc') {
      return cn('h-4 w-4 transition-transform', 'rotate-180');
    }
    return 'h-4 w-4 transition-transform';
  }, [sortOrder]);

  const handleSearchChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>): void => {
      onSearchQueryChange(event.target.value);
    },
    [onSearchQueryChange],
  );

  const handleSortByChange = useCallback(
    (value: string): void => {
      if (value === EMPTY_STRING) {
        return;
      }
      if (!isSortBy(value)) {
        return;
      }
      onSortByChange(value);
    },
    [onSortByChange],
  );

  return (
    <Card className='bg-muted/30 flex flex-wrap items-center gap-2 rounded-2xl border-none p-2'>
      <div className='relative min-w-[200px] flex-1'>
        <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
        <Input
          placeholder='Filter registries...'
          className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
          value={searchQuery}
          onChange={handleSearchChange}
        />
      </div>
      <div className='bg-border/50 mx-2 hidden h-6 w-px md:block' />
      <Select value={sortBy} onValueChange={handleSortByChange}>
        <SelectTrigger className='hover:bg-background/50 h-10 w-[150px] border-none bg-transparent transition-colors'>
          <SelectValue placeholder='Sort Parameters' />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='date'>Sync Date</SelectItem>
          <SelectItem value='name'>Identifier</SelectItem>
          <SelectItem value='items'>Node Density</SelectItem>
        </SelectContent>
      </Select>
      <Button
        variant='ghost'
        size='icon'
        onClick={onSortOrderToggle}
        className='h-10 w-10 rounded-xl'
      >
        <Activity className={sortIconClassName} />
      </Button>
    </Card>
  );
});

export { ProjectsListFiltersBar, type ProjectsListSortBy, type ProjectsListSortOrder };
