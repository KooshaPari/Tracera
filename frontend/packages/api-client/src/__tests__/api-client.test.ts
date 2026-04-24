import createClient from 'openapi-fetch';
import { beforeEach, describe, expect, expectTypeOf, it, vi } from 'vitest';

import {
  api,
  createItem,
  createLink,
  createProject,
  getItems,
  getLinks,
  getProject,
  getProjects,
} from '../api-client';

// Use vi.hoisted so the mock fns are available inside the hoisted vi.mock factory
const { mockGET, mockPOST } = vi.hoisted(() => ({
  mockGET: vi.fn(),
  mockPOST: vi.fn(),
}));

vi.mock(import('openapi-fetch'), () => ({
  default: vi.fn(() => ({
    GET: mockGET,
    POST: mockPOST,
  })),
}));

// ---------------------------------------------------------------------------
// Test data fixtures
// ---------------------------------------------------------------------------

const mockProject = {
  id: 'proj-1',
  name: 'Test Project',
  description: 'A test project',
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-01-01T00:00:00Z',
};

const mockItem = {
  id: 'item-1',
  projectId: 'proj-1',
  view: 'feature' as const,
  type: 'requirement',
  title: 'Test Item',
  status: 'todo' as const,
  priority: 'medium' as const,
  version: 1,
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-01-01T00:00:00Z',
};

const mockLink = {
  id: 'link-1',
  projectId: 'proj-1',
  sourceId: 'item-1',
  targetId: 'item-2',
  type: 'implements' as const,
  version: 1,
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-01-01T00:00:00Z',
};

// ---------------------------------------------------------------------------
// Tests: Module-level configuration
// ---------------------------------------------------------------------------

describe('API Client Configuration', () => {
  it('should call createClient with the default base URL', () => {
    expect(createClient).toHaveBeenCalledWith({
      baseUrl: 'http://localhost:4000',
    });
  });

  it('should export the api client instance', () => {
    expect(api).toBeDefined();
    expect(api.GET).toBeDefined();
    expect(api.POST).toBeDefined();
  });

  it('should expose GET and POST methods on the api object', () => {
    expectTypeOf(api.GET).toBeFunction();
    expectTypeOf(api.POST).toBeFunction();
  });
});

// ---------------------------------------------------------------------------
// Tests: getProjects
// ---------------------------------------------------------------------------

describe('getProjects()', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call api.GET with the projects endpoint', async () => {
    mockGET.mockResolvedValueOnce({ data: [mockProject], error: undefined });

    await getProjects();

    expect(mockGET).toHaveBeenCalledWith('/api/v1/projects');
  });

  it('should return the data on success', async () => {
    const projects = [mockProject, { ...mockProject, id: 'proj-2', name: 'Second' }];
    mockGET.mockResolvedValueOnce({ data: projects, error: undefined });

    const result = await getProjects();

    expect(result).toEqual(projects);
  });

  it('should return an empty array when API returns empty list', async () => {
    mockGET.mockResolvedValueOnce({ data: [], error: undefined });

    const result = await getProjects();

    expect(result).toEqual([]);
  });

  it('should throw when API returns an error', async () => {
    const apiError = { code: 'INTERNAL', message: 'Server exploded' };
    mockGET.mockResolvedValueOnce({ data: undefined, error: apiError });

    await expect(getProjects()).rejects.toEqual(apiError);
  });

  it('should throw the error object as-is without wrapping', async () => {
    const errorString = 'raw string error';
    mockGET.mockResolvedValueOnce({ data: undefined, error: errorString });

    await expect(getProjects()).rejects.toBe(errorString);
  });
});

// ---------------------------------------------------------------------------
// Tests: getProject
// ---------------------------------------------------------------------------

