import type { Item, ItemStatus, Link, Priority, Project, ViewType } from '@tracertm/types';

// Helper to generate timestamps
const now = new Date().toISOString();
const yesterday = new Date(Date.now() - 86_400_000).toISOString();
const lastWeek = new Date(Date.now() - 604_800_000).toISOString();

// Mock Projects
export const mockProjects: Project[] = [
  {
    createdAt: lastWeek,
    description: 'Core traceability management system',
    id: 'proj-1',
    name: 'TraceRTM Core',
    updatedAt: yesterday,
  },
  {
    createdAt: yesterday,
    description: 'Web interface for traceability management',
    id: 'proj-2',
    name: 'Web Dashboard',
    updatedAt: now,
  },
];

// Mock Items
export const mockItems: Item[] = [
  {
    createdAt: lastWeek,
    description: 'Implement secure user authentication system',
    id: 'item-1',
    priority: 'high' as Priority,
    projectId: 'proj-1',
    status: 'done' as ItemStatus,
    title: 'User Authentication',
    type: 'requirement',
    updatedAt: yesterday,
    version: 1,
    view: 'FEATURE' as ViewType,
  },
  {
    createdAt: lastWeek,
    description: 'Create comprehensive project dashboard with metrics',
    id: 'item-2',
    parentId: 'item-1',
    priority: 'high' as Priority,
    projectId: 'proj-1',
    status: 'in_progress' as ItemStatus,
    title: 'Project Dashboard',
    type: 'feature',
    updatedAt: now,
    version: 1,
    view: 'FEATURE' as ViewType,
  },
];

// Mock Links
export const mockLinks: Link[] = [
  {
    createdAt: lastWeek,
    id: 'link-1',
    projectId: 'proj-1',
    sourceId: 'item-1',
    targetId: 'item-2',
    type: 'implements',
  },
];

export const mockData = {
  items: mockItems,
  links: mockLinks,
  projects: mockProjects,
};
