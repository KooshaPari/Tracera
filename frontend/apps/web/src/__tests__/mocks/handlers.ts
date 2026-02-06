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
];
