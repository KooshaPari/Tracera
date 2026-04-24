/**
 * Projects API Contract Tests
 *
 * Consumer: TraceRTM-Web
 * Provider: TraceRTM-API
 * Domain: Project Management
 */

import { describe, it, beforeAll, afterAll } from 'vitest';
import {
  createPactProvider,
  setupPact,
  teardownPact,
  like,
  eachLike,
  uuid,
  integer,
  iso8601DateTime,
  errorResponse,
  standardResponse,
  paginatedResponse,
  withAuth,
  providerStates,
  testData,
} from '../setup';

const provider = createPactProvider('TraceRTM-Web-Projects');

describe('Projects Contract Tests', () => {
  beforeAll(async () => {
    await setupPact(provider);
  });

  afterAll(async () => {
    await teardownPact(provider);
  });

  describe('GET /projects', () => {
    it('should return list of projects', async () => {
      await provider.addInteraction({
        states: [{ description: 'projects exist' }],
        uponReceiving: 'a request for projects list',
        withRequest: {
          method: 'GET',
          path: '/projects',
          query: {
            page: '1',
            pageSize: '20',
          },
          headers: withAuth(),
        },
        willRespondWith: paginatedResponse([testData.project]),
      });

      const response = await fetch('http://localhost:8080/projects?page=1&pageSize=20', {
        headers: { Authorization: 'Bearer test-token' },
      });

      const data = await response.json();
      console.assert(response.status === 200);
      console.assert(Array.isArray(data.items));
    });

    it('should return empty list when no projects', async () => {
      await provider.addInteraction({
        states: [{ description: providerStates.databaseEmpty }],
        uponReceiving: 'a request for projects when none exist',
        withRequest: {
          method: 'GET',
          path: '/projects',
          query: {
            page: '1',
            pageSize: '20',
          },
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          items: [],
          pagination: {
            page: integer(1),
            pageSize: integer(20),
            total: integer(0),
            totalPages: integer(0),
          },
        }),
      });

      const response = await fetch('http://localhost:8080/projects?page=1&pageSize=20', {
        headers: { Authorization: 'Bearer test-token' },
      });

      const data = await response.json();
      console.assert(data.items.length === 0);
    });
  });

  describe('POST /projects', () => {
    it('should create new project', async () => {
      await provider.addInteraction({
        states: [{ description: providerStates.userAuthenticated }],
        uponReceiving: 'a request to create project',
        withRequest: {
          method: 'POST',
          path: '/projects',
          headers: withAuth(),
          body: {
            name: 'New Project',
            description: 'Project description',
            status: 'active',
          },
        },
        willRespondWith: standardResponse(
          {
            ...testData.project,
            name: like('New Project'),
            description: like('Project description'),
          },
          201
        ),
      });

      const response = await fetch('http://localhost:8080/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify({
          name: 'New Project',
          description: 'Project description',
          status: 'active',
        }),
      });

      console.assert(response.status === 201);
    });

    it('should reject invalid project data', async () => {
      await provider.addInteraction({
        states: [{ description: providerStates.userAuthenticated }],
        uponReceiving: 'a request to create project with invalid data',
        withRequest: {
          method: 'POST',
          path: '/projects',
          headers: withAuth(),
          body: {
            name: '', // Invalid: empty name
          },
        },
        willRespondWith: errorResponse(
          'Validation error: name is required',
          'VALIDATION_ERROR',
          400
        ),
      });

      const response = await fetch('http://localhost:8080/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify({ name: '' }),
      });

      console.assert(response.status === 400);
    });
  });

  describe('GET /projects/{id}', () => {
    it('should return project by ID', async () => {
      const projectId = 'project-123';

      await provider.addInteraction({
        states: [{ description: providerStates.resourceExists('project', projectId) }],
        uponReceiving: 'a request for project by ID',
        withRequest: {
          method: 'GET',
          path: `/projects/${projectId}`,
          headers: withAuth(),
        },
        willRespondWith: standardResponse(testData.project),
      });

      const response = await fetch(`http://localhost:8080/projects/${projectId}`, {
        headers: { Authorization: 'Bearer test-token' },
      });

      console.assert(response.status === 200);
    });

    it('should return 404 for non-existent project', async () => {
      const projectId = 'non-existent';

      await provider.addInteraction({
        states: [{ description: providerStates.resourceNotFound('project', projectId) }],
        uponReceiving: 'a request for non-existent project',
        withRequest: {
          method: 'GET',
          path: `/projects/${projectId}`,
          headers: withAuth(),
        },
        willRespondWith: errorResponse('Project not found', 'NOT_FOUND', 404),
      });

      const response = await fetch(`http://localhost:8080/projects/${projectId}`, {
        headers: { Authorization: 'Bearer test-token' },
      });

      console.assert(response.status === 404);
    });
  });

  describe('PUT /projects/{id}', () => {
    it('should update project', async () => {
      const projectId = 'project-123';

      await provider.addInteraction({
        states: [{ description: providerStates.resourceExists('project', projectId) }],
        uponReceiving: 'a request to update project',
        withRequest: {
          method: 'PUT',
          path: `/projects/${projectId}`,
          headers: withAuth(),
          body: {
            name: 'Updated Project',
            description: 'Updated description',
          },
        },
        willRespondWith: standardResponse({
          ...testData.project,
          name: like('Updated Project'),
          description: like('Updated description'),
          updatedAt: iso8601DateTime(),
        }),
      });

      const response = await fetch(`http://localhost:8080/projects/${projectId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify({
          name: 'Updated Project',
          description: 'Updated description',
        }),
      });

      console.assert(response.status === 200);
    });
  });

  describe('DELETE /projects/{id}', () => {
    it('should delete project', async () => {
      const projectId = 'project-123';

      await provider.addInteraction({
        states: [{ description: providerStates.resourceExists('project', projectId) }],
        uponReceiving: 'a request to delete project',
        withRequest: {
          method: 'DELETE',
          path: `/projects/${projectId}`,
          headers: withAuth(),
        },
        willRespondWith: standardResponse(
          {
            success: like(true),
            message: like('Project deleted successfully'),
          },
          204
        ),
      });

      const response = await fetch(`http://localhost:8080/projects/${projectId}`, {
        method: 'DELETE',
        headers: { Authorization: 'Bearer test-token' },
      });

      console.assert(response.status === 204);
    });
  });

  describe('GET /projects/{id}/items', () => {
    it('should return project items', async () => {
      const projectId = 'project-123';

      await provider.addInteraction({
        states: [{ description: providerStates.projectHasItems }],
        uponReceiving: 'a request for project items',
        withRequest: {
          method: 'GET',
          path: `/projects/${projectId}/items`,
          query: {
            page: '1',
            pageSize: '20',
          },
          headers: withAuth(),
        },
        willRespondWith: paginatedResponse([testData.item]),
      });

      const response = await fetch(
        `http://localhost:8080/projects/${projectId}/items?page=1&pageSize=20`,
        {
          headers: { Authorization: 'Bearer test-token' },
        }
      );

      console.assert(response.status === 200);
    });
  });

  describe('GET /projects/{projectId}/versions/compare', () => {
    it('should compare project versions', async () => {
      const projectId = 'project-123';

      await provider.addInteraction({
        states: [{ description: 'project has multiple versions' }],
        uponReceiving: 'a request to compare versions',
        withRequest: {
          method: 'GET',
          path: `/api/v1/projects/${projectId}/versions/compare`,
          query: {
            from: 'v1.0.0',
            to: 'v1.1.0',
          },
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          projectId: uuid(projectId),
          fromVersion: like('v1.0.0'),
          toVersion: like('v1.1.0'),
          changes: eachLike({
            type: like('added'),
            itemId: uuid('item-123'),
            field: like('description'),
            oldValue: like('old'),
            newValue: like('new'),
          }),
          summary: {
            added: integer(5),
            modified: integer(3),
            deleted: integer(1),
          },
        }),
      });

      const response = await fetch(
        `http://localhost:8080/api/v1/projects/${projectId}/versions/compare?from=v1.0.0&to=v1.1.0`,
        {
          headers: { Authorization: 'Bearer test-token' },
        }
      );

      console.assert(response.status === 200);
    });
  });
});
