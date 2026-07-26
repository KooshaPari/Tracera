// MSW handlers for TraceRTM API mocking
import { HttpResponse, http } from 'msw';

import type {
  CreateItemInput,
  CreateLinkInput,
  CreateProjectInput,
  DependencyAnalysis,
  GraphData,
  ImpactAnalysis,
  Item,
  Link,
  Project,
  UpdateItemInput,
  UpdateLinkInput,
  UpdateProjectInput,
} from '../api/types';

import {
  filterItemsByProject,
  filterLinksBySource,
  filterLinksByTarget,
  findItemById,
  findLinkById,
  findProjectById,
  generateItemId,
  generateLinkId,
  generateProjectId,
  mockItems as mockItemsBaseline,
  mockLinks as mockLinksBaseline,
  mockProjects,
} from './data';
import { enhancedItems, enhancedLinks } from './enhanced-data';

// Toggle between baseline and enhanced mock data
const USE_ENHANCED_DATA = true;
const mockItems = USE_ENHANCED_DATA ? enhancedItems : mockItemsBaseline;
const mockLinks = USE_ENHANCED_DATA ? enhancedLinks : mockLinksBaseline;

const API_BASE = 'http://localhost:4000';

// Helper to simulate delays
const delay = async (ms = 100) => new Promise((resolve) => setTimeout(resolve, ms));

