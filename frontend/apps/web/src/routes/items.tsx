import { createFileRoute } from '@tanstack/react-router';
import { useMemo } from 'react';

import { useProjects } from '@/hooks/useProjects';
import { ItemsTableView } from '@/views/ItemsTableView';

const ItemsListView = () => {
  const { data: projects } = useProjects();
  const projectId = useMemo(() => {
    if (!projects || !Array.isArray(projects)) {
      return;
    }
    return projects[0]?.id;
  }, [projects]);

  return <ItemsTableView projectId={projectId} />;
};

export const Route = createFileRoute('/items')({
  component: ItemsListView,
});
