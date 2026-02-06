import { HttpResponse, http } from 'msw';

import { mockItems, mockLinks, mockProjects } from './data';

const API_BASE = 'http://localhost:4000';

export const handlers = [
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
