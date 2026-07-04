import { Folder } from 'lucide-react';
import { memo, useCallback, useMemo } from 'react';

import { Button } from '@tracertm/ui';

interface ProjectsListEmptyStateProps {
  onClearSearch: () => void;
  searchQuery: string;
}

const EMPTY_STRING = '';

export const ProjectsListEmptyState = memo(function ProjectsListEmptyState({
  onClearSearch,
  searchQuery,
}: ProjectsListEmptyStateProps): JSX.Element {
  const showClearButton = useMemo<boolean>(() => searchQuery !== EMPTY_STRING, [searchQuery]);

  const handleClear = useCallback((): void => {
    onClearSearch();
  }, [onClearSearch]);

  let clearButton: JSX.Element | undefined = undefined;
  if (showClearButton) {
    clearButton = (
      <Button variant='link' onClick={handleClear} className='text-primary mt-2 font-bold'>
        Clear Filters
      </Button>
    );
  }

  return (
    <div className='text-muted-foreground/30 flex flex-col items-center justify-center py-32'>
      <Folder className='mb-6 h-20 w-20 opacity-10' />
      <p className='text-sm font-black tracking-[0.2em] uppercase'>Registry Vacant</p>
      {clearButton}
    </div>
  );
});
