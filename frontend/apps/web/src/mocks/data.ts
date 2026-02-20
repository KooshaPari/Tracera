// Mock data for TraceRTM development
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
  {
    createdAt: yesterday,
    description: 'Unit tests for authentication',
    id: 'item-3',
    priority: 'medium' as Priority,
    projectId: 'proj-1',
    status: 'todo' as ItemStatus,
    title: 'Auth Tests',
    type: 'test',
    updatedAt: now,
    version: 1,
    view: 'CODE' as ViewType,
  },
  {
    createdAt: yesterday,
    description: 'REST API endpoints for user management',
    id: 'item-4',
    priority: 'high' as Priority,
    projectId: 'proj-1',
    status: 'in_progress' as ItemStatus,
    title: 'Authentication API',
    type: 'api',
    updatedAt: now,
    version: 1,
    view: 'API' as ViewType,
  },
  {
    createdAt: lastWeek,
    description: 'Database schema for users table',
    id: 'item-5',
    priority: 'critical' as Priority,
    projectId: 'proj-1',
    status: 'done' as ItemStatus,
    title: 'User Database Schema',
    type: 'database',
    updatedAt: lastWeek,
    version: 1,
    view: 'DATABASE' as ViewType,
  },
  {
    createdAt: yesterday,
    description: 'Figma mockup for main dashboard',
    id: 'item-6',
    priority: 'high' as Priority,
    projectId: 'proj-2',
    status: 'done' as ItemStatus,
    title: 'Dashboard Mockup',
    type: 'wireframe',
    updatedAt: now,
    version: 1,
    view: 'WIREFRAME' as ViewType,
  },
  {
    createdAt: yesterday,
    description: 'Complete API documentation',
    id: 'item-7',
    priority: 'medium' as Priority,
    projectId: 'proj-2',
    status: 'in_progress' as ItemStatus,
    title: 'API Documentation',
    type: 'documentation',
    updatedAt: now,
    version: 1,
    view: 'DOCUMENTATION' as ViewType,
  },
  {
    createdAt: now,
    description: 'Deploy to production environment',
    id: 'item-8',
    priority: 'critical' as Priority,
    projectId: 'proj-2',
    status: 'todo' as ItemStatus,
    title: 'Production Deployment',
    type: 'deployment',
    updatedAt: now,
    version: 1,
    view: 'DEPLOYMENT' as ViewType,
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
    updatedAt: lastWeek,
    version: 1,
  },
  {
    createdAt: yesterday,
    id: 'link-2',
    projectId: 'proj-1',
    sourceId: 'item-2',
    targetId: 'item-3',
    type: 'tests',
    updatedAt: yesterday,
    version: 1,
  },
  {
    createdAt: yesterday,
    id: 'link-3',
    projectId: 'proj-1',
    sourceId: 'item-1',
    targetId: 'item-4',
    type: 'depends_on',
    updatedAt: yesterday,
    version: 1,
  },
  {
    createdAt: lastWeek,
    id: 'link-4',
    projectId: 'proj-1',
    sourceId: 'item-4',
    targetId: 'item-5',
    type: 'depends_on',
    updatedAt: lastWeek,
    version: 1,
  },
];

// Helper functions for filtering and finding mock data
export const filterItemsByProject = (projectId: string): Item[] =>
  mockItems.filter((item) => item.projectId === projectId);

export const filterLinksBySource = (sourceId: string): Link[] =>
  mockLinks.filter((link) => link.sourceId === sourceId);

export const filterLinksByTarget = (targetId: string): Link[] =>
  mockLinks.filter((link) => link.targetId === targetId);

export const findProjectById = (id: string): Project | undefined =>
  mockProjects.find((project) => project.id === id);

export const findItemById = (id: string): Item | undefined =>
  mockItems.find((item) => item.id === id);

export const findLinkById = (id: string): Link | undefined =>
  mockLinks.find((link) => link.id === id);

export const generateProjectId = (): string =>
  `proj-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

export const generateItemId = (): string =>
  `item-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

export const generateLinkId = (): string =>
  `link-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

// Export all mock data
export const mockData = {
  items: mockItems,
  links: mockLinks,
  projects: mockProjects,
};
