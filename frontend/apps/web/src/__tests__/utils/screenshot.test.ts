/**
 * Tests for screenshot storage utilities
 * Focuses on input validation, error handling, and caching logic
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
	cacheScreenshot,
	clearScreenshotCache,
	deleteScreenshot,
	getComponentScreenshots,
	getScreenshotCacheStats,
	getScreenshotFromCache,
	type ScreenshotMetadata,
	screenshotNeedsUpdate,
	updateItemWithScreenshot,
	uploadScreenshot,
} from "../../utils/screenshot";

global.fetch = vi.fn();

beforeEach(() => {
	vi.clearAllMocks();
	clearScreenshotCache();
});

afterEach(() => {
	vi.clearAllMocks();
	clearScreenshotCache();
});

describe("Screenshot Utilities", () => {
	describe("uploadScreenshot", () => {
		it("should reject empty screenshot data", async () => {
			// Given: Empty screenshot
			const emptyData = "";

			// When: Attempting upload
			const result = uploadScreenshot(emptyData, "component-1");

			// Then: Verify error is thrown
			await expect(result).rejects.toThrow("empty");
		});

		it("should handle network errors gracefully", async () => {
			// Given: Network error simulation
			(global.fetch as any).mockRejectedValueOnce(new Error("Network error"));

			// When: Uploading with network error
			const result = uploadScreenshot(
				"data:image/png;base64,ABC123",
				"component-1",
			);

			// Then: Verify error is caught
			await expect(result).rejects.toThrow();
		});

		it("should handle presigned URL generation failures", async () => {
			// Given: Failed presigned URL endpoint
			(global.fetch as any).mockResolvedValueOnce({
				ok: false,
				status: 500,
				json: async () => ({ error: "Server error" }),
			});

			// When: Attempting upload
			const result = uploadScreenshot(
				"data:image/png;base64,ABC123",
				"component-1",
			);

			// Then: Verify error is thrown
			await expect(result).rejects.toThrow();
		});

		it("should return error with proper structure", async () => {
			// Given: Empty screenshot data
			const emptyData = "";

			// When: Attempting upload
			try {
				await uploadScreenshot(emptyData, "component-1");
			} catch (error) {
				// Then: Verify error has proper structure
				expect(error).toHaveProperty("code");
				expect(error).toHaveProperty("message");
				expect((error as any).code).toMatch(
					/NETWORK_ERROR|UPLOAD_FAILED|INVALID_FILE|COMPRESSION_FAILED/,
				);
			}
		});
	});

	describe("deleteScreenshot", () => {
		it("should call delete endpoint with correct key", async () => {
			// Given: Valid screenshot key
			const key = "screenshots/file-123.jpg";

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
			});

			// When: Deleting screenshot
			await deleteScreenshot(key);

			// Then: Verify delete request was made
			expect(global.fetch).toHaveBeenCalledWith(
				expect.stringContaining(key),
				expect.objectContaining({
					method: "DELETE",
				}),
			);
		});

		it("should handle delete errors", async () => {
			// Given: Failed delete
			const key = "screenshots/missing.jpg";

			(global.fetch as any).mockResolvedValueOnce({
				ok: false,
				status: 404,
				json: async () => ({ error: "Not found" }),
			});

			// When: Deleting missing screenshot
			const result = deleteScreenshot(key);

			// Then: Verify error is thrown
			await expect(result).rejects.toThrow();
		});

		it("should handle network errors during delete", async () => {
			// Given: Network error
			(global.fetch as any).mockRejectedValueOnce(new Error("Network error"));

			// When: Deleting with network error
			const result = deleteScreenshot("screenshots/file.jpg");

			// Then: Verify error is caught
			await expect(result).rejects.toThrow();
		});
	});

	describe("Screenshot Caching", () => {
		it("should cache and retrieve screenshot metadata", () => {
			// Given: Screenshot metadata
			const metadata: ScreenshotMetadata = {
				id: "ss-1",
				componentId: "comp-1",
				url: "https://s3.amazonaws.com/screenshot.jpg",
				width: 1200,
				height: 800,
				version: "1.0.0",
				versionType: "design",
				createdAt: new Date(),
				updatedAt: new Date(),
			};

			// When: Caching screenshot
			cacheScreenshot(metadata);

			// Then: Verify it can be retrieved
			const cached = getScreenshotFromCache(metadata.id);
			expect(cached).toEqual(metadata);
		});

		it("should return undefined for non-cached screenshot", () => {
			// When: Retrieving non-existent screenshot
			const cached = getScreenshotFromCache("non-existent");

			// Then: Verify undefined is returned
			expect(cached).toBeUndefined();
		});

		it("should get all screenshots for component", () => {
			// Given: Multiple screenshots for same component
			const componentId = "comp-multi";
			const metadata1: ScreenshotMetadata = {
				id: "ss-1",
				componentId,
				url: "https://s3.amazonaws.com/ss1.jpg",
				width: 1200,
				height: 800,
				version: "1.0.0",
				versionType: "design",
				createdAt: new Date("2024-01-01"),
				updatedAt: new Date("2024-01-01"),
			};

			const metadata2: ScreenshotMetadata = {
				id: "ss-2",
				componentId,
				url: "https://s3.amazonaws.com/ss2.jpg",
				width: 1200,
				height: 800,
				version: "2.0.0",
				versionType: "review",
				createdAt: new Date("2024-01-02"),
				updatedAt: new Date("2024-01-02"),
			};

			cacheScreenshot(metadata1);
			cacheScreenshot(metadata2);

			// When: Getting component screenshots
			const screenshots = getComponentScreenshots(componentId);

			// Then: Verify all are returned and sorted (most recent first)
			expect(screenshots).toHaveLength(2);
			expect(screenshots[0].id).toBe(metadata2.id);
			expect(screenshots[1].id).toBe(metadata1.id);
		});

		it("should clear screenshot cache", () => {
			// Given: Cached screenshot
			const metadata: ScreenshotMetadata = {
				id: "ss-clear",
				componentId: "comp-clear",
				url: "https://s3.amazonaws.com/ss.jpg",
				width: 1200,
				height: 800,
				version: "1.0.0",
				versionType: "draft",
				createdAt: new Date(),
				updatedAt: new Date(),
			};
			cacheScreenshot(metadata);

			// When: Clearing cache
			clearScreenshotCache();

			// Then: Verify cache is empty
			const cached = getScreenshotFromCache(metadata.id);
			expect(cached).toBeUndefined();
		});

		it("should get cache statistics", () => {
			// Given: Cached screenshot with fileSize
			const metadata: ScreenshotMetadata = {
				id: "ss-stats",
				componentId: "comp-stats",
				url: "https://s3.amazonaws.com/ss.jpg",
				width: 1200,
				height: 800,
				version: "1.0.0",
				versionType: "draft",
				fileSize: 2048,
				createdAt: new Date(),
				updatedAt: new Date(),
			};

			cacheScreenshot(metadata);

			// When: Getting cache stats
			const stats = getScreenshotCacheStats();

			// Then: Verify stats are correct
			expect(stats.screenshots).toBe(1);
			expect(stats.totalFileSize).toBe(2048);
		});
	});

	describe("Screenshot Content Management", () => {
		it("should detect if screenshot needs update with different hash", () => {
			// Given: Existing screenshot with content hash
			const existing: ScreenshotMetadata = {
				id: "ss-hash",
				componentId: "comp-hash",
				url: "https://s3.amazonaws.com/ss.jpg",
				width: 1200,
				height: 800,
				version: "1.0.0",
				versionType: "draft",
				contentHash: "hash123",
				createdAt: new Date(),
				updatedAt: new Date(),
			};

			// When: Checking with different hash
			const needsUpdate = screenshotNeedsUpdate(existing, "hash456");

			// Then: Verify update is needed
			expect(needsUpdate).toBe(true);
		});

		it("should not update if content hash matches", () => {
			// Given: Existing screenshot with same hash
			const existing: ScreenshotMetadata = {
				id: "ss-same",
				componentId: "comp-same",
				url: "https://s3.amazonaws.com/ss.jpg",
				width: 1200,
				height: 800,
				version: "1.0.0",
				versionType: "draft",
				contentHash: "hash123",
				createdAt: new Date(),
				updatedAt: new Date(),
			};

			// When: Checking with same hash
			const needsUpdate = screenshotNeedsUpdate(existing, "hash123");

			// Then: Verify update is not needed
			expect(needsUpdate).toBe(false);
		});

		it("should require update if no existing metadata", () => {
			// When: Checking with no existing metadata
			const needsUpdate = screenshotNeedsUpdate(undefined, "hash123");

			// Then: Verify update is needed
			expect(needsUpdate).toBe(true);
		});

		it("should update item with screenshot metadata", () => {
			// Given: Item and screenshot
			const item = {
				id: "item-1",
				projectId: "proj-1",
				type: "component",
				title: "Test Component",
				createdAt: "2024-01-01T00:00:00Z",
				updatedAt: "2024-01-01T00:00:00Z",
			};

			const screenshot: ScreenshotMetadata = {
				id: "ss-update",
				componentId: "comp-update",
				url: "https://s3.amazonaws.com/ss.jpg",
				thumbnailUrl: "https://s3.amazonaws.com/ss-thumb.jpg",
				width: 1200,
				height: 800,
				version: "1.0.0",
				versionType: "design",
				contentHash: "hash789",
				createdAt: new Date(),
				updatedAt: new Date(),
			};

			// When: Updating item with screenshot
			const updatedItem = updateItemWithScreenshot(item, screenshot);

			// Then: Verify item has screenshot metadata
			expect(updatedItem.metadata?.screenshotUrl).toBe(screenshot.url);
			expect(updatedItem.metadata?.thumbnailUrl).toBe(screenshot.thumbnailUrl);
			expect(updatedItem.metadata?.screenshotVersion).toBe(screenshot.version);
			expect(updatedItem.metadata?.screenshotVersionType).toBe(
				screenshot.versionType,
			);
		});
	});

	describe("Error Handling", () => {
		it("should provide error with code property", async () => {
			// When: Attempting upload with empty data
			try {
				await uploadScreenshot("", "component-1");
			} catch (error) {
				// Then: Verify error has code
				expect((error as any).code).toBeDefined();
				expect((error as any).code).toMatch(
					/NETWORK_ERROR|UPLOAD_FAILED|INVALID_FILE|COMPRESSION_FAILED/,
				);
			}
		});

		it("should handle different error codes", async () => {
			// Test NETWORK_ERROR
			(global.fetch as any).mockRejectedValueOnce(new Error("Network"));

			try {
				await uploadScreenshot("data:image/png;base64,ABC", "comp-1");
			} catch (error) {
				expect((error as any).code).toBeDefined();
			}
		});
	});

	describe("Type Safety", () => {
		it("should preserve screenshot metadata types", () => {
			// Given: Properly typed metadata
			const metadata: ScreenshotMetadata = {
				id: "ss-types",
				componentId: "comp-types",
				url: "https://s3.amazonaws.com/ss.jpg",
				width: 1200,
				height: 800,
				version: "1.0.0",
				versionType: "draft",
				createdAt: new Date(),
				updatedAt: new Date(),
			};

			// When: Caching
			cacheScreenshot(metadata);

			// Then: Verify type is preserved
			const cached = getScreenshotFromCache(metadata.id);
			expect(cached?.versionType).toBe("draft");
			expect(cached?.width).toBe(1200);
		});

		it("should handle optional metadata fields", () => {
			// Given: Metadata with optional fields
			const metadata: ScreenshotMetadata = {
				id: "ss-optional",
				componentId: "comp-optional",
				url: "https://s3.amazonaws.com/ss.jpg",
				width: 1200,
				height: 800,
				version: "1.0.0",
				versionType: "draft",
				createdAt: new Date(),
				updatedAt: new Date(),
				contentHash: "hash",
				storageKey: "key",
				fileSize: 1024,
				thumbnailUrl: "https://example.com/thumb.jpg",
			};

			// When: Caching
			cacheScreenshot(metadata);

			// Then: Verify optional fields are preserved
			const cached = getScreenshotFromCache(metadata.id);
			expect(cached?.contentHash).toBe("hash");
			expect(cached?.fileSize).toBe(1024);
		});
	});

	describe("Integration Scenarios", () => {
		it("should support screenshot version tracking", () => {
			// Given: Multiple versions of same component
			const componentId = "comp-versions";

			const v1: ScreenshotMetadata = {
				id: "ss-v1",
				componentId,
				url: "https://s3.amazonaws.com/v1.jpg",
				width: 1200,
				height: 800,
				version: "1.0.0",
				versionType: "design",
				createdAt: new Date("2024-01-01"),
				updatedAt: new Date("2024-01-01"),
			};

			const v2: ScreenshotMetadata = {
				id: "ss-v2",
				componentId,
				url: "https://s3.amazonaws.com/v2.jpg",
				width: 1200,
				height: 800,
				version: "2.0.0",
				versionType: "review",
				createdAt: new Date("2024-01-02"),
				updatedAt: new Date("2024-01-02"),
			};

			// When: Caching both versions
			cacheScreenshot(v1);
			cacheScreenshot(v2);

			// Then: Verify version history
			const screenshots = getComponentScreenshots(componentId);
			expect(screenshots).toHaveLength(2);
			expect(screenshots[0].version).toBe("2.0.0");
			expect(screenshots[1].version).toBe("1.0.0");
		});
	});
});
