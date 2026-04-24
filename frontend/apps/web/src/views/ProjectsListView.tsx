import { useSearch } from '@tanstack/react-router';
import { useCallback, useMemo, useState } from 'react';

import type {
  ProjectsListSortBy,
  ProjectsListSortOrder,
} from '@/views/projects-list/ProjectsListFiltersBar';
import type { Project } from '@tracertm/types';

import { useProjects } from '@/hooks/useProjects';
import { CreateProjectDialog } from '@/views/projects-list/CreateProjectDialog';
import { EditProjectDialog } from '@/views/projects-list/EditProjectDialog';
import { ExportDialog } from '@/views/projects-list/ExportDialog';
import { ImportDialog } from '@/views/projects-list/ImportDialog';
import { ProjectCard } from '@/views/projects-list/ProjectCard';
import { ProjectsListEmptyState } from '@/views/projects-list/ProjectsListEmptyState';
import { ProjectsListFiltersBar } from '@/views/projects-list/ProjectsListFiltersBar';
import { ProjectsListHeader } from '@/views/projects-list/ProjectsListHeader';
import { ProjectsListLoadingState } from '@/views/projects-list/ProjectsListLoadingState';

interface ProjectsListEntry {
  itemCount: number;
  project: Project;
}

const EMPTY_STRING = '';
const SEARCH_ACTION_KEY = 'action';
const SEARCH_ACTION_CREATE = 'create';
const DEFAULT_ITEM_COUNT = 0;
const SORT_MULTIPLIER_ASC = 1;
const SORT_MULTIPLIER_DESC = -1;
const EPOCH_TIME = 0;

const isSearchParams = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;

const getSearchAction = (search: unknown): string | undefined => {
  if (!isSearchParams(search)) {
    return undefined;
  }
  const value = search[SEARCH_ACTION_KEY];
  if (typeof value === 'string') {
    return value;
  }
  return undefined;
};

const getInitialShowCreateDialog = (action: string | undefined): boolean =>
  action === SEARCH_ACTION_CREATE;

const getProjectCreatedAtTime = (createdAt: string | undefined): number => {
  if (typeof createdAt !== 'string' || createdAt.length === 0) {
    return EPOCH_TIME;
  }
  return new Date(createdAt).getTime();
};

const buildEntries = (projects: Project[]): ProjectsListEntry[] =>
  projects.map((project) => ({ itemCount: DEFAULT_ITEM_COUNT, project }));

const compareEntries = (
  first: ProjectsListEntry,
  second: ProjectsListEntry,
  sortBy: ProjectsListSortBy,
  sortOrder: ProjectsListSortOrder,
): number => {
  let comp = 0;
  if (sortBy === 'name') {
    const firstName = first.project.name ?? EMPTY_STRING;
    const secondName = second.project.name ?? EMPTY_STRING;
    comp = firstName.localeCompare(secondName);
  } else if (sortBy === 'date') {
    comp =
      getProjectCreatedAtTime(first.project.createdAt) -
      getProjectCreatedAtTime(second.project.createdAt);
  } else {
    comp = first.itemCount - second.itemCount;
  }

  if (sortOrder === 'asc') {
    return comp * SORT_MULTIPLIER_ASC;
  }
  return comp * SORT_MULTIPLIER_DESC;
};

const toggleSortOrder = (value: ProjectsListSortOrder): ProjectsListSortOrder => {
  if (value === 'asc') {
    return 'desc';
  }
  return 'asc';
};

interface ProjectsListData {
  projectsArray: Project[];
  projectsLoading: boolean;
}

function useProjectsListData(): ProjectsListData {
  const { data: projects, isLoading: projectsLoading } = useProjects();
  const projectsArray = useMemo<Project[]>((): Project[] => {
    if (Array.isArray(projects)) {
      return projects;
    }
    return [];
  }, [projects]);

  return { projectsArray, projectsLoading };
}

