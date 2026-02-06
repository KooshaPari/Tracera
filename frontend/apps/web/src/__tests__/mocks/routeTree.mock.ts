// Mock routeTree for tests
// Creates a minimal mock route tree that doesn't import actual route files

import { vi } from 'vitest';

// Create mock route that has all necessary methods
const createMockRoute = (path: string, id: string = path) => ({
  _addFileChildren: vi.fn().mockReturnThis(),
  _addFileTypes: vi.fn().mockReturnThis(),
  addChildren: vi.fn().mockReturnThis(),
  fullPath: path,
  getParentRoute: () => rootRoute,
  id,
  init: vi.fn().mockReturnValue({}),
  options: {},
  path,
  to: path,
  update: vi.fn().mockReturnThis(),
  useMatch: vi.fn(),
  useParams: vi.fn(),
  useRouteContext: vi.fn(),
  useSearch: vi.fn(),
});

// Root route mock
export const rootRoute = {
  _addFileChildren: vi.fn().mockReturnThis(),
  _addFileTypes: vi.fn().mockReturnThis(),
  addChildren: vi.fn().mockReturnThis(),
  children: [],
  fullPath: '/',
  getParentRoute: () => {},
  id: '__root__',
  init: vi.fn().mockReturnValue({}),
  options: {
    component: () => null,
  },
  path: '/',
  to: '/',
  update: vi.fn().mockReturnThis(),
  useMatch: vi.fn(),
  useParams: vi.fn(),
  useRouteContext: vi.fn(),
  useSearch: vi.fn(),
};

// Create child routes
const indexRoute = createMockRoute('/', '/');
const projectsRoute = createMockRoute('/projects/', '/projects/');
const projectDetailRoute = createMockRoute('/projects/$projectId', '/projects/$projectId');
const settingsRoute = createMockRoute('/settings/', '/settings/');

// Build the route tree
export const routeTree = rootRoute.addChildren([
  indexRoute,
  projectsRoute,
  projectDetailRoute,
  settingsRoute,
]);

// Make routeTree have the same structure as a real route tree
Object.assign(routeTree, {
  __types: {},
  init: vi.fn().mockReturnValue({}),
});

// Export Route type mocks (for file-based routes)
export const Route = {
  init: vi.fn(),
  update: vi.fn().mockReturnThis(),
};