describe('getProject()', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call api.GET with the project path and id parameter', async () => {
    mockGET.mockResolvedValueOnce({ data: mockProject, error: undefined });

    await getProject('proj-1');

    expect(mockGET).toHaveBeenCalledWith('/api/v1/projects/{id}', {
      params: { path: { id: 'proj-1' } },
    });
  });

  it('should return the project data on success', async () => {
    mockGET.mockResolvedValueOnce({ data: mockProject, error: undefined });

    const result = await getProject('proj-1');

    expect(result).toEqual(mockProject);
  });

  it('should pass through arbitrary string IDs', async () => {
    mockGET.mockResolvedValueOnce({ data: mockProject, error: undefined });

    await getProject('some-uuid-v4-here');

    expect(mockGET).toHaveBeenCalledWith('/api/v1/projects/{id}', {
      params: { path: { id: 'some-uuid-v4-here' } },
    });
  });

  it('should throw when API returns a 404 error', async () => {
    const notFoundError = { code: 'NOT_FOUND', message: 'Project not found' };
    mockGET.mockResolvedValueOnce({ data: undefined, error: notFoundError });

    await expect(getProject('nonexistent')).rejects.toEqual(notFoundError);
  });

  it('should throw when API returns a 500 error', async () => {
    const serverError = { code: 'INTERNAL', message: 'Database connection failed' };
    mockGET.mockResolvedValueOnce({ data: undefined, error: serverError });

    await expect(getProject('proj-1')).rejects.toEqual(serverError);
  });
});

// ---------------------------------------------------------------------------
// Tests: createProject
// ---------------------------------------------------------------------------

describe('createProject()', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call api.POST with the projects endpoint and body', async () => {
    mockPOST.mockResolvedValueOnce({ data: mockProject, error: undefined });

    const input = { name: 'Test Project', description: 'A test project' };
    await createProject(input);

    expect(mockPOST).toHaveBeenCalledWith('/api/v1/projects', { body: input });
  });

  it('should return the created project on success', async () => {
    mockPOST.mockResolvedValueOnce({ data: mockProject, error: undefined });

    const result = await createProject({ name: 'Test Project' });

    expect(result).toEqual(mockProject);
  });

  it('should handle partial project input with only name', async () => {
    mockPOST.mockResolvedValueOnce({ data: mockProject, error: undefined });

    await createProject({ name: 'Minimal' });

    expect(mockPOST).toHaveBeenCalledWith('/api/v1/projects', {
      body: { name: 'Minimal' },
    });
  });

  it('should throw when API returns a validation error', async () => {
    const validationError = {
      code: 'VALIDATION',
      message: 'Name is required',
      details: { field: 'name' },
    };
    mockPOST.mockResolvedValueOnce({ data: undefined, error: validationError });

    await expect(createProject({})).rejects.toEqual(validationError);
  });

  it('should pass metadata through to the API', async () => {
    mockPOST.mockResolvedValueOnce({ data: mockProject, error: undefined });

    const input = { name: 'With Meta', metadata: { team: 'alpha' } };
    await createProject(input);

    expect(mockPOST).toHaveBeenCalledWith('/api/v1/projects', { body: input });
  });
});

// ---------------------------------------------------------------------------
// Tests: getItems
// ---------------------------------------------------------------------------

describe('getItems()', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call api.GET with the items endpoint', async () => {
    mockGET.mockResolvedValueOnce({ data: [mockItem], error: undefined });

    await getItems();

    expect(mockGET).toHaveBeenCalledWith('/api/v1/items');
  });

  it('should return items array on success', async () => {
    const items = [mockItem];
    mockGET.mockResolvedValueOnce({ data: items, error: undefined });

    const result = await getItems();

    expect(result).toEqual(items);
  });

  it('should return empty array when no items exist', async () => {
    mockGET.mockResolvedValueOnce({ data: [], error: undefined });

    const result = await getItems();

    expect(result).toEqual([]);
  });

  it('should throw when API returns an error', async () => {
    const error = { code: 'FORBIDDEN', message: 'Not authorized' };
    mockGET.mockResolvedValueOnce({ data: undefined, error });

    await expect(getItems()).rejects.toEqual(error);
  });
});

