import type { Project } from '@tracertm/types'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ProjectState {
  // Current project
  currentProjectId: string | null
  currentProject: Project | null

  // Recent projects
  recentProjects: string[]

  // Project preferences
  projectSettings: Record<
    string,
    {
      defaultView?: string
      pinnedItems?: string[]
      customFilters?: Record<string, unknown>
    }
  >

  // Actions
  setCurrentProject: (project: Project | null) => void
  addRecentProject: (projectId: string) => void
  getProjectSettings: (projectId: string) => any
  updateProjectSettings: (projectId: string, settings: Record<string, unknown>) => void
  pinItem: (projectId: string, itemId: string) => void
  unpinItem: (projectId: string, itemId: string) => void
  clearCurrentProject: () => void
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentProjectId: null,
      currentProject: null,
      recentProjects: [],
      projectSettings: {},

      // Actions
      setCurrentProject: (project) => {
        set({
          currentProject: project,
          currentProjectId: project?.id || null,
        })
        if (project?.id) {
          get().addRecentProject(project.id)
        }
      },

      addRecentProject: (projectId) =>
        set((state) => {
          const filtered = state.recentProjects.filter((id) => id !== projectId)
          return {
            recentProjects: [projectId, ...filtered].slice(0, 10), // Keep last 10
          }
        }),

      getProjectSettings: (projectId) => {
        return get().projectSettings[projectId] || {}
      },

      updateProjectSettings: (projectId, settings) =>
        set((state) => ({
          projectSettings: {
            ...state.projectSettings,
            [projectId]: {
              ...state.projectSettings[projectId],
              ...settings,
            },
          },
        })),

      pinItem: (projectId, itemId) =>
        set((state) => {
          const current = state.projectSettings[projectId] || {}
          const pinnedItems = current.pinnedItems || []
          if (!pinnedItems.includes(itemId)) {
            return {
              projectSettings: {
                ...state.projectSettings,
                [projectId]: {
                  ...current,
                  pinnedItems: [...pinnedItems, itemId],
                },
              },
            }
          }
          return state
        }),

      unpinItem: (projectId, itemId) =>
        set((state) => {
          const current = state.projectSettings[projectId] || {}
          const pinnedItems = current.pinnedItems || []
          return {
            projectSettings: {
              ...state.projectSettings,
              [projectId]: {
                ...current,
                pinnedItems: pinnedItems.filter((id) => id !== itemId),
              },
            },
          }
        }),

      clearCurrentProject: () =>
        set({
          currentProject: null,
          currentProjectId: null,
        }),
    }),
    {
      name: 'tracertm-project-store',
      partialize: (state) => ({
        currentProjectId: state.currentProjectId,
        recentProjects: state.recentProjects,
        projectSettings: state.projectSettings,
      }),
    }
  )
)
