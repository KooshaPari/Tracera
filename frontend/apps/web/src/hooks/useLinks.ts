import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { Link, LinkType } from '@tracertm/types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface LinkFilters {
  projectId?: string | undefined
  sourceId?: string | undefined
  targetId?: string | undefined
  type?: LinkType | undefined
}

async function fetchLinks(filters: LinkFilters = {}): Promise<Link[]> {
  const params = new URLSearchParams()
  if (filters.projectId) params.set('project_id', filters.projectId)
  if (filters.sourceId) params.set('source_id', filters.sourceId)
  if (filters.targetId) params.set('target_id', filters.targetId)
  if (filters.type) params.set('type', filters.type)

  const res = await fetch(`${API_URL}/api/v1/links?${params}`)
  if (!res.ok) throw new Error('Failed to fetch links')
  return res.json() as Promise<Link[]>
}

interface CreateLinkData {
  projectId: string
  sourceId: string
  targetId: string
  type: LinkType
  description?: string
}

async function createLink(data: CreateLinkData): Promise<Link> {
  const res = await fetch(`${API_URL}/api/v1/links`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_id: data.projectId,
      source_id: data.sourceId,
      target_id: data.targetId,
      type: data.type,
      description: data.description,
    }),
  })
  if (!res.ok) throw new Error('Failed to create link')
  return res.json() as Promise<Link>
}

async function deleteLink(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/links/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete link')
}

export function useLinks(filters: LinkFilters = {}) {
  return useQuery({
    queryKey: ['links', filters],
    queryFn: () => fetchLinks(filters),
  })
}

export function useCreateLink() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createLink,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['links'] })
    },
  })
}

export function useDeleteLink() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteLink,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['links'] })
    },
  })
}

// Graph data hook for visualization
export function useTraceabilityGraph(projectId: string) {
  const { data: items } = useQuery<
    Array<{ id: string; title: string; view: string; status: string }>
  >({
    queryKey: ['items', { projectId }],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/api/v1/items?project_id=${projectId}`)
      if (!res.ok) throw new Error('Failed to fetch items')
      return res.json() as Promise<
        Array<{ id: string; title: string; view: string; status: string }>
      >
    },
    enabled: !!projectId,
  })

  const { data: links } = useLinks({ projectId })

  return {
    nodes: (items ?? []).map((item) => ({
      data: { id: item.id, label: item.title, type: item.view.toLowerCase(), status: item.status },
    })),
    edges: (links ?? []).map((link) => ({
      data: { id: link.id, source: link.sourceId, target: link.targetId, type: link.type },
    })),
    isLoading: !(items && links),
  }
}
