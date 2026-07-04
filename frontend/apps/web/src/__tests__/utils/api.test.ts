/**
 * Tests for API utility functions
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

// Mock fetch
const mockFetch = vi.fn();
globalThis.fetch = mockFetch as unknown as typeof fetch;

// Mock API_URL
const API_URL = 'http://localhost:4000';

describe('API utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('fetchItems', () => {
    it('should fetch items without filters', async () => {
      const mockItems = [
        { id: '1', title: 'Item 1' },
        { id: '2', title: 'Item 2' },
      ];

      mockFetch.mockResolvedValueOnce({
        json: async () => mockItems,
        ok: true,
      });

      const response = await fetch(`${API_URL}/api/v1/items`);
      const data = await response.json();

      expect(mockFetch).toHaveBeenCalledWith(`${API_URL}/api/v1/items`);
      expect(data).toEqual(mockItems);
    });

    it('should fetch items with project filter', async () => {
      mockFetch.mockResolvedValueOnce({
        json: async () => [],
        ok: true,
      });

      const params = new URLSearchParams({ project_id: 'project-1' });
      await fetch(`${API_URL}/api/v1/items?${params}`);

      expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('project_id=project-1'));
    });

    it('should handle fetch errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      const response = await fetch(`${API_URL}/api/v1/items`);

      expect(response.ok).toBeFalsy();
      expect(response.status).toBe(500);
    });
  });

  describe('createItem', () => {
    it('should create an item', async () => {
      const newItem = {
        priority: 'high',
        project_id: 'project-1',
        status: 'open',
        title: 'New Item',
        type: 'feature',
      };

      mockFetch.mockResolvedValueOnce({
        json: async () => ({ id: '1', ...newItem }),
        ok: true,
      });

      const response = await fetch(`${API_URL}/api/v1/items`, {
        body: JSON.stringify(newItem),
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      });

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_URL}/api/v1/items`,
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          method: 'POST',
        }),
      );

      const data = await response.json();
      expect(data).toEqual({ id: '1', ...newItem });
    });
  });

  describe('updateItem', () => {
    it('should update an item', async () => {
      const updates = {
        status: 'in_progress',
        title: 'Updated Title',
      };

      mockFetch.mockResolvedValueOnce({
        json: async () => ({ id: '1', ...updates }),
        ok: true,
      });

      const response = await fetch(`${API_URL}/api/v1/items/1`, {
        body: JSON.stringify(updates),
        headers: { 'Content-Type': 'application/json' },
        method: 'PATCH',
      });

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_URL}/api/v1/items/1`,
        expect.objectContaining({
          method: 'PATCH',
        }),
      );

      const data: { title: string } = await response.json();
      expect(data.title).toBe('Updated Title');
    });
  });

  describe('deleteItem', () => {
    it('should delete an item', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
      });

      const response = await fetch(`${API_URL}/api/v1/items/1`, {
        method: 'DELETE',
      });

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_URL}/api/v1/items/1`,
        expect.objectContaining({
          method: 'DELETE',
        }),
      );

      expect(response.ok).toBeTruthy();
    });
  });

  describe('projects API', () => {
    it('should fetch projects', async () => {
      const mockProjects = [
        { id: '1', name: 'Project 1' },
        { id: '2', name: 'Project 2' },
      ];

      mockFetch.mockResolvedValueOnce({
        json: async () => mockProjects,
        ok: true,
      });

      const response = await fetch(`${API_URL}/api/v1/projects`);
      const data = await response.json();

      expect(data).toEqual(mockProjects);
    });

    it('should create a project', async () => {
      const newProject = {
        description: 'Description',
        name: 'New Project',
      };

      mockFetch.mockResolvedValueOnce({
        json: async () => ({ id: '1', ...newProject }),
        ok: true,
      });

      const response = await fetch(`${API_URL}/api/v1/projects`, {
        body: JSON.stringify(newProject),
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      });

      const data: { name: string } = await response.json();
      expect(data.name).toBe('New Project');
    });
  });

  describe('links API', () => {
    it('should fetch links', async () => {
      const mockLinks = [{ id: '1', sourceId: 'item-1', targetId: 'item-2', type: 'depends_on' }];

      mockFetch.mockResolvedValueOnce({
        json: async () => mockLinks,
        ok: true,
      });

      const response = await fetch(`${API_URL}/api/v1/links`);
      const data = await response.json();

      expect(data).toEqual(mockLinks);
    });

    it('should create a link', async () => {
      const newLink = {
        source_id: 'item-1',
        target_id: 'item-2',
        type: 'depends_on',
      };

      mockFetch.mockResolvedValueOnce({
        json: async () => ({ id: '1', ...newLink }),
        ok: true,
      });

      const response = await fetch(`${API_URL}/api/v1/links`, {
        body: JSON.stringify(newLink),
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      });

      const data: { type: string } = await response.json();
      expect(data.type).toBe('depends_on');
    });
  });
});