// ---------------------------------------------------------------------------
// Tests: createItem
// ---------------------------------------------------------------------------

describe('createItem()', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call api.POST with the items endpoint and body', async () => {
    mockPOST.mockResolvedValueOnce({ data: mockItem, error: undefined });

    const input = { title: 'Test Item', projectId: 'proj-1' };
    await createItem(input);

    expect(mockPOST).toHaveBeenCalledWith('/api/v1/items', { body: input });
  });

  it('should return the created item on success', async () => {
    mockPOST.mockResolvedValueOnce({ data: mockItem, error: undefined });

    const result = await createItem({ title: 'Test Item' });

    expect(result).toEqual(mockItem);
  });

  it('should throw when API returns an error', async () => {
    const error = { code: 'CONFLICT', message: 'Duplicate item' };
    mockPOST.mockResolvedValueOnce({ data: undefined, error });

    await expect(createItem({ title: 'Dup' })).rejects.toEqual(error);
  });

  it('should handle item input with all fields', async () => {
    const fullItem = {
      projectId: 'proj-1',
      view: 'feature' as const,
      type: 'requirement',
      title: 'Full Item',
      description: 'Complete description',
      status: 'todo' as const,
      priority: 'high' as const,
    };
    mockPOST.mockResolvedValueOnce({ data: { ...mockItem, ...fullItem }, error: undefined });

    await createItem(fullItem);

    expect(mockPOST).toHaveBeenCalledWith('/api/v1/items', { body: fullItem });
  });
});

// ---------------------------------------------------------------------------
// Tests: getLinks
// ---------------------------------------------------------------------------

describe('getLinks()', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call api.GET with the links endpoint', async () => {
    mockGET.mockResolvedValueOnce({ data: [mockLink], error: undefined });

    await getLinks();

    expect(mockGET).toHaveBeenCalledWith('/api/v1/links');
  });

  it('should return links array on success', async () => {
    const links = [mockLink];
    mockGET.mockResolvedValueOnce({ data: links, error: undefined });

    const result = await getLinks();

    expect(result).toEqual(links);
  });

  it('should throw when API returns an error', async () => {
    const error = { code: 'UNAUTHORIZED', message: 'Token expired' };
    mockGET.mockResolvedValueOnce({ data: undefined, error });

    await expect(getLinks()).rejects.toEqual(error);
  });
});

// ---------------------------------------------------------------------------
// Tests: createLink
// ---------------------------------------------------------------------------

describe('createLink()', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call api.POST with the links endpoint and body', async () => {
    mockPOST.mockResolvedValueOnce({ data: mockLink, error: undefined });

    const input = { sourceId: 'item-1', targetId: 'item-2', type: 'implements' as const };
    await createLink(input);

    expect(mockPOST).toHaveBeenCalledWith('/api/v1/links', { body: input });
  });

  it('should return the created link on success', async () => {
    mockPOST.mockResolvedValueOnce({ data: mockLink, error: undefined });

    const result = await createLink({
      sourceId: 'item-1',
      targetId: 'item-2',
      type: 'implements' as const,
    });

    expect(result).toEqual(mockLink);
  });

  it('should throw when API returns an error', async () => {
    const error = { code: 'VALIDATION', message: 'Invalid link type' };
    mockPOST.mockResolvedValueOnce({ data: undefined, error });

    await expect(createLink({ sourceId: 'a', targetId: 'b' })).rejects.toEqual(error);
  });

  it('should handle link input with description and metadata', async () => {
    const input = {
      sourceId: 'item-1',
      targetId: 'item-2',
      type: 'related_to' as const,
      description: 'These items are related',
      metadata: { confidence: 0.9 },
    };
    mockPOST.mockResolvedValueOnce({ data: { ...mockLink, ...input }, error: undefined });

    await createLink(input);

    expect(mockPOST).toHaveBeenCalledWith('/api/v1/links', { body: input });
  });
});

// ---------------------------------------------------------------------------
// Tests: Error handling edge cases
// ---------------------------------------------------------------------------

