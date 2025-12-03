// API Types for TraceRTM
export interface Project {
  id: string
  name: string
  description?: string
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface Item {
  id: string
  project_id: string
  type: ItemType
  title: string
  description?: string
  status: ItemStatus
  priority?: ItemPriority
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
  parent_id?: string
}

export enum ItemType {
  REQUIREMENT = 'requirement',
  FEATURE = 'feature',
  CODE = 'code',
  TEST = 'test',
  API = 'api',
  DATABASE = 'database',
  WIREFRAME = 'wireframe',
  DOCUMENTATION = 'documentation',
  DEPLOYMENT = 'deployment',
}

export enum ItemStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  BLOCKED = 'blocked',
  CANCELLED = 'cancelled',
}

export enum ItemPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export interface Link {
  id: string
  source_id: string
  target_id: string
  type: LinkType
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

export enum LinkType {
  IMPLEMENTS = 'implements',
  TESTS = 'tests',
  DEPENDS_ON = 'depends_on',
  RELATES_TO = 'relates_to',
  DOCUMENTS = 'documents',
  DEPLOYS = 'deploys',
}

export interface Agent {
  id: string
  name: string
  type: string
  capabilities: string[]
  status: AgentStatus
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
  last_heartbeat?: string
}

export enum AgentStatus {
  IDLE = 'idle',
  BUSY = 'busy',
  OFFLINE = 'offline',
  ERROR = 'error',
}

export interface GraphNode {
  id: string
  type: ItemType
  title: string
  status: ItemStatus
  metadata?: Record<string, any>
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  type: LinkType
  metadata?: Record<string, any>
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface SearchResult {
  items: Item[]
  total: number
  page: number
  per_page: number
  query: string
}

export interface SearchQuery {
  q: string
  types?: ItemType[]
  statuses?: ItemStatus[]
  priorities?: ItemPriority[]
  project_id?: string
  page?: number
  per_page?: number
}

export interface EventLog {
  id: string
  event_type: string
  entity_type: string
  entity_id: string
  data: Record<string, any>
  timestamp: string
  user_id?: string
}

export interface ImpactAnalysis {
  item_id: string
  affected_items: Item[]
  affected_count: number
  depth: number
}

export interface DependencyAnalysis {
  item_id: string
  dependencies: Item[]
  dependency_count: number
  depth: number
}

export interface TraceabilityMatrix {
  requirements: Item[]
  coverage: Record<
    string,
    {
      implemented_by: Item[]
      tested_by: Item[]
      documented_by: Item[]
      coverage_percentage: number
    }
  >
}

export interface PaginationParams {
  limit?: number
  offset?: number
}

export interface CreateProjectInput {
  name: string
  description?: string
  metadata?: Record<string, any>
}

export interface UpdateProjectInput {
  name?: string
  description?: string
  metadata?: Record<string, any>
}

export interface CreateItemInput {
  project_id: string
  type: ItemType
  title: string
  description?: string
  status?: ItemStatus
  priority?: ItemPriority
  metadata?: Record<string, any>
  parent_id?: string
}

export interface UpdateItemInput {
  type?: ItemType
  title?: string
  description?: string
  status?: ItemStatus
  priority?: ItemPriority
  metadata?: Record<string, any>
  parent_id?: string
}

export interface CreateLinkInput {
  source_id: string
  target_id: string
  type: LinkType
  metadata?: Record<string, any>
}

export interface UpdateLinkInput {
  type?: LinkType
  metadata?: Record<string, any>
}

export interface CreateAgentInput {
  name: string
  type: string
  capabilities: string[]
  metadata?: Record<string, any>
}

export interface UpdateAgentInput {
  name?: string
  type?: string
  capabilities?: string[]
  status?: AgentStatus
  metadata?: Record<string, any>
}

export interface AgentTask {
  id: string
  agent_id: string
  type: string
  payload: Record<string, any>
  status: string
  created_at: string
  updated_at: string
}

export interface TaskResult {
  task_id: string
  result: Record<string, any>
  status: string
}

export interface TaskError {
  task_id: string
  error: string
}
