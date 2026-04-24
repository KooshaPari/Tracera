import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

import type { Project } from '@tracertm/types';

const RECENT_PROJECTS_LIMIT = Number('10');

// SSR-safe storage that only accesses localStorage on the client
const noopStorage = {
  getItem: (_key: string) => null,
  removeItem: (_key: string) => {},
  setItem: (_key: string, _value: string) => {},
};

const getStorage = () => {
  // Check if we're in a browser environment with proper localStorage
  if (
    typeof globalThis.window === 'undefined' ||
    typeof localStorage === 'undefined' ||
    typeof localStorage.getItem !== 'function'
  ) {
    return noopStorage;
  }
  return localStorage;
};

interface ProjectSettings {
  customFilters?: Record<string, unknown> | undefined;
  defaultView?: string | undefined;
  pinnedItems?: string[] | undefined;
}

interface ProjectStateData {
  currentProject: Project | null;
  currentProjectId: string | null;
  projectSettings: Record<string, ProjectSettings>;
  recentProjects: string[];
}

interface ProjectStateActions {
  addRecentProject: (projectId: string) => void;
  clearCurrentProject: () => void;
  getProjectSettings: (projectId: string) => ProjectSettings;
  pinItem: (projectId: string, itemId: string) => void;
  setCurrentProject: (project: Project | null) => void;
  setRecentProjects: (projectIds: string[]) => void;
  unpinItem: (projectId: string, itemId: string) => void;
  updateProjectSettings: (projectId: string, settings: ProjectSettings) => void;
}

type ProjectState = ProjectStateData & ProjectStateActions;

type StoreSetter = (
  partial: Partial<ProjectState> | ((state: ProjectState) => Partial<ProjectState> | ProjectState),
) => void;

type StoreGetter = () => ProjectState;

const createInitialState = (): ProjectStateData => ({
  currentProject: null,
  currentProjectId: null,
  projectSettings: {},
  recentProjects: [],
});

const normalizeRecentProjects = (projectIds: string[]): string[] =>
  projectIds.slice(0, RECENT_PROJECTS_LIMIT);

const getProjectSettingsOrDefault = (state: ProjectState, projectId: string): ProjectSettings =>
  state.projectSettings[projectId] ?? {};

const createRecentProjectActions = (
  set: StoreSetter,
): Pick<ProjectStateActions, 'addRecentProject' | 'setRecentProjects'> => ({
  addRecentProject: (projectId) => {
    set((state) => {
      const filtered = state.recentProjects.filter((id) => id !== projectId);
      return {
        recentProjects: normalizeRecentProjects([projectId, ...filtered]),
      };
    });
  },
  setRecentProjects: (projectIds) => {
    set({
      recentProjects: normalizeRecentProjects(projectIds),
    });
  },
});

const createCurrentProjectActions = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<ProjectStateActions, 'clearCurrentProject' | 'setCurrentProject'> => ({
  clearCurrentProject: () => {
    set({
      currentProject: null,
      currentProjectId: null,
    });
  },
  setCurrentProject: (project) => {
    set({
      currentProject: project,
      currentProjectId: project?.id ?? null,
    });
    if (project?.id) {
      get().addRecentProject(project.id);
    }
  },
});

const createProjectSettingsActions = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<
  ProjectStateActions,
  'getProjectSettings' | 'pinItem' | 'unpinItem' | 'updateProjectSettings'
> => ({
  getProjectSettings: (projectId) => get().projectSettings[projectId] ?? {},
  pinItem: (projectId, itemId) => {
    set((state) => {
      const current = getProjectSettingsOrDefault(state, projectId);
      const pinnedItems = current.pinnedItems ?? [];
      if (pinnedItems.includes(itemId)) {
        return state;
      }
      return {
        projectSettings: {
          ...state.projectSettings,
          [projectId]: {
            ...current,
            pinnedItems: [...pinnedItems, itemId],
          },
        },
      };
    });
  },
  unpinItem: (projectId, itemId) => {
    set((state) => {
      const current = getProjectSettingsOrDefault(state, projectId);
      const pinnedItems = current.pinnedItems ?? [];
      return {
        projectSettings: {
          ...state.projectSettings,
          [projectId]: {
            ...current,
            pinnedItems: pinnedItems.filter((id) => id !== itemId),
          },
        },
      };
    });
  },
  updateProjectSettings: (projectId, settings) => {
    set((state) => ({
      projectSettings: {
        ...state.projectSettings,
        [projectId]: {
          ...state.projectSettings[projectId],
          ...settings,
        },
      },
    }));
  },
});

const buildProjectStore = (set: StoreSetter, get: StoreGetter): ProjectState => ({
  ...createInitialState(),
  ...createCurrentProjectActions(set, get),
  ...createProjectSettingsActions(set, get),
  ...createRecentProjectActions(set),
});

export const useProjectStore = create<ProjectState>()(
  persist<ProjectState>((set, get) => buildProjectStore(set, get), {
    name: 'tracertm-project-store',
    partialize: (state: ProjectState) =>
      ({
        currentProjectId: state.currentProjectId,
        projectSettings: state.projectSettings,
        recentProjects: state.recentProjects,
      }) as unknown as ProjectState,
    storage: createJSONStorage(() => getStorage()),
  }),
);
