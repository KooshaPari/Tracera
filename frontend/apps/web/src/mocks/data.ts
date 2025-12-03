// Mock data for TraceRTM development
import type { Agent, Item, Link, Project } from '../api/types'
import { AgentStatus, ItemPriority, ItemStatus, ItemType, LinkType } from '../api/types'

// Helper to generate timestamps
const now = new Date().toISOString()
const yesterday = new Date(Date.now() - 86400000).toISOString()
const lastWeek = new Date(Date.now() - 604800000).toISOString()

// Mock Projects
export const mockProjects: Project[] = [
  {
    id: 'proj-1',
    name: 'TraceRTM Core',
    description: 'Core traceability platform for requirements management',
    metadata: {
      team: 'Platform',
      status: 'active',
    },
    created_at: lastWeek,
    updated_at: now,
  },
  {
    id: 'proj-2',
    name: 'Mobile App',
    description: 'React Native mobile application',
    metadata: {
      team: 'Mobile',
      status: 'active',
    },
    created_at: yesterday,
    updated_at: now,
  },
]

// Mock Items
export const mockItems: Item[] = [
  {
    id: 'item-1',
    project_id: 'proj-1',
    type: ItemType.REQUIREMENT,
    title: 'User Authentication',
    description: 'Implement secure user authentication system',
    status: ItemStatus.COMPLETED,
    priority: ItemPriority.HIGH,
    metadata: { tags: ['security', 'auth'] },
    created_at: lastWeek,
    updated_at: yesterday,
  },
  {
    id: 'item-2',
    project_id: 'proj-1',
    type: ItemType.FEATURE,
    title: 'Project Dashboard',
    description: 'Create comprehensive project dashboard with metrics',
    status: ItemStatus.IN_PROGRESS,
    priority: ItemPriority.HIGH,
    metadata: { tags: ['ui', 'dashboard'] },
    created_at: lastWeek,
    updated_at: now,
    parent_id: 'item-1',
  },
  {
    id: 'item-3',
    project_id: 'proj-1',
    type: ItemType.CODE,
    title: 'Auth Service Implementation',
    description: 'JWT-based authentication service',
    status: ItemStatus.COMPLETED,
    priority: ItemPriority.HIGH,
    metadata: { file_path: 'src/services/auth.ts' },
    created_at: lastWeek,
    updated_at: yesterday,
  },
  {
    id: 'item-4',
    project_id: 'proj-1',
    type: ItemType.TEST,
    title: 'Auth Service Tests',
    description: 'Unit tests for authentication service',
    status: ItemStatus.COMPLETED,
    priority: ItemPriority.MEDIUM,
    metadata: { coverage: 95 },
    created_at: lastWeek,
    updated_at: yesterday,
  },
  {
    id: 'item-5',
    project_id: 'proj-1',
    type: ItemType.API,
    title: 'Login Endpoint',
    description: 'POST /api/auth/login endpoint',
    status: ItemStatus.COMPLETED,
    priority: ItemPriority.HIGH,
    metadata: { method: 'POST', path: '/api/auth/login' },
    created_at: lastWeek,
    updated_at: yesterday,
  },
  {
    id: 'item-6',
    project_id: 'proj-1',
    type: ItemType.DATABASE,
    title: 'Users Table',
    description: 'Database schema for user accounts',
    status: ItemStatus.COMPLETED,
    priority: ItemPriority.HIGH,
    metadata: { table: 'users' },
    created_at: lastWeek,
    updated_at: yesterday,
  },
  {
    id: 'item-7',
    project_id: 'proj-1',
    type: ItemType.WIREFRAME,
    title: 'Login Screen',
    description: 'Wireframe for login interface',
    status: ItemStatus.COMPLETED,
    priority: ItemPriority.MEDIUM,
    metadata: { figma_url: 'https://figma.com/...' },
    created_at: lastWeek,
    updated_at: yesterday,
  },
  {
    id: 'item-8',
    project_id: 'proj-1',
    type: ItemType.DOCUMENTATION,
    title: 'Auth API Documentation',
    description: 'OpenAPI specification for authentication endpoints',
    status: ItemStatus.IN_PROGRESS,
    priority: ItemPriority.MEDIUM,
    metadata: { format: 'openapi' },
    created_at: lastWeek,
    updated_at: now,
  },
  {
    id: 'item-9',
    project_id: 'proj-2',
    type: ItemType.REQUIREMENT,
    title: 'Offline Mode',
    description: 'Support offline data access and sync',
    status: ItemStatus.PENDING,
    priority: ItemPriority.CRITICAL,
    metadata: { tags: ['mobile', 'sync'] },
    created_at: yesterday,
    updated_at: now,
  },
  {
    id: 'item-10',
    project_id: 'proj-2',
    type: ItemType.FEATURE,
    title: 'Local Storage Sync',
    description: 'Implement local-first data storage',
    status: ItemStatus.PENDING,
    priority: ItemPriority.HIGH,
    metadata: { tags: ['storage', 'sync'] },
    created_at: yesterday,
    updated_at: now,
    parent_id: 'item-9',
  },
]

