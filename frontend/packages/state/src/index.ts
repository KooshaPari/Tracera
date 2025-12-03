import { observable } from '@legendapp/state'
import type { Agent, Item, Link, Project } from '@tracertm/types'

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
    sidebarOpen: true,
    currentView: 'FEATURE' as string,
    selectedItemId: null as string | null,
    searchQuery: '',
    isDarkMode: false,
  },

  // Sync state
  sync: {
    isOnline: true,
    pendingMutations: 0,
    lastSyncedAt: null as string | null,
  },
})

// Selectors
export const currentProject$ = appState$.currentProject
export const currentView$ = appState$.ui.currentView
export const isOnline$ = appState$.sync.isOnline

// Actions
export const actions = {
  setProject: (project: Project) => {
    appState$.currentProject.set(project)
  },

  setView: (view: string) => {
    appState$.ui.currentView.set(view)
  },

  selectItem: (id: string | null) => {
    appState$.ui.selectedItemId.set(id)
  },

  toggleSidebar: () => {
    appState$.ui.sidebarOpen.set(!appState$.ui.sidebarOpen.get())
  },

  toggleDarkMode: () => {
    appState$.ui.isDarkMode.set(!appState$.ui.isDarkMode.get())
  },

  setOnline: (online: boolean) => {
    appState$.sync.isOnline.set(online)
  },
}