function useInitialCreateDialogOpen(): boolean {
  const searchParams = useSearch({ strict: false }) as unknown;
  const action = useMemo<string | undefined>(() => getSearchAction(searchParams), [searchParams]);
  return useMemo<boolean>(() => getInitialShowCreateDialog(action), [action]);
}

function useFilteredAndSortedProjects({
  projectsArray,
  searchQuery,
  sortBy,
  sortOrder,
}: {
  projectsArray: Project[];
  searchQuery: string;
  sortBy: ProjectsListSortBy;
  sortOrder: ProjectsListSortOrder;
}): ProjectsListEntry[] {
  return useMemo<ProjectsListEntry[]>((): ProjectsListEntry[] => {
    const query = searchQuery.trim().toLowerCase();
    const entries = buildEntries(projectsArray);

    const filtered: ProjectsListEntry[] = [];
    for (const entry of entries) {
      const displayName = entry.project.name ?? EMPTY_STRING;
      if (query === EMPTY_STRING || displayName.toLowerCase().includes(query)) {
        filtered.push(entry);
      }
    }

    const sorted = [...filtered];
    sorted.sort((first, second) => compareEntries(first, second, sortBy, sortOrder));
    return sorted;
  }, [projectsArray, searchQuery, sortBy, sortOrder]);
}

interface ProjectsListViewModel {
  editingProject: Project | undefined;
  filteredAndSorted: ProjectsListEntry[];
  handleClearSearch: () => void;
  handleCreateDialogOpenChange: (open: boolean) => void;
  handleCreated: (project: Project) => void;
  handleEditDialogOpenChange: (open: boolean) => void;
  handleEditProject: (project: Project) => void;
  handleSearchQueryChange: (value: string) => void;
  handleSortByChange: (value: ProjectsListSortBy) => void;
  handleSortOrderToggle: () => void;
  openCreateDialog: () => void;
  openExportDialog: () => void;
  openImportDialog: () => void;
  projectsArray: Project[];
  projectsLoading: boolean;
  searchQuery: string;
  showCreateDialog: boolean;
  showExportDialog: boolean;
  showImportDialog: boolean;
  sortBy: ProjectsListSortBy;
  sortOrder: ProjectsListSortOrder;
  setShowExportDialog: React.Dispatch<React.SetStateAction<boolean>>;
  setShowImportDialog: React.Dispatch<React.SetStateAction<boolean>>;
}

function useProjectsListViewModel(): ProjectsListViewModel {
  const initialShowCreateDialog = useInitialCreateDialogOpen();
  const { projectsArray, projectsLoading } = useProjectsListData();

  const [searchQuery, setSearchQuery] = useState(EMPTY_STRING);
  const [sortBy, setSortBy] = useState<ProjectsListSortBy>('date');
  const [sortOrder, setSortOrder] = useState<ProjectsListSortOrder>('desc');
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState<boolean>(initialShowCreateDialog);
  const [editingProject, setEditingProject] = useState<Project | undefined>();

  const filteredAndSorted = useFilteredAndSortedProjects({
    projectsArray,
    searchQuery,
    sortBy,
    sortOrder,
  });

  const openCreateDialog = useCallback((): void => {
    setShowCreateDialog(true);
  }, []);

  const handleCreateDialogOpenChange = useCallback((open: boolean): void => {
    setShowCreateDialog(open);
  }, []);

  const handleCreated = useCallback((project: Project): void => {
    globalThis.location.assign(`/projects/${project.id}/views/integrations`);
  }, []);

  const openExportDialog = useCallback((): void => {
    setShowExportDialog(true);
  }, []);

  const openImportDialog = useCallback((): void => {
    setShowImportDialog(true);
  }, []);

  const handleSearchQueryChange = useCallback((value: string): void => {
    setSearchQuery(value);
  }, []);

  const handleSortByChange = useCallback((value: ProjectsListSortBy): void => {
    setSortBy(value);
  }, []);

  const handleSortOrderToggle = useCallback((): void => {
    setSortOrder(toggleSortOrder);
  }, []);

  const handleClearSearch = useCallback((): void => {
    setSearchQuery(EMPTY_STRING);
  }, []);

  const handleEditProject = useCallback((project: Project): void => {
    setEditingProject(project);
  }, []);

  const handleEditDialogOpenChange = useCallback((open: boolean): void => {
    if (open) {
      return;
    }
    setEditingProject(undefined);
  }, []);

  return {
    editingProject,
    filteredAndSorted,
    handleClearSearch,
    handleCreateDialogOpenChange,
    handleCreated,
    handleEditDialogOpenChange,
    handleEditProject,
    handleSearchQueryChange,
    handleSortByChange,
    handleSortOrderToggle,
    openCreateDialog,
    openExportDialog,
    openImportDialog,
    projectsArray,
    projectsLoading,
    searchQuery,
    showCreateDialog,
    showExportDialog,
    showImportDialog,
    sortBy,
    sortOrder,
    setShowExportDialog,
    setShowImportDialog,
  };
}