// Mock Links
export const mockLinks: Link[] = [
  {
    id: 'link-1',
    source_id: 'item-3',
    target_id: 'item-1',
    type: LinkType.IMPLEMENTS,
    metadata: {},
    created_at: lastWeek,
    updated_at: lastWeek,
  },
  {
    id: 'link-2',
    source_id: 'item-4',
    target_id: 'item-3',
    type: LinkType.TESTS,
    metadata: {},
    created_at: lastWeek,
    updated_at: lastWeek,
  },
  {
    id: 'link-3',
    source_id: 'item-5',
    target_id: 'item-1',
    type: LinkType.IMPLEMENTS,
    metadata: {},
    created_at: lastWeek,
    updated_at: lastWeek,
  },
  {
    id: 'link-4',
    source_id: 'item-6',
    target_id: 'item-1',
    type: LinkType.IMPLEMENTS,
    metadata: {},
    created_at: lastWeek,
    updated_at: lastWeek,
  },
  {
    id: 'link-5',
    source_id: 'item-7',
    target_id: 'item-1',
    type: LinkType.RELATES_TO,
    metadata: {},
    created_at: lastWeek,
    updated_at: lastWeek,
  },
  {
    id: 'link-6',
    source_id: 'item-8',
    target_id: 'item-5',
    type: LinkType.DOCUMENTS,
    metadata: {},
    created_at: lastWeek,
    updated_at: lastWeek,
  },
  {
    id: 'link-7',
    source_id: 'item-10',
    target_id: 'item-9',
    type: LinkType.IMPLEMENTS,
    metadata: {},
    created_at: yesterday,
    updated_at: yesterday,
  },
]

// Mock Agents
export const mockAgents: Agent[] = [
  {
    id: 'agent-1',
    name: 'Code Analyzer',
    type: 'analyzer',
    capabilities: ['code-analysis', 'dependency-detection', 'trace-generation'],
    status: AgentStatus.IDLE,
    metadata: { version: '1.0.0' },
    created_at: lastWeek,
    updated_at: now,
    last_heartbeat: now,
  },
  {
    id: 'agent-2',
    name: 'Test Runner',
    type: 'test',
    capabilities: ['test-execution', 'coverage-analysis'],
    status: AgentStatus.BUSY,
    metadata: { version: '1.0.0' },
    created_at: lastWeek,
    updated_at: now,
    last_heartbeat: now,
  },
  {
    id: 'agent-3',
    name: 'Documentation Generator',
    type: 'documentation',
    capabilities: ['doc-generation', 'api-spec-generation'],
    status: AgentStatus.IDLE,
    metadata: { version: '1.0.0' },
    created_at: lastWeek,
    updated_at: now,
    last_heartbeat: now,
  },
]

// Helper functions for mock data manipulation
export function findItemById(id: string): Item | undefined {
  return mockItems.find((item) => item.id === id)
}

export function findProjectById(id: string): Project | undefined {
  return mockProjects.find((project) => project.id === id)
}

export function findLinkById(id: string): Link | undefined {
  return mockLinks.find((link) => link.id === id)
}

export function findAgentById(id: string): Agent | undefined {
  return mockAgents.find((agent) => agent.id === id)
}

export function filterItemsByProject(projectId: string): Item[] {
  return mockItems.filter((item) => item.project_id === projectId)
}

export function filterLinksBySource(sourceId: string): Link[] {
  return mockLinks.filter((link) => link.source_id === sourceId)
}

export function filterLinksByTarget(targetId: string): Link[] {
  return mockLinks.filter((link) => link.target_id === targetId)
}

// Generate new IDs
let nextProjectId = mockProjects.length + 1
let nextItemId = mockItems.length + 1
let nextLinkId = mockLinks.length + 1
let nextAgentId = mockAgents.length + 1

export function generateProjectId(): string {
  return `proj-${nextProjectId++}`
}

export function generateItemId(): string {
  return `item-${nextItemId++}`
}

export function generateLinkId(): string {
  return `link-${nextLinkId++}`
}

export function generateAgentId(): string {
  return `agent-${nextAgentId++}`
}