describe('Error handling edge cases', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should propagate non-object errors from GET endpoints', async () => {
    mockGET.mockResolvedValueOnce({ data: undefined, error: 'plain string error' });

    await expect(getProjects()).rejects.toBe('plain string error');
  });

  it('should propagate numeric errors from GET endpoints', async () => {
    mockGET.mockResolvedValueOnce({ data: undefined, error: 500 });

    await expect(getItems()).rejects.toBe(500);
  });

  it('should propagate non-object errors from POST endpoints', async () => {
    mockPOST.mockResolvedValueOnce({ data: undefined, error: 'creation failed' });

    await expect(createProject({ name: 'test' })).rejects.toBe('creation failed');
  });

  it('should treat falsy error (null) as no error when data is present', async () => {
    // When error is null/undefined/0/false, the `if (error)` check is false
    mockGET.mockResolvedValueOnce({ data: [mockProject], error: null });

    const result = await getProjects();

    expect(result).toEqual([mockProject]);
  });

  it('should treat empty string error as no error (falsy)', async () => {
    mockGET.mockResolvedValueOnce({ data: [mockItem], error: '' });

    const result = await getItems();

    expect(result).toEqual([mockItem]);
  });

  it('should treat false error as no error (falsy)', async () => {
    mockGET.mockResolvedValueOnce({ data: mockProject, error: false });

    const result = await getProject('proj-1');

    expect(result).toEqual(mockProject);
  });

  it('should return undefined data when no error but data is undefined', async () => {
    // If error is falsy and data is undefined, the function returns undefined
    mockGET.mockResolvedValueOnce({ data: undefined, error: undefined });

    const result = await getProjects();

    expect(result).toBeUndefined();
  });

  it('should throw error objects with extra detail fields', async () => {
    const detailedError = {
      code: 'RATE_LIMITED',
      message: 'Too many requests',
      details: { retryAfter: 30, limit: 100 },
    };
    mockGET.mockResolvedValueOnce({ data: undefined, error: detailedError });

    await expect(getLinks()).rejects.toEqual(detailedError);
  });
});

// ---------------------------------------------------------------------------
// Tests: Verify correct endpoint routing
// ---------------------------------------------------------------------------

describe('Endpoint routing', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should use GET for all read operations', async () => {
    mockGET.mockResolvedValue({ data: [], error: undefined });

    await getProjects();
    await getItems();
    await getLinks();

    expect(mockGET).toHaveBeenCalledTimes(3);
    expect(mockPOST).not.toHaveBeenCalled();
  });

  it('should use GET with path params for single resource', async () => {
    mockGET.mockResolvedValue({ data: mockProject, error: undefined });

    await getProject('abc-123');

    expect(mockGET).toHaveBeenCalledWith('/api/v1/projects/{id}', {
      params: { path: { id: 'abc-123' } },
    });
  });

  it('should use POST for all create operations', async () => {
    mockPOST.mockResolvedValue({ data: {}, error: undefined });

    await createProject({ name: 'p' });
    await createItem({ title: 'i' });
    await createLink({ sourceId: 's', targetId: 't' });

    expect(mockPOST).toHaveBeenCalledTimes(3);
    expect(mockGET).not.toHaveBeenCalled();
  });

  it('should call correct endpoints for each create function', async () => {
    mockPOST.mockResolvedValue({ data: {}, error: undefined });

    await createProject({ name: 'p' });
    await createItem({ title: 'i' });
    await createLink({ sourceId: 's', targetId: 't' });

    expect(mockPOST).toHaveBeenNthCalledWith(1, '/api/v1/projects', { body: { name: 'p' } });
    expect(mockPOST).toHaveBeenNthCalledWith(2, '/api/v1/items', { body: { title: 'i' } });
    expect(mockPOST).toHaveBeenNthCalledWith(3, '/api/v1/links', {
      body: { sourceId: 's', targetId: 't' },
    });
  });
});
