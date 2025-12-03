// Core domain types matching TraceRTM backend

export type ViewType =
  | 'FEATURE'
  | 'CODE'
  | 'TEST'
  | 'API'
  | 'DATABASE'
  | 'WIREFRAME'
  | 'DOCUMENTATION'
  | 'DEPLOYMENT'

export type ItemStatus = 'todo' | 'in_progress' | 'done' | 'blocked' | 'cancelled'

export type Priority = 'low' | 'medium' | 'high' | 'critical'

export type LinkType = 'implements' | 'tests' | 'depends_on' | 'related_to' | 'blocks' | 'parent_of'

export interface Project {
  id: string
  name: string
  description?: string
  createdAt: string
  updatedAt: string
}

export interface Item {
  id: string
  projectId: string
  view: ViewType
  type: string
  title: string
  description?: string
  status: ItemStatus
  priority: Priority
  parentId?: string
  owner?: string
  metadata?: Record<string, unknown>
  version: number
  createdAt: string
  updatedAt: string
}

export interface Link {
  id: string
  projectId: string
  sourceId: string
  targetId: string
  type: LinkType
  description?: string
  metadata?: Record<string, unknown>
  createdAt: string
}

export interface Agent {
  id: string
  name: string
  type: string
  status: 'active' | 'idle' | 'offline'
  lastSeen: string
}

export interface Mutation {
  id: string
  agentId: string
  itemId: string
  operation: 'create' | 'update' | 'delete'
  data: Record<string, unknown>
  timestamp: string
  synced: boolean
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}

export interface ApiError {
  code: string
  message: string
  details?: Record<string, unknown>
}