function ProjectsListView(): JSX.Element {
  const model = useProjectsListViewModel();
  return renderProjectsListView(model);
}

function renderProjectsListContent({
  filteredAndSorted,
  handleClearSearch,
  handleEditProject,
  searchQuery,
}: Pick<
  ProjectsListViewModel,
  'filteredAndSorted' | 'handleClearSearch' | 'handleEditProject' | 'searchQuery'
>): JSX.Element {
  if (filteredAndSorted.length === 0) {
    return <ProjectsListEmptyState searchQuery={searchQuery} onClearSearch={handleClearSearch} />;
  }

  return (
    <div className='stagger-children grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'>
      {filteredAndSorted.map(({ project, itemCount }) => (
        <ProjectCard
          key={project.id}
          project={project}
          itemCount={itemCount}
          onEdit={handleEditProject}
        />
      ))}
    </div>
  );
}

function renderProjectsListView(model: ProjectsListViewModel): JSX.Element {
  const {
    editingProject,
    filteredAndSorted,
    handleClearSearch,
    handleCreateDialogOpenChange,
    handleCreated,
    handleEditDialogOpenChange,
    handleEditProject,
    handleSearchQueryChange,
    handleSortByChange,
    handleSortOrderToggle,
    openCreateDialog,
    openExportDialog,
    openImportDialog,
    projectsArray,
    projectsLoading,
    searchQuery,
    showCreateDialog,
    showExportDialog,
    showImportDialog,
    sortBy,
    sortOrder,
    setShowExportDialog,
    setShowImportDialog,
  } = model;
  if (projectsLoading) {
    return <ProjectsListLoadingState />;
  }

  const content = renderProjectsListContent({
    filteredAndSorted,
    handleClearSearch,
    handleEditProject,
    searchQuery,
  });

  return (
    <div className='animate-in-fade-up mx-auto max-w-[1600px] space-y-8 p-6'>
      <ProjectsListHeader
        onCreate={openCreateDialog}
        onExport={openExportDialog}
        onImport={openImportDialog}
      />

      <ProjectsListFiltersBar
        searchQuery={searchQuery}
        onSearchQueryChange={handleSearchQueryChange}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortByChange={handleSortByChange}
        onSortOrderToggle={handleSortOrderToggle}
      />

      {content}

      <CreateProjectDialog
        open={showCreateDialog}
        onOpenChange={handleCreateDialogOpenChange}
        onCreated={handleCreated}
      />

      <EditProjectDialog
        project={editingProject}
        open={editingProject !== undefined}
        onOpenChange={handleEditDialogOpenChange}
      />

      <ExportDialog
        open={showExportDialog}
        onOpenChange={setShowExportDialog}
        projects={projectsArray}
      />
      <ImportDialog
        open={showImportDialog}
        onOpenChange={setShowImportDialog}
        projects={projectsArray}
      />
    </div>
  );
}

export { ProjectsListView };
