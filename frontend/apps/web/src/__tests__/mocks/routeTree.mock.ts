// Mock routeTree for tests
// Creates a minimal mock route tree that doesn't import actual route files

import { vi } from "vitest";

// Create mock route that has all necessary methods
const createMockRoute = (path: string, id: string = path) => ({
	id,
	path,
	getParentRoute: () => rootRoute,
	init: vi.fn().mockReturnValue({}),
	update: vi.fn().mockReturnThis(),
	addChildren: vi.fn().mockReturnThis(),
	_addFileChildren: vi.fn().mockReturnThis(),
	_addFileTypes: vi.fn().mockReturnThis(),
	useMatch: vi.fn(),
	useRouteContext: vi.fn(),
	useSearch: vi.fn(),
	useParams: vi.fn(),
	options: {},
	fullPath: path,
	to: path,
});

// Root route mock
export const rootRoute = {
	id: "__root__",
	path: "/",
	getParentRoute: () => undefined,
	init: vi.fn().mockReturnValue({}),
	update: vi.fn().mockReturnThis(),
	addChildren: vi.fn().mockReturnThis(),
	_addFileChildren: vi.fn().mockReturnThis(),
	_addFileTypes: vi.fn().mockReturnThis(),
	useMatch: vi.fn(),
	useRouteContext: vi.fn(),
	useSearch: vi.fn(),
	useParams: vi.fn(),
	options: {
		component: () => null,
	},
	fullPath: "/",
	to: "/",
	children: [],
};

// Create child routes
const indexRoute = createMockRoute("/", "/");
const projectsRoute = createMockRoute("/projects/", "/projects/");
const projectDetailRoute = createMockRoute(
	"/projects/$projectId",
	"/projects/$projectId",
);
const settingsRoute = createMockRoute("/settings/", "/settings/");
const searchRoute = createMockRoute("/search/", "/search/");
const reportsRoute = createMockRoute("/reports/", "/reports/");
const linksRoute = createMockRoute("/links/", "/links/");
const itemsRoute = createMockRoute("/items/", "/items/");
const graphRoute = createMockRoute("/graph/", "/graph/");

// Build the route tree
export const routeTree = rootRoute.addChildren([
	indexRoute,
	projectsRoute,
	projectDetailRoute,
	settingsRoute,
	searchRoute,
	reportsRoute,
	linksRoute,
	itemsRoute,
	graphRoute,
	eventsRoute,
]);

// Make routeTree have the same structure as a real route tree
Object.assign(routeTree, {
	init: vi.fn().mockReturnValue({}),
	__types: {},
});

// Export Route type mocks (for file-based routes)
export const Route = {
	init: vi.fn(),
	update: vi.fn().mockReturnThis(),
};
