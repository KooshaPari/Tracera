import { observable } from '@legendapp/state';

import type { Agent, Item, Link, Project } from '@tracertm/types';

// Global application state with Legend State
export const appState$ = observable({
  // Current project
  currentProject: null as Project | null,

  // Items indexed by view
  items: {} as Record<string, Item[]>,

  // Links
  links: [] as Link[],

  // Active agents
  agents: [] as Agent[],

  // UI State
  ui: {
    currentView: 'FEATURE' as string,
    isDarkMode: false,
    searchQuery: '',
    selectedItemId: null as string | null,
    sidebarOpen: true,
  },

  // Sync state
  sync: {
    isOnline: true,
    lastSyncedAt: null as string | null,
    pendingMutations: 0,
  },
});

// Selectors
export const currentProject$ = appState$.currentProject;
export const currentView$ = appState$.ui.currentView;
export const isOnline$ = appState$.sync.isOnline;

// Actions
export const actions = {
  selectItem: (id: string | null) => {
    appState$.ui.selectedItemId.set(id);
  },

  setOnline: (online: boolean) => {
    appState$.sync.isOnline.set(online);
  },

  setProject: (project: Project) => {
    appState$.currentProject.set(project);
  },

  setView: (view: string) => {
    appState$.ui.currentView.set(view);
  },

  toggleDarkMode: () => {
    appState$.ui.isDarkMode.set(!appState$.ui.isDarkMode.get());
  },

  toggleSidebar: () => {
    appState$.ui.sidebarOpen.set(!appState$.ui.sidebarOpen.get());
  },
};
