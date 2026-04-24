import { HttpResponse, http } from 'msw';

import { mockItems, mockLinks, mockProjects } from './data';

const API_BASE = 'http://localhost:4000';

export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE}/api/v1/auth/login`, () =>
    HttpResponse.json({
      token: 'test-jwt-token-12345',
      user: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
      },
    }),
  ),
  http.post(`${API_BASE}/api/v1/auth/logout`, () => HttpResponse.json({ success: true })),
  http.post(`${API_BASE}/api/v1/auth/refresh`, () =>
    HttpResponse.json({
      token: 'test-jwt-token-refreshed',
    }),
  ),
  http.get(`${API_BASE}/api/v1/auth/user`, () =>
    HttpResponse.json({
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
    }),
  ),
  // Project and item endpoints
  http.get(`${API_BASE}/api/v1/projects`, () =>
    HttpResponse.json({
      projects: mockProjects,
      total: mockProjects.length,
    }),
  ),
  http.get(`${API_BASE}/api/v1/items`, () =>
    HttpResponse.json({
      items: mockItems,
      total: mockItems.length,
    }),
  ),
  http.get(`${API_BASE}/api/v1/links`, () =>
    HttpResponse.json({
      links: mockLinks,
      total: mockLinks.length,
    }),
  ),
  // Reports endpoints
  http.get(`${API_BASE}/api/v1/reports/templates`, () =>
    HttpResponse.json({
      templates: [
        {
          id: 'template-1',
          name: 'Traceability Report',
          description: 'Standard traceability analysis',
          fields: ['project', 'items', 'links', 'coverage'],
        },
        {
          id: 'template-2',
          name: 'Impact Analysis',
          description: 'Change impact assessment',
          fields: ['changes', 'affected_items', 'risk_level'],
        },
      ],
    }),
  ),
  http.post(`${API_BASE}/api/v1/reports/export`, () =>
    HttpResponse.json({
      exportId: 'export-12345',
      status: 'completed',
      url: 'https://example.com/reports/export-12345.pdf',
      createdAt: new Date().toISOString(),
    }),
  ),
  // Search endpoint
  http.get(`${API_BASE}/api/v1/search`, ({ request }) => {
    const url = new URL(request.url);
    const query = url.searchParams.get('q') ?? '';

    return HttpResponse.json({
      results: [
        {
          id: 'item-1',
          title: 'User Authentication',
          type: 'item',
          projectId: 'proj-1',
          highlight: query ? `User <mark>${query}</mark> Authentication` : 'User Authentication',
        },
        {
          id: 'item-2',
          title: 'Project Dashboard',
          type: 'item',
          projectId: 'proj-1',
          highlight: query ? `Project <mark>${query}</mark> Dashboard` : 'Project Dashboard',
        },
      ],
      total: 2,
    });
  }),
];
