import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { Item, ItemStatus, Priority, ViewType } from '@tracertm/types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface ItemFilters {
  projectId?: string | undefined
  view?: ViewType | undefined
  status?: ItemStatus | undefined
  parentId?: string | undefined
}

async function fetchItems(filters: ItemFilters = {}): Promise<Item[]> {
  const params = new URLSearchParams()
  if (filters.projectId) params.set('project_id', filters.projectId)
  if (filters.view) params.set('view', filters.view)
  if (filters.status) params.set('status', filters.status)
  if (filters.parentId) params.set('parent_id', filters.parentId)

  const res = await fetch(`${API_URL}/api/v1/items?${params}`)
  if (!res.ok) throw new Error('Failed to fetch items')
  return res.json() as Promise<Item[]>
}

async function fetchItem(id: string): Promise<Item> {
  const res = await fetch(`${API_URL}/api/v1/items/${id}`)
  if (!res.ok) throw new Error('Failed to fetch item')
  return res.json() as Promise<Item>
}

interface CreateItemData {
  projectId: string
  view: ViewType
  type: string
  title: string
  description?: string
  status: ItemStatus
  priority: Priority
  parentId?: string
  owner?: string
}

async function createItem(data: CreateItemData): Promise<Item> {
  const res = await fetch(`${API_URL}/api/v1/items`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_id: data.projectId,
      view: data.view,
      type: data.type,
      title: data.title,
      description: data.description,
      status: data.status,
      priority: data.priority,
      parent_id: data.parentId,
      owner: data.owner,
    }),
  })
  if (!res.ok) throw new Error('Failed to create item')
  return res.json() as Promise<Item>
}

async function updateItem(id: string, data: Partial<Item>): Promise<Item> {
  const res = await fetch(`${API_URL}/api/v1/items/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Failed to update item')
  return res.json() as Promise<Item>
}

async function deleteItem(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/items/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete item')
}

export function useItems(filters: ItemFilters = {}) {
  return useQuery({
    queryKey: ['items', filters],
    queryFn: () => fetchItems(filters),
  })
}

export function useItem(id: string) {
  return useQuery({
    queryKey: ['items', id],
    queryFn: () => fetchItem(id),
    enabled: !!id,
  })
}

export function useCreateItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    },
  })
}

export function useUpdateItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Item> }) => updateItem(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
      queryClient.invalidateQueries({ queryKey: ['items', id] })
    },
  })
}

export function useDeleteItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    },
  })
}