export const handlers = [
  // ============================================================================
  // HEALTH CHECK
  // ============================================================================
  http.get(`${API_BASE}/health`, async () => {
    await delay();
    return HttpResponse.json({
      service: 'tracertm-api',
      status: 'ok',
    });
  }),

  http.get(`${API_BASE}/api/v1/health`, async () => {
    await delay();
    return HttpResponse.json({
      service: 'tracertm-api',
      status: 'ok',
    });
  }),

  // ============================================================================
  // PROJECT ENDPOINTS
  // ============================================================================
  http.get(`${API_BASE}/api/v1/projects`, async ({ request }) => {
    await delay();
    const url = new URL(request.url);
    const limit = Number(url.searchParams.get('limit')) || mockProjects.length;
    const offset = Number(url.searchParams.get('offset')) || 0;

    const paginatedProjects = mockProjects.slice(offset, offset + limit);
    // API returns { total: number, projects: Project[] }
    return HttpResponse.json({
      projects: paginatedProjects,
      total: mockProjects.length,
    });
  }),

  http.get(`${API_BASE}/api/v1/projects/:id`, async ({ params }) => {
    await delay();
    const { id } = params;
    const project = findProjectById(id as string);

    if (!project) {
      return HttpResponse.json({ error: 'Project not found' }, { status: 404 });
    }

    return HttpResponse.json(project);
  }),

  http.post(`${API_BASE}/api/v1/projects`, async ({ request }) => {
    await delay();
    const body = (await request.json()) as CreateProjectInput;

    const newProject: Project = {
      id: generateProjectId(),
      name: body.name,
      ...(body.description !== undefined && { description: body.description }),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    mockProjects.push(newProject);
    return HttpResponse.json(newProject, { status: 201 });
  }),

  http.put(`${API_BASE}/api/v1/projects/:id`, async ({ params, request }) => {
    await delay();
    const { id } = params;
    const body = (await request.json()) as UpdateProjectInput;
    const projectIndex = mockProjects.findIndex((p) => p.id === id);

    if (projectIndex === -1) {
      return HttpResponse.json({ error: 'Project not found' }, { status: 404 });
    }

    const baseProject = mockProjects[projectIndex]!;
    const updatedProject: Project = {
      id: baseProject.id,
      name: body.name ?? baseProject.name,
      ...(body.description !== undefined
        ? { description: body.description }
        : baseProject.description !== undefined
          ? { description: baseProject.description }
          : {}),
      createdAt: baseProject.createdAt,
      updatedAt: new Date().toISOString(),
    };

    mockProjects[projectIndex] = updatedProject;
    return HttpResponse.json(updatedProject);
  }),

  http.delete(`${API_BASE}/api/v1/projects/:id`, async ({ params }) => {
    await delay();
    const { id } = params;
    const projectIndex = mockProjects.findIndex((p) => p.id === id);

    if (projectIndex === -1) {
      return HttpResponse.json({ error: 'Project not found' }, { status: 404 });
    }

    mockProjects.splice(projectIndex, 1);
    return HttpResponse.json(null, { status: 204 });
  }),

  // ============================================================================
  // ITEM ENDPOINTS
  // ============================================================================
  http.get(`${API_BASE}/api/v1/items`, async ({ request }) => {
    await delay();
    const url = new URL(request.url);
    const projectId = url.searchParams.get('project_id');
    const limit = Number(url.searchParams.get('limit')) || mockItems.length;
    const offset = Number(url.searchParams.get('offset')) || 0;

    let items = projectId ? filterItemsByProject(projectId) : mockItems;
    const total = items.length;
    items = items.slice(offset, offset + limit);

    // API returns { total: number, items: Item[] }
    return HttpResponse.json({ items, total });
  }),

  http.get(`${API_BASE}/api/v1/items/:id`, async ({ params }) => {
    await delay();
    const { id } = params;
    const item = findItemById(id as string);

    if (!item) {
      return HttpResponse.json({ error: 'Item not found' }, { status: 404 });
    }

    return HttpResponse.json(item);
  }),

  http.post(`${API_BASE}/api/v1/items`, async ({ request }) => {
    await delay();
    const body = (await request.json()) as CreateItemInput;

    const newItem: Item = {
      id: generateItemId(),
      projectId: body.projectId,
      type: body.type,
      title: body.title,
      ...(body.description !== undefined && { description: body.description }),
      status: body.status ?? ('todo' as const),
      priority: body.priority ?? ('medium' as const),
      view: 'FEATURE' as const,
      version: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ...(body.parentId !== undefined && { parentId: body.parentId }),
    };

    mockItems.push(newItem);
    return HttpResponse.json(newItem, { status: 201 });
  }),

  http.put(`${API_BASE}/api/v1/items/:id`, async ({ params, request }) => {
    await delay();
    const { id } = params;
    const body = (await request.json()) as UpdateItemInput;
    const itemIndex = mockItems.findIndex((i) => i.id === id);

    if (itemIndex === -1) {
      return HttpResponse.json({ error: 'Item not found' }, { status: 404 });
    }

    const baseItem = mockItems[itemIndex]!;
    const updatedItem: Item = {
      id: baseItem.id,
      projectId: baseItem.projectId,
      view: baseItem.view,
      version: baseItem.version,
      type: body.type ?? baseItem.type,
      title: body.title ?? baseItem.title,
      ...((body.description ?? baseItem.description) !== undefined && {
        description: body.description ?? baseItem.description,
      }),
      status: body.status ?? baseItem.status,
      priority: body.priority ?? baseItem.priority,
      createdAt: baseItem.createdAt,
      updatedAt: new Date().toISOString(),
      ...((body.parentId ?? baseItem.parentId) !== undefined && {
        parentId: body.parentId ?? baseItem.parentId,
      }),
    };

    mockItems[itemIndex] = updatedItem;
    return HttpResponse.json(updatedItem);
  }),

  http.delete(`${API_BASE}/api/v1/items/:id`, async ({ params }) => {
    await delay();
    const { id } = params;
    const itemIndex = mockItems.findIndex((i) => i.id === id);

    if (itemIndex === -1) {
      return HttpResponse.json({ error: 'Item not found' }, { status: 404 });
    }

    mockItems.splice(itemIndex, 1);
    return HttpResponse.json(null, { status: 204 });
  }),

  // ============================================================================
  // LINK ENDPOINTS
  // ============================================================================
  http.get(`${API_BASE}/api/v1/links`, async ({ request }) => {
    await delay();
    const url = new URL(request.url);
    const projectId = url.searchParams.get('project_id');
    const limit = Number(url.searchParams.get('limit')) || mockLinks.length;
    const offset = Number(url.searchParams.get('offset')) || 0;

    let links = mockLinks;
    if (projectId) {
      // Filter links by project (check source or target items)
      links = mockLinks.filter((link) => {
        const sourceItem = findItemById(link.sourceId);
        const targetItem = findItemById(link.targetId);
        return sourceItem?.projectId === projectId || targetItem?.projectId === projectId;
      });
    }
    const total = links.length;
    const paginatedLinks = links.slice(offset, offset + limit);
    // API returns { total: number, links: Link[] }
    return HttpResponse.json({ links: paginatedLinks, total });
  }),

  http.get(`${API_BASE}/api/v1/links/:id`, async ({ params }) => {
    await delay();
    const { id } = params;
    const link = findLinkById(id as string);

    if (!link) {
      return HttpResponse.json({ error: 'Link not found' }, { status: 404 });
    }

    return HttpResponse.json(link);
  }),

  http.post(`${API_BASE}/api/v1/links`, async ({ request }) => {
    await delay();
    const body = (await request.json()) as CreateLinkInput;

    // Get source item to determine projectId
    const sourceItem = findItemById(body.sourceId);
    const projectId = sourceItem?.projectId ?? 'unknown';

    const now = new Date().toISOString();
    const newLink: Link = {
      id: generateLinkId(),
      projectId: projectId,
      sourceId: body.sourceId,
      targetId: body.targetId,
      type: body.type,
      ...(body.description !== undefined && { description: body.description }),
      createdAt: now,
      updatedAt: now,
      version: 1,
    };

    mockLinks.push(newLink);
    return HttpResponse.json(newLink, { status: 201 });
  }),

  http.put(`${API_BASE}/api/v1/links/:id`, async ({ params, request }) => {
    await delay();
    const { id } = params;
    const body = (await request.json()) as UpdateLinkInput;
    const linkIndex = mockLinks.findIndex((l) => l.id === id);

    if (linkIndex === -1) {
      return HttpResponse.json({ error: 'Link not found' }, { status: 404 });
    }

    const baseLink = mockLinks[linkIndex]!;
    const updatedLink: Link = {
      id: baseLink.id,
      projectId: baseLink.projectId,
      sourceId: baseLink.sourceId,
      targetId: baseLink.targetId,
      type: body.type ?? baseLink.type,
      ...(body.description !== undefined && { description: body.description }),
      createdAt: baseLink.createdAt,
      updatedAt: new Date().toISOString(),
      version: (baseLink.version ?? 1) + 1,
    };

    mockLinks[linkIndex] = updatedLink;
    return HttpResponse.json(updatedLink);
  }),

  http.delete(`${API_BASE}/api/v1/links/:id`, async ({ params }) => {
    await delay();
    const { id } = params;
    const linkIndex = mockLinks.findIndex((l) => l.id === id);

    if (linkIndex === -1) {
      return HttpResponse.json({ error: 'Link not found' }, { status: 404 });
    }

    mockLinks.splice(linkIndex, 1);
    return HttpResponse.json(null, { status: 204 });
  }),

  // ============================================================================
  // GRAPH ENDPOINTS
  // ============================================================================
  http.get(`${API_BASE}/api/v1/graph/full`, async ({ request }) => {
    await delay();
    const url = new URL(request.url);
    const projectId = url.searchParams.get('project_id');

    const items = projectId ? filterItemsByProject(projectId) : mockItems;
    const nodes = items.map((item) => ({
      id: item.id,
      status: item.status,
      title: item.title,
      type: item.type,
      ...(item.metadata !== undefined && { metadata: item.metadata }),
    }));

    const edges = mockLinks.map((link) => ({
      id: link.id,
      source: link.sourceId,
      target: link.targetId,
      type: link.type,
    }));

    const graphData: GraphData = { edges, nodes };
    return HttpResponse.json(graphData);
  }),

  http.get(`${API_BASE}/api/v1/graph/impact/:id`, async ({ params }) => {
    await delay();
    const { id } = params;
    const item = findItemById(id as string);

    if (!item) {
      return HttpResponse.json({ error: 'Item not found' }, { status: 404 });
    }

    const affectedLinks = filterLinksByTarget(id as string);
    const affectedItems = affectedLinks
      .map((link) => findItemById(link.sourceId))
      .filter(Boolean) as Item[];

    const impactAnalysis: ImpactAnalysis = {
      affectedCount: affectedItems.length,
      affectedItems: affectedItems,
      depth: 1,
      itemId: id as string,
    };

    return HttpResponse.json(impactAnalysis);
  }),

  http.get(`${API_BASE}/api/v1/graph/dependencies/:id`, async ({ params }) => {
    await delay();
    const { id } = params;
    const item = findItemById(id as string);

    if (!item) {
      return HttpResponse.json({ error: 'Item not found' }, { status: 404 });
    }

    const dependencyLinks = filterLinksBySource(id as string);
    const dependencies = dependencyLinks
      .map((link) => findItemById(link.targetId))
      .filter(Boolean) as Item[];

    const dependencyAnalysis: DependencyAnalysis = {
      dependencies,
      dependencyCount: dependencies.length,
      depth: 1,
      itemId: id as string,
    };

    return HttpResponse.json(dependencyAnalysis);
  }),

  // ============================================================================
  // SYNC STATUS ENDPOINT
  // ============================================================================
  http.get(`${API_BASE}/api/v1/sync/status`, async () => {
    await delay();
    return HttpResponse.json({
      last_sync: new Date().toISOString(),
      pending_changes: 0,
      status: 'synced',
    });
  }),
];
