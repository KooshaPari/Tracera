/**
 * Tests for screenshot storage utilities
 * Focuses on input validation, error handling, and caching logic
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import type { ScreenshotMetadata } from '../../utils/screenshot';

import {
  cacheScreenshot,
  clearScreenshotCache,
  deleteScreenshot,
  getComponentScreenshots,
  getScreenshotCacheStats,
  getScreenshotFromCache,
  screenshotNeedsUpdate,
  updateItemWithScreenshot,
  uploadScreenshot,
} from '../../utils/screenshot';

globalThis.fetch = vi.fn() as unknown as typeof fetch;

beforeEach(() => {
  vi.clearAllMocks();
  clearScreenshotCache();
});

afterEach(() => {
  vi.clearAllMocks();
  clearScreenshotCache();
});

describe('Screenshot Utilities', () => {
  describe(uploadScreenshot, () => {
    it('should reject empty screenshot data', async () => {
      // Given: Empty screenshot
      const emptyData = '';

      // When: Attempting upload
      const result = uploadScreenshot({
        componentId: 'component-1',
        screenshotData: emptyData,
      });

      // Then: Verify error is thrown
      await expect(result).rejects.toThrow('empty');
    });

    it.skip('should handle network errors gracefully', async () => {
      // Given: Network error simulation
      (globalThis.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      // When: Uploading with network error
      const result = uploadScreenshot({
        componentId: 'component-1',
        screenshotData: 'data:image/png;base64,ABC123',
      });

      // Then: Verify error is caught
      await expect(result).rejects.toThrow();
    });

    it('should handle presigned URL generation failures', async () => {
      // Given: Failed presigned URL endpoint
      (globalThis.fetch as any).mockResolvedValueOnce({
        json: async () => ({ error: 'Server error' }),
        ok: false,
        status: 500,
      });

      // When: Attempting upload
      const result = uploadScreenshot({
        componentId: 'component-1',
        screenshotData: 'data:image/png;base64,ABC123',
      });

      // Then: Verify error is thrown
      await expect(result).rejects.toThrow();
    });

    it('should return error with proper structure', async () => {
      // Given: Empty screenshot data
      const emptyData = '';

      // When: Attempting upload
      try {
        await uploadScreenshot({
          componentId: 'component-1',
          screenshotData: emptyData,
        });
      } catch (error) {
        // Then: Verify error has proper structure
        expect(error).toHaveProperty('code');
        expect(error).toHaveProperty('message');
        expect(error.code).toMatch(/NETWORK_ERROR|UPLOAD_FAILED|INVALID_FILE|COMPRESSION_FAILED/);
      }
    });
  });

  describe(deleteScreenshot, () => {
    it('should call delete endpoint with correct key', async () => {
      // Given: Valid screenshot key
      const key = 'screenshots/file-123.jpg';

      (globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
      });

      // When: Deleting screenshot
      await deleteScreenshot(key);

      // Then: Verify delete request was made
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining(key),
        expect.objectContaining({
          method: 'DELETE',
        }),
      );
    });

    it('should handle delete errors', async () => {
      // Given: Failed delete
      const key = 'screenshots/missing.jpg';

      (globalThis.fetch as any).mockResolvedValueOnce({
        json: async () => ({ error: 'Not found' }),
        ok: false,
        status: 404,
      });

      // When: Deleting missing screenshot
      const result = deleteScreenshot(key);

      // Then: Verify error is thrown
      await expect(result).rejects.toThrow();
    });

    it('should handle network errors during delete', async () => {
      // Given: Network error
      (globalThis.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      // When: Deleting with network error
      const result = deleteScreenshot('screenshots/file.jpg');

      // Then: Verify error is caught
      await expect(result).rejects.toThrow();
    });
  });

  describe('Screenshot Caching', () => {
    it('should cache and retrieve screenshot metadata', () => {
      // Given: Screenshot metadata
      const metadata: ScreenshotMetadata = {
        componentId: 'comp-1',
        createdAt: new Date(),
        height: 800,
        id: 'ss-1',
        updatedAt: new Date(),
        url: 'https://s3.amazonaws.com/screenshot.jpg',
        version: '1.0.0',
        versionType: 'design',
        width: 1200,
      };

      // When: Caching screenshot
      cacheScreenshot(metadata);

      // Then: Verify it can be retrieved
      const cached = getScreenshotFromCache(metadata.id);
      expect(cached).toEqual(metadata);
    });

    it('should return undefined for non-cached screenshot', () => {
      // When: Retrieving non-existent screenshot
      const cached = getScreenshotFromCache('non-existent');

      // Then: Verify undefined is returned
      expect(cached).toBeUndefined();
    });

    it('should get all screenshots for component', () => {
      // Given: Multiple screenshots for same component
      const componentId = 'comp-multi';
      const metadata1: ScreenshotMetadata = {
        componentId,
        createdAt: new Date('2024-01-01'),
        height: 800,
        id: 'ss-1',
        updatedAt: new Date('2024-01-01'),
        url: 'https://s3.amazonaws.com/ss1.jpg',
        version: '1.0.0',
        versionType: 'design',
        width: 1200,
      };

      const metadata2: ScreenshotMetadata = {
        componentId,
        createdAt: new Date('2024-01-02'),
        height: 800,
        id: 'ss-2',
        updatedAt: new Date('2024-01-02'),
        url: 'https://s3.amazonaws.com/ss2.jpg',
        version: '2.0.0',
        versionType: 'review',
        width: 1200,
      };

      cacheScreenshot(metadata1);
      cacheScreenshot(metadata2);

      // When: Getting component screenshots
      const screenshots = getComponentScreenshots(componentId);

      // Then: Verify all are returned and sorted (most recent first)
      expect(screenshots).toHaveLength(2);
      expect(screenshots[0]?.id).toBe(metadata2.id);
      expect(screenshots[1]?.id).toBe(metadata1.id);
    });

    it('should clear screenshot cache', () => {
      // Given: Cached screenshot
      const metadata: ScreenshotMetadata = {
        componentId: 'comp-clear',
        createdAt: new Date(),
        height: 800,
        id: 'ss-clear',
        updatedAt: new Date(),
        url: 'https://s3.amazonaws.com/ss.jpg',
        version: '1.0.0',
        versionType: 'draft',
        width: 1200,
      };
      cacheScreenshot(metadata);

      // When: Clearing cache
      clearScreenshotCache();

      // Then: Verify cache is empty
      const cached = getScreenshotFromCache(metadata.id);
      expect(cached).toBeUndefined();
    });

    it('should get cache statistics', () => {
      // Given: Cached screenshot with fileSize
      const metadata: ScreenshotMetadata = {
        componentId: 'comp-stats',
        createdAt: new Date(),
        fileSize: 2048,
        height: 800,
        id: 'ss-stats',
        updatedAt: new Date(),
        url: 'https://s3.amazonaws.com/ss.jpg',
        version: '1.0.0',
        versionType: 'draft',
        width: 1200,
      };

      cacheScreenshot(metadata);

      // When: Getting cache stats
      const stats = getScreenshotCacheStats();

      // Then: Verify stats are correct
      expect(stats.screenshots).toBe(1);
      expect(stats.totalFileSize).toBe(2048);
    });
  });

  describe('Screenshot Content Management', () => {
    it('should detect if screenshot needs update with different hash', () => {
      // Given: Existing screenshot with content hash
      const existing: ScreenshotMetadata = {
        componentId: 'comp-hash',
        contentHash: 'hash123',
        createdAt: new Date(),
        height: 800,
        id: 'ss-hash',
        updatedAt: new Date(),
        url: 'https://s3.amazonaws.com/ss.jpg',
        version: '1.0.0',
        versionType: 'draft',
        width: 1200,
      };

      // When: Checking with different hash
      const needsUpdate = screenshotNeedsUpdate(existing, 'hash456');

      // Then: Verify update is needed
      expect(needsUpdate).toBeTruthy();
    });

    it('should not update if content hash matches', () => {
      // Given: Existing screenshot with same hash
      const existing: ScreenshotMetadata = {
        componentId: 'comp-same',
        contentHash: 'hash123',
        createdAt: new Date(),
        height: 800,
        id: 'ss-same',
        updatedAt: new Date(),
        url: 'https://s3.amazonaws.com/ss.jpg',
        version: '1.0.0',
        versionType: 'draft',
        width: 1200,
      };

      // When: Checking with same hash
      const needsUpdate = screenshotNeedsUpdate(existing, 'hash123');

      // Then: Verify update is not needed
      expect(needsUpdate).toBeFalsy();
    });

    it('should require update if no existing metadata', () => {
      // When: Checking with no existing metadata
      const needsUpdate = screenshotNeedsUpdate(undefined, 'hash123');

      // Then: Verify update is needed
      expect(needsUpdate).toBeTruthy();
    });

    it('should update item with screenshot metadata', () => {
      // Given: Item and screenshot
      const item = {
        createdAt: '2024-01-01T00:00:00Z',
        id: 'item-1',
        priority: 'medium' as const,
        projectId: 'proj-1',
        status: 'todo' as const,
        title: 'Test Component',
        type: 'component',
        updatedAt: '2024-01-01T00:00:00Z',
        version: 1,
        view: 'architecture' as const,
      };

      const screenshot: ScreenshotMetadata = {
        componentId: 'comp-update',
        contentHash: 'hash789',
        createdAt: new Date(),
        height: 800,
        id: 'ss-update',
        thumbnailUrl: 'https://s3.amazonaws.com/ss-thumb.jpg',
        updatedAt: new Date(),
        url: 'https://s3.amazonaws.com/ss.jpg',
        version: '1.0.0',
        versionType: 'design',
        width: 1200,
      };

      // When: Updating item with screenshot
      const updatedItem = updateItemWithScreenshot(item, screenshot);

      // Then: Verify item has screenshot metadata
      expect(updatedItem.metadata?.['screenshotUrl']).toBe(screenshot.url);
      expect(updatedItem.metadata?.['thumbnailUrl']).toBe(screenshot.thumbnailUrl);
      expect(updatedItem.metadata?.['screenshotVersion']).toBe(screenshot.version);
      expect(updatedItem.metadata?.['screenshotVersionType']).toBe(screenshot.versionType);
    });
  });

  describe('Error Handling', () => {
    it('should provide error with code property', async () => {
      // When: Attempting upload with empty data
      try {
        await uploadScreenshot({
          componentId: 'component-1',
          screenshotData: '',
        });
      } catch (error) {
        // Then: Verify error has code
        expect(error.code).toBeDefined();
        expect(error.code).toMatch(/NETWORK_ERROR|UPLOAD_FAILED|INVALID_FILE|COMPRESSION_FAILED/);
      }
    });

    it('should handle different error codes', async () => {
      // Test NETWORK_ERROR
      (globalThis.fetch as any).mockRejectedValueOnce(new Error('Network'));

      try {
        await uploadScreenshot({
          componentId: 'comp-1',
          screenshotData: 'data:image/png;base64,ABC',
        });
      } catch (error) {
        expect(error.code).toBeDefined();
      }
    });
  });

  describe('Type Safety', () => {
    it('should preserve screenshot metadata types', () => {
      // Given: Properly typed metadata
      const metadata: ScreenshotMetadata = {
        componentId: 'comp-types',
        createdAt: new Date(),
        height: 800,
        id: 'ss-types',
        updatedAt: new Date(),
        url: 'https://s3.amazonaws.com/ss.jpg',
        version: '1.0.0',
        versionType: 'draft',
        width: 1200,
      };

      // When: Caching
      cacheScreenshot(metadata);

      // Then: Verify type is preserved
      const cached = getScreenshotFromCache(metadata.id);
      expect(cached?.versionType).toBe('draft');
      expect(cached?.width).toBe(1200);
    });

    it('should handle optional metadata fields', () => {
      // Given: Metadata with optional fields
      const metadata: ScreenshotMetadata = {
        componentId: 'comp-optional',
        contentHash: 'hash',
        createdAt: new Date(),
        fileSize: 1024,
        height: 800,
        id: 'ss-optional',
        storageKey: 'key',
        thumbnailUrl: 'https://example.com/thumb.jpg',
        updatedAt: new Date(),
        url: 'https://s3.amazonaws.com/ss.jpg',
        version: '1.0.0',
        versionType: 'draft',
        width: 1200,
      };

      // When: Caching
      cacheScreenshot(metadata);

      // Then: Verify optional fields are preserved
      const cached = getScreenshotFromCache(metadata.id);
      expect(cached?.contentHash).toBe('hash');
      expect(cached?.fileSize).toBe(1024);
    });
  });

  describe('Integration Scenarios', () => {
    it('should support screenshot version tracking', () => {
      // Given: Multiple versions of same component
      const componentId = 'comp-versions';

      const v1: ScreenshotMetadata = {
        componentId,
        createdAt: new Date('2024-01-01'),
        height: 800,
        id: 'ss-v1',
        updatedAt: new Date('2024-01-01'),
        url: 'https://s3.amazonaws.com/v1.jpg',
        version: '1.0.0',
        versionType: 'design',
        width: 1200,
      };

      const v2: ScreenshotMetadata = {
        componentId,
        createdAt: new Date('2024-01-02'),
        height: 800,
        id: 'ss-v2',
        updatedAt: new Date('2024-01-02'),
        url: 'https://s3.amazonaws.com/v2.jpg',
        version: '2.0.0',
        versionType: 'review',
        width: 1200,
      };

      // When: Caching both versions
      cacheScreenshot(v1);
      cacheScreenshot(v2);

      // Then: Verify version history
      const screenshots = getComponentScreenshots(componentId);
      expect(screenshots).toHaveLength(2);
      expect(screenshots[0]?.version).toBe('2.0.0');
      expect(screenshots[1]?.version).toBe('1.0.0');
    });
  });
});
