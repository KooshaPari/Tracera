import type { Page, Route } from '@playwright/test';

/**
 * Mock API data for E2E tests
 */
export const mockProjects = [
  {
    createdAt: new Date().toISOString(),
    description: 'Desktop App + Website for traceability management',
    id: '1',
    name: 'TraceRTM Frontend',
    status: 'active',
    updatedAt: new Date().toISOString(),
  },
  {
    createdAt: new Date().toISOString(),
    description: 'Demo project for testing',
    id: '2',
    name: 'Pokemon Go Demo',
    status: 'active',
    updatedAt: new Date().toISOString(),
  },
  {
    createdAt: new Date().toISOString(),
    description: 'Online shopping application',
    id: '3',
    name: 'E-Commerce Platform',
    status: 'active',
    updatedAt: new Date().toISOString(),
  },
];

export const mockItems = [
  {
    createdAt: new Date().toISOString(),
    description: 'Implement user login and registration',
    id: 'item-1',
    priority: 'high',
    projectId: '1',
    status: 'in_progress',
    title: 'User Authentication',
    type: 'requirement',
    updatedAt: new Date().toISOString(),
    version: 1,
    view: 'Feature',
  },
  {
    createdAt: new Date().toISOString(),
    description: 'Create main dashboard with metrics',
    id: 'item-2',
    priority: 'medium',
    projectId: '1',
    status: 'todo',
    title: 'Dashboard View',
    type: 'feature',
    updatedAt: new Date().toISOString(),
    version: 1,
    view: 'Feature',
  },
  {
    createdAt: new Date().toISOString(),
    description: 'Connect to backend services',
    id: 'item-3',
    priority: 'high',
    projectId: '1',
    status: 'done',
    title: 'API Integration',
    type: 'requirement',
    updatedAt: new Date().toISOString(),
    version: 1,
    view: 'Code',
  },
  {
    createdAt: new Date().toISOString(),
    description: 'Write comprehensive unit tests',
    id: 'item-4',
    priority: 'medium',
    projectId: '1',
    status: 'in_progress',
    title: 'Unit Tests',
    type: 'test',
    updatedAt: new Date().toISOString(),
    version: 1,
    view: 'Test',
  },
];

export const mockAgents = [
  {
    capabilities: ['sync', 'dependency-check'],
    id: 'agent-1',
    lastRun: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
    name: 'Sync Agent',
    status: 'active',
    tasksCompleted: 24,
    type: 'sync',
  },
  {
    capabilities: ['validation', 'quality-checks'],
    id: 'agent-2',
    lastRun: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    name: 'Validation Agent',
    status: 'idle',
    tasksCompleted: 12,
    type: 'validator',
  },
  {
    capabilities: ['coverage-report', 'test-execution'],
    id: 'agent-3',
    lastRun: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    name: 'Coverage Agent',
    status: 'running',
    tasksCompleted: 7,
    type: 'coverage',
  },
];

export const mockLinks = [
  {
    createdAt: new Date().toISOString(),
    id: 'link-1',
    sourceId: 'item-1',
    targetId: 'item-2',
    type: 'depends_on',
  },
  {
    createdAt: new Date().toISOString(),
    id: 'link-2',
    sourceId: 'item-3',
    targetId: 'item-4',
    type: 'tests',
  },
];

export const mockSystemStatus = {
  activeAgents: 2,
  queuedJobs: 5,
  status: 'healthy',
  uptime: 99.9,
};

/**
 * Setup API route mocking for E2E tests
 * Uses a single route handler with URL parsing for reliable interception
 */
