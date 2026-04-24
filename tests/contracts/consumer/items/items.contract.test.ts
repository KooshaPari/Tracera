/**
 * Items API Contract Tests
 *
 * Consumer: TraceRTM-Web
 * Provider: TraceRTM-API
 * Domain: Item Management
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

const provider = createPactProvider('TraceRTM-Web-Items');

describe('Items Contract Tests', () => {
  beforeAll(async () => {
    await setupPact(provider);
  });

  afterAll(async () => {
    await teardownPact(provider);
  });

  describe('GET /items', () => {
    it('should return list of items', async () => {
      await provider.addInteraction({
        states: [{ description: 'items exist' }],
        uponReceiving: 'a request for items list',
        withRequest: {
          method: 'GET',
          path: '/items',
          query: {
            page: '1',
            pageSize: '20',
          },
          headers: withAuth(),
        },
        willRespondWith: paginatedResponse([testData.item]),
      });

      const response = await fetch('http://localhost:8080/items?page=1&pageSize=20', {
        headers: { Authorization: 'Bearer test-token' },
      });

      console.assert(response.status === 200);
    });

    it('should filter items by type', async () => {
      await provider.addInteraction({
        states: [{ description: 'items of type requirement exist' }],
        uponReceiving: 'a request for items filtered by type',
        withRequest: {
          method: 'GET',
          path: '/items',
          query: {
            type: 'requirement',
            page: '1',
            pageSize: '20',
          },
          headers: withAuth(),
        },
        willRespondWith: paginatedResponse([
          {
            ...testData.item,
            type: like('requirement'),
          },
        ]),
      });

      const response = await fetch(
        'http://localhost:8080/items?type=requirement&page=1&pageSize=20',
        {
          headers: { Authorization: 'Bearer test-token' },
        }
      );

      console.assert(response.status === 200);
    });
  });

  describe('POST /items', () => {
    it('should create new item', async () => {
      await provider.addInteraction({
        states: [
          { description: providerStates.userAuthenticated },
          { description: providerStates.projectExists },
        ],
        uponReceiving: 'a request to create item',
        withRequest: {
          method: 'POST',
          path: '/items',
          headers: withAuth(),
          body: {
            projectId: 'project-123',
            type: 'requirement',
            title: 'New Requirement',
            description: 'Requirement description',
            status: 'draft',
          },
        },
        willRespondWith: standardResponse(
          {
            ...testData.item,
            title: like('New Requirement'),
          },
          201
        ),
      });

      const response = await fetch('http://localhost:8080/items', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify({
          projectId: 'project-123',
          type: 'requirement',
          title: 'New Requirement',
          description: 'Requirement description',
          status: 'draft',
        }),
      });

      console.assert(response.status === 201);
    });
  });

  describe('GET /items/{id}', () => {
    it('should return item by ID', async () => {
      const itemId = 'item-123';

      await provider.addInteraction({
        states: [{ description: providerStates.resourceExists('item', itemId) }],
        uponReceiving: 'a request for item by ID',
        withRequest: {
          method: 'GET',
          path: `/items/${itemId}`,
          headers: withAuth(),
        },
        willRespondWith: standardResponse(testData.item),
      });

      const response = await fetch(`http://localhost:8080/items/${itemId}`, {
        headers: { Authorization: 'Bearer test-token' },
      });

      console.assert(response.status === 200);
    });
  });

  describe('PUT /items/{id}', () => {
    it('should update item', async () => {
      const itemId = 'item-123';

      await provider.addInteraction({
        states: [{ description: providerStates.resourceExists('item', itemId) }],
        uponReceiving: 'a request to update item',
        withRequest: {
          method: 'PUT',
          path: `/items/${itemId}`,
          headers: withAuth(),
          body: {
            title: 'Updated Item',
            status: 'approved',
          },
        },
        willRespondWith: standardResponse({
          ...testData.item,
          title: like('Updated Item'),
          status: like('approved'),
          updatedAt: iso8601DateTime(),
        }),
      });

      const response = await fetch(`http://localhost:8080/items/${itemId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify({
          title: 'Updated Item',
          status: 'approved',
        }),
      });

      console.assert(response.status === 200);
    });
  });

  describe('DELETE /items/{id}', () => {
    it('should delete item', async () => {
      const itemId = 'item-123';

      await provider.addInteraction({
        states: [{ description: providerStates.resourceExists('item', itemId) }],
        uponReceiving: 'a request to delete item',
        withRequest: {
          method: 'DELETE',
          path: `/items/${itemId}`,
          headers: withAuth(),
        },
        willRespondWith: standardResponse(
          {
            success: like(true),
            message: like('Item deleted successfully'),
          },
          204
        ),
      });

      const response = await fetch(`http://localhost:8080/items/${itemId}`, {
        method: 'DELETE',
        headers: { Authorization: 'Bearer test-token' },
      });

      console.assert(response.status === 204);
    });
  });

  describe('GET /items/{id}/links', () => {
    it('should return item links', async () => {
      const itemId = 'item-123';

      await provider.addInteraction({
        states: [{ description: 'item has links' }],
        uponReceiving: 'a request for item links',
        withRequest: {
          method: 'GET',
          path: `/items/${itemId}/links`,
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          incoming: eachLike(testData.link),
          outgoing: eachLike(testData.link),
        }),
      });

      const response = await fetch(`http://localhost:8080/items/${itemId}/links`, {
        headers: { Authorization: 'Bearer test-token' },
      });

      console.assert(response.status === 200);
    });
  });

  describe('GET /items/{id}/pivot', () => {
    it('should return pivot analysis for item', async () => {
      const itemId = 'item-123';

      await provider.addInteraction({
        states: [{ description: providerStates.resourceExists('item', itemId) }],
        uponReceiving: 'a request for item pivot analysis',
        withRequest: {
          method: 'GET',
          path: `/items/${itemId}/pivot`,
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          itemId: uuid(itemId),
          perspectives: eachLike({
            type: like('technical'),
            items: eachLike(testData.item),
          }),
          relationships: eachLike({
            from: uuid('item-123'),
            to: uuid('item-456'),
            type: like('implements'),
          }),
        }),
      });

      const response = await fetch(`http://localhost:8080/items/${itemId}/pivot`, {
        headers: { Authorization: 'Bearer test-token' },
      });

      console.assert(response.status === 200);
    });
  });

  describe('GET /items/{id}/pivot-targets', () => {
    it('should return available pivot targets', async () => {
      const itemId = 'item-123';

      await provider.addInteraction({
        states: [{ description: providerStates.resourceExists('item', itemId) }],
        uponReceiving: 'a request for item pivot targets',
        withRequest: {
          method: 'GET',
          path: `/items/${itemId}/pivot-targets`,
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          targets: eachLike({
            type: like('feature'),
            count: integer(5),
            items: eachLike(testData.item),
          }),
        }),
      });

      const response = await fetch(`http://localhost:8080/items/${itemId}/pivot-targets`, {
        headers: { Authorization: 'Bearer test-token' },
      });

      console.assert(response.status === 200);
    });
  });
});
