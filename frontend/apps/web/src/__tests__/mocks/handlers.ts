/**
 * MSW request handlers for API mocking
 */

import { HttpResponse, http } from 'msw'
import {
  createMockItem,
  createMockLink,
  createMockProject,
  mockAgents,
  mockGraphData,
  mockItems,
  mockLinks,
  mockProjects,
  mockSearchResult,
} from './data'

const API_BASE = 'http://localhost:8000/api/v1'

export const handlers = [
  // Projects
  http.get(`${API_BASE}/projects`, () => {
    return HttpResponse.json(mockProjects)
  }),

  http.get(`${API_BASE}/projects/:id`, ({ params }) => {
    const project = mockProjects.find((p) => p.id === params.id)
    if (!project) {
      return new HttpResponse(null, { status: 404 })
    }
    return HttpResponse.json(project)
  }),

  http.post(`${API_BASE}/projects`, async ({ request }) => {
    const body = await request.json()
    const newProject = createMockProject(body as any)
    return HttpResponse.json(newProject, { status: 201 })
  }),

  http.patch(`${API_BASE}/projects/:id`, async ({ params, request }) => {
    const body = await request.json()
    const project = mockProjects.find((p) => p.id === params.id)
    if (!project) {
      return new HttpResponse(null, { status: 404 })
    }
    const updated = { ...project, ...(body as object), updated_at: new Date().toISOString() }
    return HttpResponse.json(updated)
  }),

  http.delete(`${API_BASE}/projects/:id`, ({ params }) => {
    const project = mockProjects.find((p) => p.id === params.id)
    if (!project) {
      return new HttpResponse(null, { status: 404 })
    }
    return new HttpResponse(null, { status: 204 })
  }),

  // Items
  http.get(`${API_BASE}/items`, ({ request }) => {
    const url = new URL(request.url)
    const projectId = url.searchParams.get('project_id')

    let items = mockItems
    if (projectId) {
      items = items.filter((item) => item.project_id === projectId)
    }

    return HttpResponse.json(items)
  }),

  http.get(`${API_BASE}/items/:id`, ({ params }) => {
    const item = mockItems.find((i) => i.id === params.id)
    if (!item) {
      return new HttpResponse(null, { status: 404 })
    }
    return HttpResponse.json(item)
  }),

  http.post(`${API_BASE}/items`, async ({ request }) => {
    const body = await request.json()
    const newItem = createMockItem(body as any)
    return HttpResponse.json(newItem, { status: 201 })
  }),

  http.patch(`${API_BASE}/items/:id`, async ({ params, request }) => {
    const body = await request.json()
    const item = mockItems.find((i) => i.id === params.id)
    if (!item) {
      return new HttpResponse(null, { status: 404 })
    }
    const updated = { ...item, ...(body as object), updated_at: new Date().toISOString() }
    return HttpResponse.json(updated)
  }),

  http.delete(`${API_BASE}/items/:id`, ({ params }) => {
    const item = mockItems.find((i) => i.id === params.id)
    if (!item) {
      return new HttpResponse(null, { status: 404 })
    }
    return new HttpResponse(null, { status: 204 })
  }),

  // Links
  http.get(`${API_BASE}/links`, ({ request }) => {
    const url = new URL(request.url)
    const itemId = url.searchParams.get('item_id')

    let links = mockLinks
    if (itemId) {
      links = links.filter((link) => link.source_id === itemId || link.target_id === itemId)
    }

    return HttpResponse.json(links)
  }),

  http.get(`${API_BASE}/links/:id`, ({ params }) => {
    const link = mockLinks.find((l) => l.id === params.id)
    if (!link) {
      return new HttpResponse(null, { status: 404 })
    }
    return HttpResponse.json(link)
  }),

  http.post(`${API_BASE}/links`, async ({ request }) => {
    const body = await request.json()
    const newLink = createMockLink(body as any)
    return HttpResponse.json(newLink, { status: 201 })
  }),

  http.delete(`${API_BASE}/links/:id`, ({ params }) => {
    const link = mockLinks.find((l) => l.id === params.id)
    if (!link) {
      return new HttpResponse(null, { status: 404 })
    }
    return new HttpResponse(null, { status: 204 })
  }),

  // Graph
  http.get(`${API_BASE}/graph/:projectId`, () => {
    return HttpResponse.json(mockGraphData)
  }),

  // Search
  http.get(`${API_BASE}/search`, ({ request }) => {
    const url = new URL(request.url)
    const query = url.searchParams.get('q')

    return HttpResponse.json({
      ...mockSearchResult,
      query: query || '',
    })
  }),

  // Agents
  http.get(`${API_BASE}/agents`, () => {
    return HttpResponse.json(mockAgents)
  }),

  http.get(`${API_BASE}/agents/:id`, ({ params }) => {
    const agent = mockAgents.find((a) => a.id === params.id)
    if (!agent) {
      return new HttpResponse(null, { status: 404 })
    }
    return HttpResponse.json(agent)
  }),

  // Impact Analysis
  http.get(`${API_BASE}/items/:id/impact`, ({ params }) => {
    return HttpResponse.json({
      item_id: params.id,
      affected_items: mockItems.slice(0, 2),
      affected_count: 2,
      depth: 1,
    })
  }),

  // Dependency Analysis
  http.get(`${API_BASE}/items/:id/dependencies`, ({ params }) => {
    return HttpResponse.json({
      item_id: params.id,
      dependencies: mockItems.slice(0, 1),
      dependency_count: 1,
      depth: 1,
    })
  }),

  // Traceability Matrix
  http.get(`${API_BASE}/traceability/:projectId`, () => {
    return HttpResponse.json({
      requirements: mockItems.filter((i) => i.type === 'requirement'),
      coverage: {
        'item-2': {
          implemented_by: [mockItems[0]],
          tested_by: [mockItems[2]],
          documented_by: [],
          coverage_percentage: 66,
        },
      },
    })
  }),

  // Auth
  http.post(`${API_BASE}/auth/login`, async ({ request }) => {
    const body = (await request.json()) as any
    return HttpResponse.json({
      user: {
        id: 'user-1',
        email: body.email,
        name: body.email.split('@')[0],
      },
      token: 'mock-jwt-token',
    })
  }),

  http.post(`${API_BASE}/auth/logout`, () => {
    return new HttpResponse(null, { status: 204 })
  }),

  http.post(`${API_BASE}/auth/refresh`, () => {
    return HttpResponse.json({
      token: 'new-mock-jwt-token',
    })
  }),

  // Dashboard stats
  http.get(`${API_BASE}/dashboard/stats`, () => {
    return HttpResponse.json({
      total_projects: 2,
      total_items: 3,
      total_links: 2,
      items_by_status: {
        pending: 1,
        in_progress: 1,
        completed: 1,
      },
      items_by_type: {
        feature: 1,
        requirement: 1,
        test: 1,
      },
      recent_activity: [
        {
          id: 'activity-1',
          type: 'item_created',
          timestamp: '2025-01-01T00:00:00Z',
          data: { item_id: 'item-1' },
        },
      ],
    })
  }),

  // Health check
  http.get(`${API_BASE}/health`, () => {
    return HttpResponse.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
    })
  }),
]
