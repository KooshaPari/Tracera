/**
 * Tests for Links API
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { createLink, deleteLink, fetchLink, fetchLinks, updateLink } from '@/api/links';

// Mock endpoints
vi.mock('@/api/endpoints', () => ({
  linksApi: {
    create: vi.fn(),
    delete: vi.fn(),
    get: vi.fn(),
    list: vi.fn(),
    update: vi.fn(),
  },
}));

import { linksApi } from '@/api/endpoints';

import { mockLinks } from '../mocks/data';

describe('Links API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchLinks, () => {
    it('should fetch links', async () => {
      vi.mocked(linksApi.list).mockResolvedValue(mockLinks);

      const result = await fetchLinks();
      expect(result).toEqual(mockLinks);
      expect(linksApi.list).toHaveBeenCalledWith();
    });

    it('should fetch links with params', async () => {
      vi.mocked(linksApi.list).mockResolvedValue(mockLinks);

      const result = await fetchLinks({ limit: 10, offset: 0 });
      expect(result).toEqual(mockLinks);
      expect(linksApi.list).toHaveBeenCalledWith({ limit: 10, offset: 0 });
    });
  });

  describe(fetchLink, () => {
    it('should fetch a single link', async () => {
      vi.mocked(linksApi.get).mockResolvedValue(mockLinks[0]);

      const result = await fetchLink('link-1');
      expect(result).toEqual(mockLinks[0]);
      expect(linksApi.get).toHaveBeenCalledWith('link-1');
    });
  });

  describe(createLink, () => {
    it('should create a link', async () => {
      const newLink = {
        source_id: 'item-1',
        target_id: 'item-2',
        type: 'implements' as const,
      };
      const created = { ...mockLinks[0], ...newLink, id: 'new-link' };
      vi.mocked(linksApi.create).mockResolvedValue(created);

      const result = await createLink(newLink);
      expect(result).toEqual(created);
      expect(linksApi.create).toHaveBeenCalledWith(newLink);
    });
  });

  describe(updateLink, () => {
    it('should update a link', async () => {
      const updates = { type: 'tests' as const };
      const updated = { ...mockLinks[0], ...updates };
      vi.mocked(linksApi.update).mockResolvedValue(updated);

      const result = await updateLink('link-1', updates);
      expect(result).toEqual(updated);
      expect(linksApi.update).toHaveBeenCalledWith('link-1', updates);
    });
  });

  describe(deleteLink, () => {
    it('should delete a link', async () => {
      vi.mocked(linksApi.delete).mockResolvedValue();

      await expect(deleteLink('link-1')).resolves.toBeUndefined();
      expect(linksApi.delete).toHaveBeenCalledWith('link-1');
    });
  });
});