export async function setupApiMocks(page: Page): Promise<void> {
  const apiUrls = ['http://localhost:4000', 'http://127.0.0.1:4000', 'http://127.0.0.1:8080'];

  // Single comprehensive route handler for all API calls
  const handler = async (route: Route) => {
    const url = route.request().url();
    const method = route.request().method();
    const { pathname } = new URL(url);

    // Health endpoint
    if (pathname === '/health' || pathname === '/api/v1/health') {
      await route.fulfill({
        body: JSON.stringify({ status: 'healthy' }),
        contentType: 'application/json',
        status: 200,
      });
      return;
    }

    // CSRF token
    if (pathname === '/api/v1/csrf-token') {
      await route.fulfill({
        body: JSON.stringify({ token: 'csrf-test-token' }),
        contentType: 'application/json',
        status: 200,
      });
      return;
    }

    // Auth endpoints
    if (pathname === '/api/v1/auth/login' && method === 'POST') {
      await route.fulfill({
        body: JSON.stringify({
          access_token: 'test-token',
          user: {
            email: 'test@example.com',
            id: 'test-user',
            name: 'Test User',
          },
        }),
        contentType: 'application/json',
        status: 200,
      });
      return;
    }
    if (pathname === '/api/v1/auth/logout' && method === 'POST') {
      await route.fulfill({
        body: JSON.stringify({ status: 'ok' }),
        contentType: 'application/json',
        status: 200,
      });
      return;
    }
    if (pathname === '/api/v1/auth/me' && method === 'GET') {
      await route.fulfill({
        body: JSON.stringify({
          account: {
            account_type: 'personal',
            id: 'test-account',
            name: 'Test Account',
            slug: 'test-account',
          },
          accounts: [],
          user: {
            email: 'test@example.com',
            id: 'test-user',
            name: 'Test User',
          },
        }),
        contentType: 'application/json',
        status: 200,
      });
      return;
    }

    // MCP endpoints
    if (pathname === '/api/v1/mcp/health') {
      await route.fulfill({
        body: JSON.stringify({ service: 'mcp', status: 'ok' }),
        contentType: 'application/json',
        status: 200,
      });
      return;
    }
    if (pathname === '/api/v1/mcp/config') {
      await route.fulfill({
        body: JSON.stringify({
          auth_mode: 'oauth',
          mcp_base_url: 'http://localhost:4000/api/v1/mcp',
          requires_auth: true,
        }),
        contentType: 'application/json',
        status: 200,
      });
      return;
    }

    // Projects endpoints
    if (pathname.startsWith('/api/v1/projects')) {
      if (method === 'GET') {
        if (pathname !== '/api/v1/projects' && pathname.includes('/projects/')) {
          // Single project
          const projectId = pathname.split('/projects/')[1]?.split('/')[0];
          const project = mockProjects.find((p) => p.id === projectId);
          await route.fulfill({
            body: JSON.stringify(project ?? { error: 'Not found' }),
            contentType: 'application/json',
            status: project ? 200 : 404,
          });
        } else {
          // List projects
          await route.fulfill({
            body: JSON.stringify(mockProjects),
            contentType: 'application/json',
            status: 200,
          });
        }
      } else if (method === 'POST') {
        const body = route.request().postDataJSON();
        const newProject = {
          id: `proj-${Date.now()}`,
          ...body,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        await route.fulfill({
          body: JSON.stringify(newProject),
          contentType: 'application/json',
          status: 201,
        });
      } else {
        await route.fulfill({
          body: JSON.stringify({}),
          contentType: 'application/json',
          status: 200,
        });
      }
      return;
    }

    // Items endpoints
    if (pathname.startsWith('/api/v1/items')) {
      if (method === 'GET') {
        if (pathname !== '/api/v1/items' && pathname.includes('/items/')) {
          // Single item
          const itemId = pathname.split('/items/')[1]?.split('/')[0];
          const item = mockItems.find((i) => i.id === itemId);
          await route.fulfill({
            body: JSON.stringify(item ?? { error: 'Not found' }),
            contentType: 'application/json',
            status: item ? 200 : 404,
          });
        } else {
          // List items with optional filtering
          const urlParams = new URL(url).searchParams;
          const projectId = urlParams.get('project_id');
          let items = mockItems;
          if (projectId) {
            items = mockItems.filter((i) => i.projectId === projectId);
          }
          await route.fulfill({
            body: JSON.stringify({ items, total: items.length }),
            contentType: 'application/json',
            status: 200,
          });
        }
      } else if (method === 'POST') {
        const body = route.request().postDataJSON();
        const newItem = {
          id: `item-${Date.now()}`,
          ...body,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        await route.fulfill({
          body: JSON.stringify(newItem),
          contentType: 'application/json',
          status: 201,
        });
      } else {
        await route.fulfill({
          body: JSON.stringify({}),
          contentType: 'application/json',
          status: 200,
        });
      }
      return;
    }

    // Agents endpoints
    if (pathname.startsWith('/api/v1/agents')) {
      if (method === 'GET') {
        await route.fulfill({
          body: JSON.stringify({
            agents: mockAgents,
            total: mockAgents.length,
          }),
          contentType: 'application/json',
          status: 200,
        });
      } else {
        await route.fulfill({
          body: JSON.stringify({}),
          contentType: 'application/json',
          status: 200,
        });
      }
      return;
    }

    // Links endpoints
    if (pathname.startsWith('/api/v1/links')) {
      if (method === 'GET') {
        await route.fulfill({
          body: JSON.stringify(mockLinks),
          contentType: 'application/json',
          status: 200,
        });
      } else {
        await route.fulfill({
          body: JSON.stringify({}),
          contentType: 'application/json',
          status: 200,
        });
      }
      return;
    }

    // Graph endpoints
    if (pathname.startsWith('/api/v1/graph')) {
      await route.fulfill({
        body: JSON.stringify({
          edges: mockLinks.map((link) => ({
            id: link.id,
            source: link.sourceId,
            target: link.targetId,
            type: link.type,
          })),
          nodes: mockItems.map((item) => ({
            data: item,
            id: item.id,
            label: item.title,
            type: item.type,
          })),
        }),
        contentType: 'application/json',
        status: 200,
      });
      return;
    }

    // System status
    if (pathname.startsWith('/api/v1/system')) {
      await route.fulfill({
        body: JSON.stringify(mockSystemStatus),
        contentType: 'application/json',
        status: 200,
      });
      return;
    }

    // Search endpoint
    if (pathname.startsWith('/api/v1/search')) {
      const urlParams = new URL(url).searchParams;
      const query = urlParams.get('q') ?? '';

      const results = mockItems.filter(
        (item) =>
          item.title.toLowerCase().includes(query.toLowerCase()) ||
          item.description.toLowerCase().includes(query.toLowerCase()),
      );

      await route.fulfill({
        body: JSON.stringify({ results, total: results.length }),
        contentType: 'application/json',
        status: 200,
      });
      return;
    }

    // Events endpoint
    if (pathname.startsWith('/api/v1/events')) {
      await route.fulfill({
        body: JSON.stringify([
          {
            data: { itemId: 'item-1', title: 'User Authentication' },
            id: 'event-1',
            timestamp: new Date().toISOString(),
            type: 'item_created',
          },
        ]),
        contentType: 'application/json',
        status: 200,
      });
      return;
    }

    // Notifications endpoint
    if (pathname === '/api/v1/notifications' || pathname === '/api/v1/notifications/') {
      await route.fulfill({
        body: JSON.stringify([]),
        contentType: 'application/json',
        status: 200,
      });
      return;
    }

    // Default fallback for unhandled API routes
    console.log(`Unhandled API route: ${method} ${url}`);
    await route.fulfill({
      body: JSON.stringify({}),
      contentType: 'application/json',
      status: 200,
    });
  };

  for (const apiUrl of apiUrls) {
    await page.route(`${apiUrl}/**`, handler);
  }
}
