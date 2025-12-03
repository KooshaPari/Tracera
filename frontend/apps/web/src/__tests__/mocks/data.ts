/**
 * Mock data factories for tests
 */

import type { Project } from '@tracertm/types'
import type {
  Agent,
  AgentStatus,
  GraphData,
  Item,
  ItemPriority,
  ItemStatus,
  ItemType,
  Link,
  LinkType,
  SearchResult,
} from '../../api/types'

// Projects
export const mockProjects: Project[] = [
  {
    id: 'proj-1',
    name: 'Test Project',
    description: 'Test project description',
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-01T00:00:00Z',
  },
  {
    id: 'proj-2',
    name: 'Another Project',
    description: 'Another test project',
    createdAt: '2025-01-02T00:00:00Z',
    updatedAt: '2025-01-02T00:00:00Z',
  },
]

// Items
export const mockItems: Item[] = [
  {
    id: 'item-1',
    project_id: 'proj-1',
    type: 'feature' as ItemType,
    title: 'Test Feature',
    description: 'A test feature item',
    status: 'in_progress' as ItemStatus,
    priority: 'high' as ItemPriority,
    metadata: {},
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  },
  {
    id: 'item-2',
    project_id: 'proj-1',
    type: 'requirement' as ItemType,
    title: 'Test Requirement',
    description: 'A test requirement item',
    status: 'completed' as ItemStatus,
    priority: 'medium' as ItemPriority,
    metadata: {},
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  },
  {
    id: 'item-3',
    project_id: 'proj-1',
    type: 'test' as ItemType,
    title: 'Test Case',
    description: 'A test case item',
    status: 'pending' as ItemStatus,
    priority: 'low' as ItemPriority,
    metadata: {},
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  },
]

// Links
export const mockLinks: Link[] = [
  {
    id: 'link-1',
    source_id: 'item-1',
    target_id: 'item-2',
    type: 'implements' as LinkType,
    metadata: {},
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  },
  {
    id: 'link-2',
    source_id: 'item-3',
    target_id: 'item-1',
    type: 'tests' as LinkType,
    metadata: {},
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  },
]

// Agents
export const mockAgents: Agent[] = [
  {
    id: 'agent-1',
    name: 'Test Agent',
    type: 'ai',
    capabilities: ['code-generation', 'testing'],
    status: 'idle' as AgentStatus,
    metadata: {},
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  },
]

// Graph data
export const mockGraphData: GraphData = {
  nodes: [
    {
      id: 'item-1',
      type: 'feature' as ItemType,
      title: 'Test Feature',
      status: 'in_progress' as ItemStatus,
      metadata: {},
    },
    {
      id: 'item-2',
      type: 'requirement' as ItemType,
      title: 'Test Requirement',
      status: 'completed' as ItemStatus,
      metadata: {},
    },
  ],
  edges: [
    {
      id: 'link-1',
      source: 'item-1',
      target: 'item-2',
      type: 'implements' as LinkType,
      metadata: {},
    },
  ],
}

// Search results
export const mockSearchResult: SearchResult = {
  items: mockItems,
  total: 3,
  page: 1,
  per_page: 10,
  query: 'test',
}

// Factory functions
export const createMockProject = (overrides?: Partial<Project>): Project => {
  const project: Project = {
    id: `proj-${Date.now()}`,
    name: 'Test Project',
    description: 'Test description',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ...overrides,
  }
  return project
}

export const createMockItem = (overrides?: Partial<Item>): Item => ({
  id: `item-${Date.now()}`,
  project_id: 'proj-1',
  type: 'feature' as ItemType,
  title: 'Test Item',
  description: 'Test description',
  status: 'pending' as ItemStatus,
  priority: 'medium' as ItemPriority,
  metadata: {},
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  ...overrides,
})

export const createMockLink = (overrides?: Partial<Link>): Link => ({
  id: `link-${Date.now()}`,
  source_id: 'item-1',
  target_id: 'item-2',
  type: 'implements' as LinkType,
  metadata: {},
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  ...overrides,
})

export const createMockAgent = (overrides?: Partial<Agent>): Agent => ({
  id: `agent-${Date.now()}`,
  name: 'Test Agent',
  type: 'ai',
  capabilities: ['testing'],
  status: 'idle' as AgentStatus,
  metadata: {},
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  ...overrides,
})
