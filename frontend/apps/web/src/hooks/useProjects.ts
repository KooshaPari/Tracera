import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { Project } from '@tracertm/types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_URL}/api/v1/projects`)
  if (!res.ok) throw new Error('Failed to fetch projects')
  return res.json() as Promise<Project[]>
}

async function fetchProject(id: string): Promise<Project> {
  const res = await fetch(`${API_URL}/api/v1/projects/${id}`)
  if (!res.ok) throw new Error('Failed to fetch project')
  return res.json() as Promise<Project>
}

async function createProject(data: {
  name: string
  description?: string | undefined
}): Promise<Project> {
  const res = await fetch(`${API_URL}/api/v1/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Failed to create project')
  return res.json() as Promise<Project>
}

async function updateProject(id: string, data: Partial<Project>): Promise<Project> {
  const res = await fetch(`${API_URL}/api/v1/projects/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Failed to update project')
  return res.json() as Promise<Project>
}

async function deleteProject(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/projects/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete project')
}

export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: fetchProjects,
  })
}

export function useProject(id: string) {
  return useQuery({
    queryKey: ['projects', id],
    queryFn: () => fetchProject(id),
    enabled: !!id,
  })
}

export function useCreateProject() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    },
  })
}

export function useUpdateProject() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Project> }) => updateProject(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      queryClient.invalidateQueries({ queryKey: ['projects', id] })
    },
  })
}

export function useDeleteProject() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    },
  })
}
